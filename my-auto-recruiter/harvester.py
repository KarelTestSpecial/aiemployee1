# harvester.py - The Harvester Agent
import sqlite3
import trafilatura
from rich.console import Console
import imaplib
import email
import re
from email.header import decode_header

from config import DB_FILE, IMAP_SERVER, IMAP_USERNAME, IMAP_PASSWORD
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
            # Dit is een normale, verwachte gebeurtenis, dus geen harde foutmelding.
            return False
        except Exception as e:
            self.console.print(f"[bold red]Error storing job: {e}[/bold red]")
            return False

    def fetch_job_from_url(self, url):
        """Haalt de tekst van een job-URL op met trafilatura."""
        self.console.print(f"  [cyan]Fetching job from {url}...[/cyan]")
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            return trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        self.console.print(f"  [bold red]Failed to download content from {url}[/bold red]")
        return None

    def run_from_urls(self, url_list):
        """Een run-methode die een lijst van URLs als input neemt."""
        self.console.print(f"[bold cyan]Processing {len(url_list)} extracted URLs...[/bold cyan]")
        new_jobs_found = 0
        for url in url_list:
            job_text = self.fetch_job_from_url(url)
            if job_text:
                if self.store_job(title=url, company="Unknown", description=job_text, url=url):
                    new_jobs_found += 1
        return new_jobs_found

    def run(self):
        """
        Maakt verbinding met het IMAP-account, haalt URLs uit ongelezen e-mails en verwerkt ze.
        """
        self.console.print("[bold cyan]Starting Harvester...[/bold cyan]")
        if not IMAP_USERNAME or not IMAP_PASSWORD:
            self.console.print("[bold red]IMAP credentials not found in .env file. Cannot fetch emails.[/bold red]")
            return

        all_urls = set()
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(IMAP_USERNAME, IMAP_PASSWORD)
            mail.select('inbox')

            # Zoek naar ongelezen e-mails. Je kunt dit specifieker maken,
            # bijvoorbeeld: '(UNSEEN FROM "jobs@linkedin.com")'
            status, messages = mail.search(None, '(UNSEEN)')

            if status != 'OK':
                self.console.print("[yellow]Error searching for emails.[/yellow]")
                return

            email_ids = messages[0].split()
            if not email_ids:
                self.console.print("[green]No new unread emails found.[/green]")
                return

            self.console.print(f"Found {len(email_ids)} unread emails. Parsing for URLs...")

            for email_id in email_ids:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        # Zoek naar URLs in de body van de e-mail
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                if "text/html" in content_type or "text/plain" in content_type:
                                    try:
                                        body = part.get_payload(decode=True).decode()
                                        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', body)
                                        all_urls.update(urls)
                                    except:
                                        pass
                        else:
                            try:
                                body = msg.get_payload(decode=True).decode()
                                urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', body)
                                all_urls.update(urls)
                            except:
                                pass

            mail.logout()

        except Exception as e:
            self.console.print(f"[bold red]An error occurred during email harvesting: {e}[/bold red]")
            return

        if all_urls:
            new_jobs_found = self.run_from_urls(list(all_urls))
            self.console.print(f"[bold green]Harvesting complete. Found {new_jobs_found} new jobs.[/bold green]")
        else:
            self.console.print("[green]No new URLs found in unread emails.[/green]")

        self.conn.close()

if __name__ == '__main__':
    harvester = Harvester()
    harvester.run()
