# Magistra

Een woordjes overhoring applicatie gebouwd met Flask en PostgreSQL.

## Features

- Maak woordenlijsten met bron- en doeltaal
- Voeg woorden toe aan lijsten
- Oefen met een interactieve quiz
  - Bidirectionele quizzes (bron→doel en doel→bron)
  - Mixed quizzes met meerdere lijsten tegelijk
  - Foute antwoorden worden herhaald tot je ze goed hebt
- Houd scores bij (goed/fout per woord)

## Quick Start

```bash
# 1. Maak virtual environment en installeer dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Start database
docker compose up -d

# 3. Build frontend assets
docker compose run --rm vite yarn build

# 4. Run migrations
flask db upgrade

# 5. Start applicatie
python run.py
```

Open **http://localhost:5000** in je browser!

## Setup Instructies

### Aanbevolen Setup: PyCharm + Docker Database

Deze setup geeft je de beste development ervaring:
- ✅ Flask draait lokaal (snelle reload, debugger werkt perfect)
- ✅ PostgreSQL in Docker (geen lokale PostgreSQL installatie nodig)
- ✅ PyCharm herkent alles automatisch

#### 1. Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Op Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Voor testing en linting
```

#### 2. PostgreSQL Database (Docker)

Start de PostgreSQL database met Docker Compose:

```bash
# Start database (draait op achtergrond)
docker compose up -d

# Check of database draait
docker compose ps
```

**Vereisten:**
- Docker Desktop geïnstalleerd ([download hier](https://www.docker.com/products/docker-desktop))

**Database credentials** (al geconfigureerd in docker-compose.yml):
- Database: `magistra`
- User: `magistra`
- Password: `magistra`
- Port: `5432`

#### 3. Environment Configuratie

Een `.env` bestand is al aangemaakt met de juiste configuratie:

```env
# Flask Configuration
SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
FLASK_DEBUG=1

# Database Configuration
DATABASE_URL=postgresql://magistra:magistra@localhost/magistra
```

Voor productie: verander de `SECRET_KEY`!

#### 4. PyCharm Configuratie

**Python Interpreter instellen:**
1. Open PyCharm Settings (CMD+, of File → Settings)
2. Ga naar **Project: magistra → Python Interpreter**
3. Klik **Add Interpreter → Add Local Interpreter**
4. Kies **Existing environment**
5. Selecteer: `venv/bin/python`
6. Klik **OK**

**Run Configuration maken:**
1. Klik **Add Configuration** (rechtsboven)
2. Klik **+** → **Python**
3. Vul in:
   - **Name:** `Run Magistra`
   - **Script path:** `run.py`
   - **Working directory:** (project root)
   - **Environment variables:** Vink **Load from .env file** aan
4. Klik **OK**

Nu kun je de app starten met de ▶️ knop of debuggen met 🐛!

#### 5. Database Migraties

Eerste keer:

```bash
# Voer migrations uit (creëert de tables)
flask db upgrade
```

Later, als je models wijzigt:

```bash
flask db migrate -m "Beschrijving van wijziging"
flask db upgrade
```

**Database recovery** (als je database in een inconsistente staat raakt):

```bash
# Als Alembic denkt dat migraties zijn uitgevoerd maar tabellen niet bestaan:
flask db stamp base      # Reset migration tracking (behoudt data)
flask db upgrade head    # Voer alle migraties uit
```

⚠️ **Let op:** Gebruik nooit `db.drop_all()` tenzij je bewust alle data wilt verwijderen!

#### 6. (Optioneel) Seed de Database met Voorbeelddata

Om snel te beginnen met oefenen, kun je de database vullen met voorbeeldlijsten:

```bash
# Seed basis talen (Nederlands, Engels, Latijn, Grieks)
python seed_languages.py

# Seed Grieks alfabet (25 letters + 16 combinaties)
python seed_greek_alphabet.py

# Seed 23 Latijnse werkwoorden met volledige vervoegingen (4 tijden)
python seed_latin_verbs_extended.py
```

#### 7. Start de Applicatie

**In PyCharm:** Klik op ▶️ **Run 'Run Magistra'**

**Of via terminal:**
```bash
python run.py
```

Ga naar **http://localhost:5000** in je browser.

---

### Alternatief: Handmatige PostgreSQL installatie

Wil je geen Docker gebruiken? Je kunt ook PostgreSQL lokaal installeren:

**macOS (met Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
createdb magistra
```

