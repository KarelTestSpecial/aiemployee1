# scout.py - The Scout Agent
import sqlite3
import os
import json
import google.generativeai as genai
from rich.console import Console
from rich.table import Table

from config import DB_FILE, PROFILE_FILE, GEMINI_API_KEY
from database import initialize_database

class Scout:
    def __init__(self):
        self.console = Console()
        initialize_database()  # Zorgt ervoor dat de database en tabel bestaan
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row

        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set. Please create a .env file or set it in the environment.")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-flash-latest')

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

    def rank_jobs_with_ai(self, profile, jobs):
        """Gebruikt de Gemini API om jobs te ranken op basis van het profiel."""
        self.console.print("[cyan]Scouting with AI... This may take a moment.[/cyan]")

        # Bouw een prompt die de AI instrueert om JSON terug te geven
        prompt_parts = [
            "You are a Job Scout AI. Your task is to rank the following jobs based on the user's preference profile.",
            "Analyze the user profile:",
            "--- PROFILE ---",
            profile,
            "--- END PROFILE ---",
            "\nNow, for each of the following jobs, provide a relevance score from 0 to 100 and a brief one-sentence reasoning.",
            "Return your response as a single valid JSON array of objects. Each object must have three keys: 'job_id', 'score', and 'reasoning'.",
            "Example: [{'job_id': 1, 'score': 85, 'reasoning': 'Matches preference for Python and remote work.'}]",
            "\n--- JOBS ---"
        ]

        job_data_for_prompt = []
        for job in jobs:
            job_data_for_prompt.append({
                "job_id": job['id'],
                "title": job['title'],
                "description": job['description'][:1000] # Beperk de lengte om de prompt beheersbaar te houden
            })

        prompt_parts.append(json.dumps(job_data_for_prompt))
        prompt_parts.append("--- END JOBS ---")
        prompt_parts.append("Now, provide only the JSON array as your response.")

        prompt = "\n".join(prompt_parts)

        try:
            response = self.model.generate_content(prompt)
            # Probeer de JSON te parsen. Soms voegt de AI extra tekst toe (bv. ```json ... ```)
            cleaned_response = response.text.strip().replace("```json", "").replace("```", "")
            ranked_data = json.loads(cleaned_response)
            return ranked_data
        except Exception as e:
            self.console.print(f"[bold red]AI ranking failed. Error: {e}[/bold red]")
            self.console.print(f"Raw AI response was: {response.text}")
            return None

    def run(self):
        """Voert de volledige scouting en ranking cyclus uit."""
        self.console.print("[bold cyan]Starting Scout Agent...[/bold cyan]")
        profile = self.load_profile()
        unprocessed_jobs = self.get_unprocessed_jobs()

        if not unprocessed_jobs:
            self.console.print("[yellow]No new jobs to scout.[/yellow]")
            self.conn.close()
            return

        ranked_data = self.rank_jobs_with_ai(profile, unprocessed_jobs)

        if not ranked_data:
            self.console.print("[yellow]Could not rank jobs. Displaying them unsorted.[/yellow]")
            for job in unprocessed_jobs:
                 self.console.print(f"  - [ ] {job['title']}")
            return

        # Maak een mapping van job_id naar job-object voor gemakkelijke toegang
        jobs_by_id = {job['id']: job for job in unprocessed_jobs}

        # Sorteer de resultaten van de AI op score (hoog naar laag)
        ranked_data.sort(key=lambda x: x.get('score', 0), reverse=True)

        table = Table(title="Scouted Jobs (Ranked by AI)", show_lines=True)
        table.add_column("Score", style="magenta", justify="center")
        table.add_column("Title", style="cyan")
        table.add_column("AI Reasoning", style="green")

        for item in ranked_data:
            job = jobs_by_id.get(item.get('job_id'))
            if job:
                table.add_row(
                    str(item.get('score', 'N/A')),
                    job['title'],
                    item.get('reasoning', 'No reasoning provided.')
                )

        self.console.print(table)
        self.conn.close()

if __name__ == '__main__':
    try:
        scout = Scout()
        scout.run()
    except ValueError as e:
        print(e)
