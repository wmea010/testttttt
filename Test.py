import json
import tkinter as tk
import pyttsx3
import psycopg2
from datetime import datetime

def check_login(username, password):
    try:
        conn = psycopg2.connect(
            host="4.211.203.204",
            database="steamdatabase",
            user="jochem",
            password="jochem123",
            port=5432
        )
        cur = conn.cursor()

        #Login check in PgAdmin
        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s AND can_login=TRUE",
            (username, password)
        )
        result = cur.fetchone()

        #als login klopt, dan de last_seen updaten in PgAdmin
        if result:
            cur.execute(
                "UPDATE users SET last_seen = NOW() WHERE username = %s",
                (username,)
            )
            conn.commit()

        conn.close()
        return result is not None

    #foutmelding
    except Exception as e:
        print("Database error:", e)
        return False

#Data bestand uitlezen
with open("steam.json", "r", encoding="utf-8") as bestand:
    data = json.load(bestand)

#print informatie over alle games uit
games_text = ""
for game in data[:10]:
    naam = game["name"]
    prijs = game["price"]
    genre = game["genres"]
    developer = game["developer"]

    games_text += (
        f" {naam}\n"
        f"Genre: {genre}\n"
        f"Ontwikkelaar: {developer}\n"
        f"Prijs: €{prijs}\n\n"
    )

#tekst voorlezen
engine = pyttsx3.init()
def voorlezen():
    engine.say(games_text)
    engine.runAndWait()


#Mouseover, als de muis ergens overheen gaat, verschijnt er een tooltip met info.
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        x = self.widget.winfo_rootx() + 40
        y = self.widget.winfo_rooty() + 20
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        self.tip.geometry(f"+{x}+{y}")
        tk.Label(
            self.tip,
            text=self.text,
            bg="#fff8c4",
            fg="black",
            padx=8,
            pady=5,
            relief="solid",
            borderwidth=1
        ).pack()

    def hide(self, event=None):
        if self.tip:
            self.tip.destroy()
            self.tip = None

#Vriendenlijst ophalen uit PgAdmin
def get_users():
    try:
        conn = psycopg2.connect(
            host="4.211.203.204",
            database="steamdatabase",
            user="jochem",
            password="jochem123",
            port=5432
        )
        cur = conn.cursor()
        #Query van PgAdmin
        cur.execute("""
            SELECT username, last_seen
            FROM users
            ORDER BY last_seen DESC NULLS LAST
        """)
        users = cur.fetchall()
        conn.close()
        return users

    #Database Error
    except Exception as e:
        print("DB error:", e)
        return []

#Update de vriendenlijst
def update_friends():
    users = get_users()
    text = "Vriendenstatus\n\n"
    now = datetime.utcnow()
    for username, last_seen in users:
        status = ""
        if not last_seen:
            status = "nooit online geweest"
        else:
            #Zet de Last_Seen tijd naar UTC, de timezone in Nederland
            if hasattr(last_seen, "tzinfo") and last_seen.tzinfo is not None:
                last_seen = last_seen.replace(tzinfo=None)
            #berekent how lang het verschil is tussen wanneer iemand online was en nu
            try:
                diff = now - last_seen
                seconds = diff.total_seconds()
                #Laat de online status zien
                if seconds < 300:
                    status = "ONLINE"
                elif seconds < 3600:
                    status = f"{int(seconds//60)} min geleden"
                elif seconds < 86400:
                    status = f"{int(seconds//3600)} uur geleden"
                else:
                    status = f"{last_seen.strftime('%d-%m %H:%M')}"

            #Database error
            except Exception as e:
                print("Time error:", e)
                status = "onbekend"

        text += f"{username} — {status}\n"
    friends_label.config(text=text)

#Schermtijd en popup als schermtijd voorbij is
kleinkind_naam = ""
schermtijd_minuten = 0
timer_id = None

def schermtijd_popup():
    popup = tk.Toplevel(root)
    popup.config(bg=current_bg)
    naam = kleinkind_naam if kleinkind_naam != "" else "je kleinkind"
    tk.Label(
        popup,
        text=f"Tijd voor een pauze!\n\nGa anders even kijken hoe het met {naam} gaat?",
        font=("Arial", 14),
        bg=current_bg,
        fg=current_fg
    ).pack(padx=20, pady=20)

#Maak een timer aan voor de schermtijd
def instellingen_opslaan():
    global kleinkind_naam, schermtijd_minuten, timer_id
    kleinkind_naam = naam_entry.get()
    if tijd_entry.get() == "":
        status_label.config(text="Vul een tijd in!")
        return
    try:
        schermtijd_minuten = int(tijd_entry.get())

        #Oude timer stoppen zodat er niet meerdere timers op de achtergrond lopen
        if timer_id is not None:
            root.after_cancel(timer_id)

        status_label.config(text="Schermtijd opgeslagen")
        if schermtijd_minuten > 0:
            timer_id = root.after(
                schermtijd_minuten * 60000,
                schermtijd_popup
            )

    #Als een ongeldig getal is ingevuld
    except:
        status_label.config(text="Vul een geldig getal in!")


#Tekst grootte kan worden aangepast
font_size = 13

#Maak de tekst groter
def grotere_tekst():
    global font_size
    if font_size < 30:
        font_size += 2
        games_label.config(font=("Arial", font_size))

