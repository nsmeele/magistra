# Magistra

Een woordjes overhoring applicatie gebouwd met Flask en PostgreSQL.

## Features

- Maak woordenlijsten met bron- en doeltaal
- Voeg woorden toe aan lijsten
- Oefen met een interactieve quiz
- Houd scores bij (goed/fout per woord)

## Setup Instructies

### Optie 1: Docker (Aanbevolen - Eenvoudigste)

Met Docker hoef je geen Python, PostgreSQL of dependencies handmatig te installeren:

```bash
# Start de applicatie (eerste keer duurt iets langer door image build)
./start.sh

# Ga naar http://localhost:5000 in je browser
```

**Andere handige commando's:**
```bash
./stop.sh      # Stop de applicatie
./restart.sh   # Herstart de applicatie
./logs.sh      # Bekijk logs
```

**Vereisten:**
- Docker Desktop geïnstalleerd ([download hier](https://www.docker.com/products/docker-desktop))

---

### Optie 2: Handmatige Setup

#### 1. Python Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Op Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. PostgreSQL Database

Installeer PostgreSQL als je het nog niet hebt:

**macOS (met Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download van https://www.postgresql.org/download/windows/

### 3. Database Aanmaken

```bash
# Start psql als postgres gebruiker
psql postgres

# In psql console:
CREATE DATABASE magistra;
CREATE USER magistra_user WITH PASSWORD 'jouw_wachtwoord';
GRANT ALL PRIVILEGES ON DATABASE magistra TO magistra_user;
\q
```

### 4. Environment Configuratie

Kopieer `.env.example` naar `.env` en pas aan:

```bash
cp .env.example .env
```

Edit `.env` met je database credentials:
```
SECRET_KEY=een-random-secret-key
DATABASE_URL=postgresql://magistra_user:jouw_wachtwoord@localhost/magistra
```

### 5. Database Migraties

```bash
# Initialiseer migraties
flask db init

# Maak eerste migratie
flask db migrate -m "Initial migration"

# Voer migratie uit
flask db upgrade
```

### 6. Start de Applicatie

```bash
python run.py
```

Ga naar http://localhost:5000 in je browser.

## Project Structuur

De applicatie volgt een volledige OOP architectuur met separation of concerns:

```
magistra/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models (WordList, Word)
│   ├── repositories.py      # Data access layer (Repository pattern)
│   ├── services.py          # Business logic layer (Services)
│   ├── views.py             # Presentation layer (Class-based views)
│   ├── routes.py            # URL routing configuration
│   └── templates/           # Jinja2 templates
│       ├── base.html
│       ├── index.html
│       ├── new_list.html
│       ├── list_detail.html
│       ├── quiz.html
│       └── quiz_complete.html
├── static/
│   └── style.css            # CSS styling
├── config.py                # Configuratie
├── run.py                   # Entry point
└── requirements.txt         # Dependencies
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

## Development

De applicatie gebruikt:
- Flask voor de webserver
- PostgreSQL voor data opslag
- SQLAlchemy als ORM
- Jinja2 voor templates
- Flask-Migrate voor database migraties

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
