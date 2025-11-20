# curator.py - The Curator Agent
import sqlite3
import json
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt

from config import DB_FILE, TRAINING_DATA_FILE
from database import initialize_database

class Curator:
    def __init__(self):
        self.console = Console()
        initialize_database()  # Zorgt ervoor dat de database en tabel bestaan
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row

    def get_unprocessed_jobs(self):
        """Haalt alle nog niet beoordeelde jobs uit de database."""
        c = self.conn.cursor()
        c.execute("SELECT * FROM jobs WHERE processed = 0")
        return c.fetchall()

    def mark_job_as_processed(self, job_id):
        """Markeert een job als beoordeeld in de database."""
        c = self.conn.cursor()
        c.execute("UPDATE jobs SET processed = 1 WHERE id = ?", (job_id,))
        self.conn.commit()

    def save_feedback(self, job, score, tag):
        """Slaat de feedback van de gebruiker op in een JSONL-bestand."""
        feedback_entry = {
            "job_id": job['id'],
            "title": job['title'],
            "company": job['company'],
            "description": job['description'],
            "url": job['url'],
            "score": score,
            "tag": tag
        }
        with open(TRAINING_DATA_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(feedback_entry, ensure_ascii=False) + '\n')

    def run(self):
        """Start de interactieve feedback-sessie."""
        self.console.print("[bold cyan]Starting Job Curation Session...[/bold cyan]")
        unprocessed_jobs = self.get_unprocessed_jobs()

        if not unprocessed_jobs:
            self.console.print("[yellow]No new jobs to review.[/yellow]")
            return

        for job in unprocessed_jobs:
            self.console.print(Panel(f"[bold]{job['title']}[/bold]\\n[italic]{job['company']}[/italic]\\n\\n{job['description']}",
                                     title="Job Details", border_style="green"))

            score = IntPrompt.ask("Score (0-10), or -1 to quit", choices=[str(i) for i in range(-1, 11)])

            if score == -1:
                self.console.print("[bold red]Quitting session.[/bold red]")
                break

            tag = Prompt.ask("Optional tag (e.g., 'good culture', 'bad pay')")

            self.save_feedback(job, score, tag)
            self.mark_job_as_processed(job['id'])
            self.console.print(f"[green]Feedback saved for job {job['id']}.[/green]\\n")

        self.conn.close()
        self.console.print("[bold cyan]Curation session finished.[/bold cyan]")

if __name__ == '__main__':
    # Om het script direct te testen
    curator = Curator()
    curator.run()
