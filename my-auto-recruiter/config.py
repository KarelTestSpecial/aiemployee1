import os
from dotenv import load_dotenv

# Laad de omgevingsvariabelen uit het .env-bestand
# Dit bestand staat in .gitignore en wordt niet meegestuurd naar de repository.
load_dotenv()

# De absolute pad naar de map waarin dit bestand zich bevindt.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Haal de secrets op uit de omgevingsvariabelen
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
IMAP_USERNAME = os.getenv("IMAP_USERNAME")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD")

# IMAP Server (niet-geheim)
IMAP_SERVER = "imap.gmail.com"

# Bestandspaden
DB_FILE = os.path.join(BASE_DIR, "jobs_inbox.db")
TRAINING_DATA_FILE = os.path.join(BASE_DIR, "training_data.jsonl")
PROFILE_FILE = os.path.join(BASE_DIR, "my_dynamic_profile.txt")

# Configureer de Gemini API key als deze is ingesteld
if GEMINI_API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=GEMINI_API_KEY)
