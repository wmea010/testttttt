# ============================================================
#  PICO W – RFID Scanner met LCD1602 Scherm + RESET KNOP
# gemaakt door Amin Aohammadi
# ============================================================

from mfrc522 import MFRC522
from machine import Pin, I2C
import network, rp2, time
from pico_i2c_lcd import I2cLcd

try:
    import upgsql
except ImportError:
    print("FOUT: upgsql.py ontbreekt op je Pico W!")

# -------------------- WIFI CONFIG --------------------
WIFI_SSID     = "iotroam"
WIFI_PASSWORD = "Welkom!F4EA"

# -------------------- DATABASE CONFIG --------------------
DB_HOST     = "4.211.203.204"
DB_PORT     = 5432
DB_NAME     = "steamdatabase"
DB_USER     = "amin"
DB_PASSWORD = "amin123"

# -------------------- HARDWARE SETUP (LCD & RFID) --------------------
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=400000)

devices = i2c.scan()
if len(devices) == 0:
    print("Geen I2C apparaten gevonden! Controleer je draden.")
    lcd_adres = 0x27
else:
    lcd_adres = devices[0]
    print("LCD gevonden op I2C adres:", hex(lcd_adres))

lcd = I2cLcd(i2c, lcd_adres, 2, 16)
lcd.clear()
lcd.putstr("Systeem start op..")

reader = MFRC522(sck=2, mosi=3, miso=4, rst=0, cs=5)

led1 = Pin(15, Pin.OUT)   # wassim
led2 = Pin(14, Pin.OUT)   # amin
led3 = Pin(13, Pin.OUT)   # ayoub

led1.off()
led2.off()
led3.off()

# -------------------- RESET KNOP (GP16) --------------------
reset_knop   = Pin(16, Pin.IN, Pin.PULL_UP)
knop_gedrukt = False   # vlag die de interrupt zet

def knop_handler(pin):
    global knop_gedrukt
    knop_gedrukt = True  # interrupt zet alleen een vlaggetje

# Interrupt: vuurt af bij indrukken (FALLING = van HIGH naar LOW)
reset_knop.irq(trigger=Pin.IRQ_FALLING, handler=knop_handler)

# -------------------- KAARTEN --------------------
KAARTEN = {
    "122-223-129-129":     ("wassim", led1),
    "154-80-199-0":        ("amin",   led2),
    "5-134-57-4-58-226-0": ("ayoub",  led3),
}

# -------------------- WIFI VERBINDING --------------------
def connect_wifi():
    rp2.country('NL')
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.config(pm=0xa11140)

    if not wlan.isconnected():
        print("Verbinden met " + WIFI_SSID + "...")
        lcd.clear()
        lcd.putstr("WiFi Verbinden..")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)

        timeout = 15
        while not wlan.isconnected() and timeout > 0:
            time.sleep(1)
            timeout -= 1
            print("Wachten op WiFi...")

    if wlan.isconnected():
        print("WiFi verbonden!")
        print("IP-adres:", wlan.ifconfig()[0])
        lcd.clear()
        lcd.putstr("WiFi Verbonden!\nScan uw kaart...")
        return True
    else:
        print("WiFi verbinding mislukt!")
        lcd.clear()
        lcd.putstr("WiFi Fout!")
        return False

# -------------------- DATABASE TOGGLE --------------------
def toggle_user(username):
    try:
        conn = upgsql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        cursor.execute(
            "SELECT can_login FROM users WHERE username = %s;",
            (username,)
        )
        result = cursor.fetchone()

        if result is None:
            print("Gebruiker niet gevonden: " + username)
            cursor.close()
            conn.close()
            return None

        huidige_status = result[0]
        nieuwe_status  = not huidige_status

        if nieuwe_status:
            cursor.execute(
                """UPDATE users
                   SET can_login    = TRUE,
                       online_since = NOW(),
                       last_seen    = NOW()
                   WHERE username = %s;""",
                (username,)
            )
            print(username + " --> ONLINE")
        else:
            cursor.execute(
                """UPDATE users
                   SET can_login = FALSE,
                       last_seen  = NOW()
                   WHERE username = %s;""",
                (username,)
            )
            print(username + " --> OFFLINE")

        conn.commit()
        cursor.close()
        conn.close()
        return nieuwe_status

    except Exception as e:
        print("Database fout:", e)
        return None

# -------------------- IEDEREEN OFFLINE --------------------
def zet_iedereen_offline():
    lcd.clear()
    lcd.putstr("Bezig...")

    succes = True
    try:
        conn = upgsql.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Alle users in één query offline zetten
        cursor.execute(
            "UPDATE users SET can_login = FALSE, last_seen = NOW() WHERE can_login = TRUE;"
        )

        conn.commit()
        cursor.close()
        conn.close()
        print("Iedereen is OFFLINE gezet.")

    except Exception as e:
        print("Database fout bij reset:", e)
        succes = False

    # Alle LEDs uit
    led1.off()
    led2.off()
    led3.off()

    lcd.clear()
    if succes:
        lcd.putstr("Iedereen\nis OFFLINE")
    else:
        lcd.putstr("Reset mislukt!\nDB Fout")

    time.sleep(3)
    lcd.clear()
    lcd.putstr("Scan uw kaart...")

# -------------------- START --------------------
if not connect_wifi():
    print("Gestopt: geen WiFi verbinding.")
    raise SystemExit

print("RFID scanner klaar. Houd een kaart voor de lezer...")

# -------------------- LOOP --------------------
while True:

    # --- Knop check via interrupt vlag ---
    if knop_gedrukt:
        time.sleep(0.05)               # debounce
        if reset_knop.value() == 0:    # controleer of knop echt ingedrukt is
            zet_iedereen_offline()
        knop_gedrukt = False           # vlag resetten, klaar om weer te scannen

    # --- RFID check ---
    reader.init()
    (stat, tag_type) = reader.request(reader.REQIDL)

    if stat == reader.OK:
        (stat, uid) = reader.SelectTagSN()

        if stat == reader.OK:
            kaart_id = "-".join([str(x) for x in uid])
            print("Scan:", kaart_id)

            if kaart_id in KAARTEN:
                username, led = KAARTEN[kaart_id]

                nieuwe_status = toggle_user(username)

                if nieuwe_status is not None:
                    led.value(nieuwe_status)

                    # MicroPython-safe capitalize
                    naam_netjes = username[:1].upper() + username[1:]

                    lcd.clear()
                    if nieuwe_status:
                        lcd.putstr(naam_netjes + "\nis ONLINE")
                    else:
                        lcd.putstr(naam_netjes + "\nis OFFLINE")

                    time.sleep(5)
                    lcd.clear()
                    lcd.putstr("Scan uw kaart...")

                else:
                    lcd.clear()
                    lcd.putstr("DB Fout!")
                    time.sleep(2)
                    lcd.clear()
                    lcd.putstr("Scan uw kaart...")

            else:
                print("Onbekende kaart:", kaart_id)
                lcd.clear()
                lcd.putstr("Onbekende kaart!\nToegang geweigerd")
                time.sleep(3)
                lcd.clear()
                lcd.putstr("Scan uw kaart...")

    time.sleep(0.1)
