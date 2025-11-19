# scout.py - The Scout Agent
import sqlite3
import os
import google.generativeai as genai
from rich.console import Console

from config import DB_FILE, PROFILE_FILE, GEMINI_API_KEY
from database import initialize_database

class Scout:
    def __init__(self):
        self.console = Console()
        initialize_database()  # Zorgt ervoor dat de database en tabel bestaan
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row

        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Please create a .env file based on .env.example.")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-flash')

    def load_profile(self):
        """Laadt het gebruikersprofiel."""
        if not os.path.exists(PROFILE_FILE):
            self.console.print(f"[bold yellow]Warning: Profile file not found. Scouting will be generic.[/bold yellow]")
            return "A generic user looking for any job."

        with open(PROFILE_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def get_unprocessed_jobs(self):
        """Haalt alle nog niet beoordeelde jobs uit de database."""
        c = self.conn.cursor()
        c.execute("SELECT * FROM jobs WHERE processed = 0")
        return c.fetchall()

    def run(self):
        """
        **Placeholder & Demo:** De AI-gebaseerde sortering is niet in scope voor deze PoC.
        Deze methode simuleert de workflow door de onverwerkte jobs te tonen.

        **Volgende stappen voor een volledige implementatie:**
        1. Bouw een prompt die het gebruikersprofiel en de jobomschrijvingen bevat.
        2. Vraag de AI om elke job te scoren op basis van het profiel.
        3. Parse de output van de AI.
        4. Sorteer de jobs op basis van de AI-gegenereerde score en toon ze aan de gebruiker.
        """
        self.console.print("[bold cyan]Starting Scout Agent...[/bold cyan]")
        profile = self.load_profile()
        unprocessed_jobs = self.get_unprocessed_jobs()

        if not unprocessed_jobs:
            self.console.print("[yellow]No new jobs to scout.[/yellow]")
            self.conn.close()
            return

        self.console.print(f"Scouting {len(unprocessed_jobs)} new jobs based on the profile:")
        self.console.print(f"[italic gray]{profile[:300].strip()}...[/italic]\\n")

        self.console.print("[bold yellow]AI-based sorting is a placeholder.[/bold yellow]")
        self.console.print("The jobs below are unsorted and would be ranked by the AI in a full implementation:")

        for job in unprocessed_jobs:
            self.console.print(f"  - [ ] {job['title']}")

        self.conn.close()


if __name__ == '__main__':
    try:
        scout = Scout()
        scout.run()
    except ValueError as e:
        print(e)
