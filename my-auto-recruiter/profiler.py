# profiler.py - The Profiler Agent
import json
import os
import google.generativeai as genai
from rich.console import Console

# Importeer de geconfigureerde bestandsnamen
from config import TRAINING_DATA_FILE, PROFILE_FILE, GEMINI_API_KEY

class Profiler:
    def __init__(self):
        self.console = Console()
        # Configureer de Gemini API
        if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_GEMINI_API_KEY":
            raise ValueError("GEMINI_API_KEY is not set. Please set it in config.py or as an environment variable.")
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def load_training_data(self):
        """Laadt de trainingsdata uit het JSONL-bestand."""
        if not os.path.exists(TRAINING_DATA_FILE):
            self.console.print(f"[bold red]Error: Training data file not found at {TRAINING_DATA_FILE}[/bold red]")
            return None

        with open(TRAINING_DATA_FILE, 'r', encoding='utf-8') as f:
            return [json.loads(line) for line in f]

    def generate_profile(self, training_data):
        """Genereert een gebruikersprofiel op basis van de trainingsdata."""
        self.console.print("[cyan]Analyzing your feedback to generate a profile...[/cyan]")

        # Bouw de prompt op
        prompt_lines = [
            "You are a career counselor AI. Analyze the following job feedback from a user. The user has rated several jobs and provided tags.",
            "Based on this data, create a detailed 'Implicit User Preference Profile' in natural language.",
            "Focus on the underlying patterns, not just the job titles. What does the user value? What do they dislike? What are the common themes?",
            "For example, look for preferences in work environment (remote, office), company culture (startup, corporate), work type (creative, manual), and skills.",
            "Here is the user's feedback data in JSON format:",
            "---"
        ]

        for item in training_data:
            prompt_lines.append(json.dumps(item, indent=2))

        prompt_lines.append("---")
        prompt_lines.append("Now, provide the detailed Implicit User Preference Profile.")

        prompt = "\n".join(prompt_lines)

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            self.console.print(f"[bold red]An error occurred while calling the Gemini API: {e}[/bold red]")
            return None

    def save_profile(self, profile_text):
        """Slaat het gegenereerde profiel op."""
        with open(PROFILE_FILE, 'w', encoding='utf-8') as f:
            f.write(profile_text)
        self.console.print(f"[green]User profile saved to {PROFILE_FILE}[/green]")

    def run(self):
        """Voert de volledige profileringscyclus uit."""
        training_data = self.load_training_data()
        if not training_data:
            return

        profile_text = self.generate_profile(training_data)
        if profile_text:
            self.save_profile(profile_text)

if __name__ == '__main__':
    # Om het script direct te testen
    # Let op: je hebt een geldige GEMINI_API_KEY nodig in config.py
    try:
        profiler = Profiler()
        profiler.run()
    except ValueError as e:
        print(e)
