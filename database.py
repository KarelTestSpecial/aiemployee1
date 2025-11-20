# database.py - Functies voor het beheren van de SQLite-database
import sqlite3
from rich.console import Console
import os

# Haal de DB_FILE-locatie op uit de configuratie.
# Dit vereist dat de 'config'-module vindbaar is, wat het geval is als scripts
# vanuit de 'my-auto-recruiter' map worden uitgevoerd.
try:
    from config import DB_FILE
except (ModuleNotFoundError, ImportError):
    # Fallback voor het geval het script op een onverwachte manier wordt aangeroepen
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_FILE = os.path.join(BASE_DIR, "jobs_inbox.db")


def initialize_database():
    """
    Controleert of de database en de 'jobs'-tabel bestaan.
    Maakt ze aan als ze niet bestaan.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
    if c.fetchone() is None:
        console = Console()
        console.print(f"[bold yellow]Database table 'jobs' not found. Creating it now at {DB_FILE}...[/bold yellow]")
        c.execute("""
        CREATE TABLE jobs (
            id INTEGER PRIMARY KEY,
            title TEXT,
            company TEXT,
            description TEXT,
            url TEXT UNIQUE,
            processed INTEGER DEFAULT 0
        )
        """)
        conn.commit()
        console.print("[green]Database table 'jobs' created successfully.[/green]")

    conn.close()
