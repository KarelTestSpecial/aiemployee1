# main.py - The orchestrator for the Job-Discovery-Engine
import argparse
from rich.console import Console

from harvester import Harvester
from curator import Curator
from profiler import Profiler
from scout import Scout
from database import initialize_database

def main():
    """Hoofdfunctie om de CLI te beheren."""
    console = Console()
    parser = argparse.ArgumentParser(
        description="Job-Discovery-Engine: A self-learning job discovery tool.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "agent",
        choices=["harvest", "curate", "profile", "scout"],
        help="""The agent to run:
  - harvest: Collect new job postings.
  - curate: Start the interactive job review session.
  - profile: Analyze your feedback and update your preference profile.
  - scout:   View new jobs, sorted by your profile.
"""
    )

    args = parser.parse_args()

    try:
        if args.agent == "harvest":
            agent = Harvester()
            agent.run()
        elif args.agent == "curate":
            agent = Curator()
            agent.run()
        elif args.agent == "profile":
            agent = Profiler()
            agent.run()
        elif args.agent == "scout":
            agent = Scout()
            agent.run()
    except ValueError as e:
        # Vang de API-sleutel fout op die door Profiler en Scout wordt gegooid
        console.print(f"[bold red]Configuration Error:[/bold red] {e}")
        console.print("Please set your GEMINI_API_KEY in 'my-auto-recruiter/config.py'.")
    except ImportError as e:
        console.print(f"[bold red]Import Error:[/bold red] {e}")
        console.print("Please make sure you are running this script from the root directory of the project.")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred:[/bold red] {e}")


if __name__ == "__main__":
    main()
