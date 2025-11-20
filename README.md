# Job-Discovery-Engine

Dit project is een "zelflerende" command-line applicatie die je helpt jobaanbiedingen te ontdekken die écht bij je passen. In plaats van te filteren op harde criteria, leert de applicatie je impliciete voorkeuren door middel van een feedback-cyclus en AI-analyse.

## Features

-   **Automatisch verzamelen**: Haalt jobaanbiedingen uit je e-mail (via IMAP).
-   **Interactieve Feedback**: Een eenvoudige CLI om jobs te beoordelen met een score en tags.
-   **AI-Gegenereerd Profiel**: Gebruikt de Gemini API om een gedetailleerd profiel van jouw voorkeuren op te stellen op basis van je feedback.
-   **AI-Ranking**: Sorteert nieuwe vacatures op relevantie op basis van je persoonlijke profiel.
-   **Veilig**: Beheert geheimen (API-sleutels, wachtwoorden) via een `.env` bestand, niet in de code.

---

## Installatie & Configuratie

Volg deze stappen om de applicatie lokaal op te zetten.

### 1. Vereisten

-   Python 3.8+
-   Een Gmail-account (voor de `Harvester`)
-   Een Google Gemini API-sleutel

### 2. Installatie

1.  **Clone of download de code** naar een map op je computer, bijvoorbeeld `~/projecten/`.

2.  **Navigeer naar de projectmap** in je terminal:
    ```bash
    cd ~/projecten/my-auto-recruiter
    ```

3.  **Installeer de Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuratie

1.  **Maak je `.env` bestand aan** door het voorbeeldbestand te kopiëren. Dit bestand is privé en bevat je geheimen.
    ```bash
    cp .env.example .env
    ```

2.  **Open het `.env` bestand** met een editor:
    ```bash
    nano .env
    ```

3.  **Vul je gegevens in:**
    -   `GEMINI_API_KEY`: Plak hier je API-sleutel van Google AI Studio.
    -   `IMAP_USERNAME`: Je volledige Gmail-adres (bv. `jouwnaam@gmail.com`).
    -   `IMAP_PASSWORD`: **BELANGRIJK:** Gebruik hier **niet** je gewone Gmail-wachtwoord. Genereer een "App Password" in je Google Account instellingen. Dit is een 16-cijferig wachtwoord specifiek voor deze applicatie.

---

## Hoe te gebruiken: De Workflow

De applicatie wordt bestuurd via `main.py`. Voer de commando's altijd uit vanuit de `my-auto-recruiter` map.

### Stap 1: Verzamel Vacatures (`harvest`)

Dit commando logt in op je e-mailaccount, zoekt naar ongelezen job-alerts, en slaat de gevonden vacatures op in de lokale database.
```bash
python3 main.py harvest
```

### Stap 2: Beoordeel Vacatures (`curate`)

Start de interactieve sessie om de nieuwe vacatures te beoordelen. Dit is de belangrijkste stap om de AI te trainen.
```bash
python3 main.py curate
```
Geef een **score (0-10)** en een optionele **tag** (bv. "goede sfeer", "te ver weg").

### Stap 3: Genereer je Profiel (`profile`)

Nadat je een set vacatures (bv. 20+) hebt beoordeeld, laat je de AI je feedback analyseren. Dit creëert of update je persoonlijke voorkeursprofiel.
```bash
python3 main.py profile
```
Het resultaat wordt opgeslagen in `my_dynamic_profile.txt`.

### Stap 4: Ontdek de Beste Jobs (`scout`)

De `Scout` gebruikt je profiel om de nieuwste, nog niet-beoordeelde jobs te sorteren op relevantie.
```bash
python3 main.py scout
```
Je krijgt een gesorteerde tabel te zien met de meest relevante jobs bovenaan, inclusief een score en een korte redenering van de AI.

**Tip:** Herhaal deze cyclus regelmatig. Hoe meer feedback je geeft, hoe beter de AI je voorkeuren zal begrijpen!
