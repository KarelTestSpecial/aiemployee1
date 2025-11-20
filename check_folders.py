import imaplib
import os
from dotenv import load_dotenv

# Laad je wachtwoord in
load_dotenv()

username = os.getenv("IMAP_USERNAME")
password = os.getenv("IMAP_PASSWORD")

print(f"Inloggen als {username}...")

try:
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)

    print("\n--- JOUW GMAIL MAPPENLIJST ---")
    status, folders = mail.list()
    
    for folder in folders:
        # Decodeer de bytes naar tekst
        print(folder.decode())
        
    print("------------------------------")
    mail.logout()
except Exception as e:
    print(f"Fout: {e}")