#Maak de test kleiner
def kleinere_tekst():
    global font_size
    if font_size > 10:
        font_size -= 2
        games_label.config(font=("Arial", font_size))


#Lichte en donkere themas
dark_mode = False

def apply_theme():
    global current_bg, current_fg
    if dark_mode:
        current_bg = "#1b2838"
        current_fg = "white"
        card = "#2a475e"
    else:
        current_bg = "white"
        current_fg = "black"
        card = "#eaeaea"

#kleurenthema aanpassen
    root.config(bg=current_bg)
    container.config(bg=current_bg)
    left_frame.config(bg=card)
    right_frame.config(bg=current_bg)
    settings_frame.config(bg=card)
    friends_frame.config(bg=card)
    friends_label.config(
        bg=card,
        fg=current_fg
    )

    #Scrollbare lijst
    canvas.config(bg=card)
    scrollable_frame.config(bg=card)
    games_label.config(
        bg=card,
        fg=current_fg
    )
    title.config(
        bg=current_bg,
        fg="#66c0f4" if dark_mode else "black"
    )

#Zet dark mode aan of uit
def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    apply_theme()


#Hoofdvenster aanmaken
root = tk.Tk()
root.title("Steam Accessibility Dashboard")
root.geometry("1200x700")
root.attributes("-fullscreen", True)

root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))


#Titel van het dashboard
title = tk.Label(
    root,
    text="STEAM ACCESSIBILITY DASHBOARD",
    font=("Arial", 20, "bold")
)
title.pack(pady=10)


#Layout van de applicatie
container = tk.Frame(root)
container.pack(fill="both", expand=True)
container.rowconfigure(0, weight=1)
container.columnconfigure(0, weight=3)
container.columnconfigure(1, weight=1)

#Games
left_frame = tk.Frame(container, padx=10, pady=10)
left_frame.grid(row=0, column=0, sticky="nsew")
canvas = tk.Canvas(left_frame, highlightthickness=0)
scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

window_id = canvas.create_window(
    (0, 0),
    window=scrollable_frame,
    anchor="nw"
)

def resize_canvas(event):
    canvas.itemconfig(window_id, width=event.width)
canvas.bind("<Configure>", resize_canvas)
canvas.configure(yscrollcommand=scrollbar.set)
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

games_label = tk.Label(
    scrollable_frame,
    text=games_text,
    font=("Arial", font_size),
    justify="left",
    anchor="nw"
)
games_label.pack(fill="both", expand=True)

#Accessibility dashboard en vriendenlijst
right_frame = tk.Frame(container, padx=10, pady=10)
right_frame.grid(row=0, column=1, sticky="nsew")
right_frame.rowconfigure(0, weight=0)  # bovenkant (knoppen)
right_frame.rowconfigure(1, weight=1)  # onderkant (friends)
friends_frame = tk.Frame(right_frame, padx=10, pady=10)
friends_frame.pack(side="bottom", fill="both", expand=True)
right_frame.columnconfigure(0, weight=1)
friends_label = tk.Label(friends_frame, text="", justify="left", font=("Arial", 20))
friends_label.pack(fill="both", expand=True)

#knoppen
def button(text, cmd, tip):
    b = tk.Button(
        right_frame,
        text=text,
        command=cmd,
        font=("Arial", 11),
        width=20,
        relief="flat"
    )
    b.pack(pady=5, fill="x")
    ToolTip(b, tip)

button("Voorlezen", voorlezen, "Leest alle games voor")
button("Groter", grotere_tekst, "Vergroot tekst")
button("Kleiner", kleinere_tekst, "Verkleint tekst")
button("Thema", toggle_theme, "Wissel licht/donker")


#Schermtijd instellingen
settings_frame = tk.Frame(right_frame, padx=10, pady=10)
settings_frame.pack(pady=15, fill="x")
tk.Label(settings_frame, text="Schermtijd", font=("Arial", 20, "bold")).pack()
tk.Label(settings_frame, text="Naam kleinkind").pack()
naam_entry = tk.Entry(settings_frame)
naam_entry.pack()
tk.Label(settings_frame, text="Minuten").pack()
tijd_entry = tk.Entry(settings_frame)
tijd_entry.pack()
tk.Button(
    settings_frame,
    text="Opslaan",
    command=instellingen_opslaan
).pack(pady=5)

status_label = tk.Label(settings_frame, text="")
status_label.pack()

#werk de online status elke 5 seconden bij
def auto_refresh_friends():
    update_friends()
    root.after(5000, auto_refresh_friends)
auto_refresh_friends()

#launch
apply_theme()

#login scherm om in te loggen
def login_screen():
    login_root = tk.Tk()
    login_root.title("Login")
    login_root.geometry("300x200")

    tk.Label(login_root, text="Gebruikersnaam").pack()
    user_entry = tk.Entry(login_root)
    user_entry.pack()

    tk.Label(login_root, text="Wachtwoord").pack()
    pass_entry = tk.Entry(login_root, show="*")
    pass_entry.pack()

    #Als de login klopt, destroy het login scherm
    def login():
        if check_login(user_entry.get(), pass_entry.get()):
            login_root.destroy()
            root.deiconify()
        else:
            tk.Label(login_root, text="Foute login").pack()
    tk.Button(login_root, text="Login", command=login).pack(pady=10)
    root.withdraw()
    login_root.mainloop()

login_screen()