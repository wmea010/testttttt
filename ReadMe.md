# Steam Project - Team Enjoy

**Welkom bij het Steam project van Team Enjoy!** <br/>
In dit project maken wij een dashboard voor het bedrijf Steam.
Dit dashboard is speciaal gemaakt voor ouderen die graag willen gamen.
Het is heel rustig, simpel en makkelijk te gebruiken, ook voor slechtzienden en kleurenblinden.
Met handige knoppen maak je de tekst groter, wissel je tussen licht en donker en kan je de tekst laten voorlezen.
Ook kan je een schermtijd instellen zodat men niet te lang achter een scherm zit.

Om bij het dashboard te komen, moet men inloggen met een steam account dat in een database staat. Als het wachtwoord niet bij de gebruikersnaam past wordt de gebruiker niet toegelaten.
Als het wachtwoord klopt, dan komt de gebruiker in het dashboard. 
In de vriendenlijst kan gezien worden wie momenteel online en wanneer iemand voor het laatst online was.


## Team enjoy

| Naam   | Leerlingnummer | Rol           |
|--------|----------------|---------------|
| Jochem | 1921223        | SD/Teamleider |
| Ayman  | 1909871        | Ai            |
| Wassim | 1922834        | CSC           |
| Ayoub  | 1908033        | BIM           |
| Amin   | 1911328        | TI            |



## Software development

Jochem is verantwoordelijk voor het maken van het Steam dashboard:
- Data van steam wordt uit het `.json` bestand gehaald
- Er is gebruik gemaakt van `tkinter`
- Er zijn meerdere knoppen om de gebruikerservaring van senioren te verbeteren
- Optie om schermtijd in te stellen
- Inlogfunctie voor meerdere accounts en vriendenlijst




## Artificial Intelligence

Ayman is verantwoordelijk voor Het analyserapport:
- Het rapport onderzoekt de schermtijd van gamers van 45 jaar en ouder
- De schermtijd in uren per week is gekozen als variabel
- Mogelijke factoren zijn: Leeftijd, jaar, type games, gamingplatform en de hoeveelheid gamers binnen de leeftijdsgroep
- Oudere mensen gamen minder, maar het aantal gamers boven de 45 groeit sterk




## Cybersecurity

CSC – Cyber Security and Cloud
Verantwoordelijke: Wassim
Azure VM & Database

PostgreSQL database opgezet op een Azure Virtual Machine (CSC-Wassim-01, IP: 4.211.203.204)
Database aangemaakt: steamdatabase
Firewall (NSG) geconfigureerd met inbound rules voor poort 22 (SSH) en poort 5432 (PostgreSQL)

Account-autorisatie

Elk teamlid heeft een eigen databaseaccount met individuele inloggegevens
Wassim heeft beheerdersrechten (superuser)
Teamleden hebben toegang tot de steamdatabase via hun eigen account
Accounts aangemaakt: wassim, amin, ayoub, jochem, ayman

Flask Webserver

Flask webserver opgezet op de Azure VM
Bereikbaar via http://4.211.203.204:5000
Poort 5000 opengezet in de Azure NSG

Raspberry Pi

Raspberry Pi OS geïnstalleerd en geconfigureerd via Raspberry Pi Imager
SSH ingeschakeld voor remote toegang
VNC ingeschakeld
Verbonden via WiFi hotspot
Benodigde software geïnstalleerd: python3-tk, espeak, psycopg2-binary, pyttsx3
Steam-applicatie wordt uitgevoerd op de Raspberry Pi

Lokaal Netwerk

Raspberry Pi ingesteld als Wireless Bridge
Switch aangesloten op de Pi zodat teamleden via ethernet verbinding kunnen maken




## Business IT en Management

Ayoub is verantwoordelijk voor de stakeholder analyse en de requirements specificatie:
- Functionaliteiten vastgesteld
- Stakeholders geïdentificeerd
- Wireframes gemaakt




## Technische Informatica

TI - technische informatie
verantwoordlijke: Amin Amohammadi

- Een RFID-scanner herkent de kaart van een gebruiker
- De gebruiker wordt via WiFi in een PostgreSQL database online of offline gezet
- Een LCD-schermpje toont wie er in- of uitcheckt
- Elke gebruiker heeft een eigen LED die aan of uitgaat bij het scannen
- Een fysieke knop zet iedereen tegelijk offline met één druk

# Hoe gebruik je deze code?
Om deze code van GitHub in PyCharm te gebruiken, kopieer je eerst de URL van de repository via de groene Code knop op de website.
Vervolgens open je PyCharm en kies je in het startmenu voor de optie Get from Version Control.
Nadat je de gekopieerde URL hebt geplakt en op Clone hebt geklikt, downloadt het programma het volledige project naar je computer.



