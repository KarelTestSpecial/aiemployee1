# database.py - Functies voor het beheren van de SQLite-database
import sqlite3
from rich.console import Console

from config import DB_FILE

def initialize_database():
    """
    Controleert of de database en de 'jobs'-tabel bestaan.
    Maakt ze aan als ze niet bestaan.
    Dit zorgt ervoor dat de applicatie altijd kan starten, zelfs bij de eerste run.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Controleer of de 'jobs'-tabel bestaat
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jobs'")
    if c.fetchone() is None:
        console = Console()
        console.print(f"[bold yellow]Database table 'jobs' not found. Creating it now at {DB_FILE}...[/bold yellow]")
        # Maak de tabel aan
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
