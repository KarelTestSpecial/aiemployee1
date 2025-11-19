# harvester.py - The Harvester Agent
import sqlite3
import trafilatura
from rich.console import Console

from config import DB_FILE
from database import initialize_database

class Harvester:
    def __init__(self):
        self.console = Console()
        initialize_database()  # Zorgt ervoor dat de database en tabel bestaan
        self.conn = sqlite3.connect(DB_FILE)

    def store_job(self, title, company, description, url):
        """Slaat een nieuwe job op in de database, als de URL nog niet bestaat."""
        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO jobs (title, company, description, url) VALUES (?, ?, ?, ?)",
                      (title, company, description, url))
            self.conn.commit()
            self.console.print(f"[green]Stored new job: {title}[/green]")
            return True
        except sqlite3.IntegrityError:
            self.console.print(f"[yellow]Job already exists: {url}[/yellow]")
            return False
        except Exception as e:
            self.console.print(f"[bold red]Error storing job: {e}[/bold red]")
            return False

    def fetch_job_from_url(self, url):
        """Haalt de tekst van een job-URL op met trafilatura."""
        self.console.print(f"[cyan]Fetching job from {url}...[/cyan]")
        # Let op: veel sites blokkeren scrapers. Een robuuste implementatie vereist mogelijk
        # technieken zoals het roteren van user-agents of het gebruik van scraping services.
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            return trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        self.console.print(f"[bold red]Failed to download content from {url}[/bold red]")
        return None

    def run_from_urls(self, url_list):
        """Een run-methode die een lijst van URLs als input neemt voor demonstratiedoeleinden."""
        self.console.print("[bold cyan]Starting Harvester from URL list...[/bold cyan]")
        for url in url_list:
            job_text = self.fetch_job_from_url(url)
            if job_text:
                self.console.print(f"  [green]Successfully extracted text (length: {len(job_text)}).[/green]")
                # Het programmatisch extraheren van titel/bedrijf is complex en vereist
                # domein-specifieke logica. We slaan de URL op als titel.
                self.store_job(title=url, company="Unknown", description=job_text, url=url)
            else:
                self.console.print(f"  [red]Failed to extract text from {url}.[/red]")
        self.conn.close()

    def run(self):
        """
        **Placeholder & Demo:** De volledige IMAP-implementatie is niet in scope voor deze PoC.
        Deze methode simuleert de workflow door een vaste lijst van URLs te gebruiken.

        **Volgende stappen voor een volledige implementatie:**
        1. Implementeer IMAP-logica om in te loggen op een e-mailaccount.
        2. Zoek naar e-mails van job-alerts (bv. LinkedIn, Indeed).
        3. Extraheer de URLs uit de body van de e-mails.
        4. Roep `run_from_urls` aan met de gevonden URLs.
        """
        self.console.print("[bold yellow]Harvester (IMAP) is a placeholder.[/bold yellow]")
        self.console.print("Running a demo with a predefined URL list instead.")
        demo_urls = [
            'https://www.ictjob.be/nl/vacature/477113/python-developer/it-jobs-brussel',
            'https://www.vdab.be/v2/jobs/job-offer-ex/000072349141'
        ]
        self.run_from_urls(demo_urls)


if __name__ == '__main__':
    harvester = Harvester()
    harvester.run()