**Ubuntu/Debian:**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createdb magistra
```

Update dan je `.env`:
```env
DATABASE_URL=postgresql://jouw_username@localhost/magistra
```

## Project Structuur

De applicatie volgt een volledige OOP architectuur met separation of concerns:

```
magistra/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models (List, Entry)
│   ├── repositories.py      # Data access layer (Repository pattern)
│   ├── services.py          # Business logic layer (Services)
│   ├── views.py             # Presentation layer (Class-based views)
│   ├── routes.py            # URL routing configuration
│   └── forms.py             # WTForms form definitions
├── templates/               # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── list_detail.html
│   ├── quiz.html
│   ├── mixed_quiz.html
│   └── ...
├── assets/                  # Frontend source files (Vite input)
│   ├── main.js              # JavaScript entry point
│   └── style.css            # CSS source
├── static/
│   └── dist/                # Compiled assets (Vite output)
│       ├── assets/
│       │   ├── main-*.js
│       │   └── main-*.css
│       └── .vite/
│           └── manifest.json
├── migrations/              # Database migrations (Alembic)
├── config.py                # Configuratie
├── run.py                   # Entry point
├── vite.config.js           # Vite configuratie
├── package.json             # Node.js dependencies
├── docker-compose.yml       # Docker services (DB + Vite)
├── seed_languages.py        # Seed script voor basis talen
├── seed_greek_alphabet.py   # Seed script voor Grieks alfabet
├── seed_latin_verbs_extended.py  # Seed script voor Latijnse werkwoorden
└── requirements.txt         # Python dependencies
```

### Architectuur Lagen

1. **Models** (`models.py`): SQLAlchemy ORM models
2. **Repositories** (`repositories.py`): Database CRUD operaties
3. **Services** (`services.py`): Business logic en data transformatie
4. **Views** (`views.py`): Request handling en response rendering
5. **Routes** (`routes.py`): URL mapping naar views

## Gebruik

1. Maak een nieuwe woordenlijst met bron- en doeltaal
2. Voeg woorden toe aan de lijst
3. Klik op "Start Oefening" om te beginnen
4. Type de vertaling en druk op enter
5. Bekijk je score na afloop

## Handige Commando's

### Database
```bash
docker compose up -d          # Start database
docker compose down           # Stop database
docker compose ps             # Check status
docker compose logs -f db     # Bekijk database logs

# Database seeding
python seed_languages.py                # Seed basis talen (nl, en, la, el)
python seed_greek_alphabet.py           # Seed Grieks alfabet (41 entries)
python seed_latin_verbs_extended.py     # Seed 23 Latijnse werkwoorden (552 vervoegingen)
```

### Flask
```bash
python run.py                 # Start applicatie
flask run                     # Alternatief: start Flask dev server
flask db upgrade              # Run migrations
flask db migrate -m "msg"     # Create migration
```

### Frontend (Vite)
```bash
# Build production assets
docker compose run --rm vite yarn build

# Development mode (met hot reload)
docker compose run --rm vite yarn dev

# Install/update dependencies
docker compose run --rm vite yarn install
```

**Let op:** Gebruik `docker compose run` in plaats van `docker exec` omdat de Vite container
niet continu draait. De `--rm` flag verwijdert de container automatisch na gebruik.

### Development Tools
```bash
# Code quality
black .                       # Format code
isort .                       # Sort imports
flake8 .                      # Linting

# Testing
pytest                        # Run tests
pytest --cov=app              # Run tests met coverage
pytest -v                     # Verbose output
```

## Development

De applicatie gebruikt:
- **Flask** voor de webserver
- **PostgreSQL** voor data opslag (draait in Docker)
- **SQLAlchemy** als ORM
- **Jinja2** voor templates (vergelijkbaar met Twig)
- **Flask-Migrate** voor database migraties
- **Vite** voor frontend build (JavaScript/CSS bundling)
- **Tailwind CSS** voor styling
- **Font Awesome** voor iconen

### OOP Architectuur

De applicatie volgt object-georiënteerde principes:

**Repository Pattern**: Scheiding tussen business logic en data access
- `BaseRepository`: Basis CRUD operaties
- `WordListRepository`: Specifieke queries voor woordenlijsten
- `WordRepository`: Specifieke queries voor woorden

**Service Layer**: Business logic en orchestration
- `WordListService`: Beheer van lijsten en woorden
- `QuizService`: Quiz logica en score tracking

**Class-Based Views**: Gestructureerde request handling
- Elke view erft van Flask's `MethodView`
- HTTP methods (GET, POST) als class methods
- Dependency injection van services via constructor

## CI/CD

Dit project heeft een complete CI/CD pipeline via GitHub Actions:

### Workflows

**CI - Tests en Linting**
- Automatisch bij elke push en PR
- Draait code quality checks (Black, isort, Flake8)
- Voert pytest tests uit met PostgreSQL database
- Genereert coverage reports

**Docker Build en Push**
- Bouwt Docker images bij push naar `main`
- Pusht naar GitHub Container Registry
- Multi-platform support (AMD64 + ARM64)
- Automatische tagging (latest, version tags, commit SHA)

**Deployment (template)**
- Klaar voor deployment naar:
  - Google Cloud Run
  - DigitalOcean App Platform
  - AWS ECS
  - VPS via SSH

### Lokaal development tests draaien

```bash
# Installeer dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run tests met coverage
pytest --cov=app --cov-report=term-missing

# Code formatting
black .
isort .

# Linting
flake8 .
```

### Docker image van GitHub gebruiken

Na een succesvolle build op `main`:

```bash
# Pull de latest image
docker pull ghcr.io/USERNAME/magistra:latest

# Of een specifieke versie
docker pull ghcr.io/USERNAME/magistra:v1.0.0
```

Zie `.github/workflows/README.md` voor meer details over de CI/CD setup.
