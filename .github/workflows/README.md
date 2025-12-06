# GitHub Actions Workflows

Dit project gebruikt GitHub Actions voor CI/CD.

## Workflows

### 1. CI - Tests and Linting (`ci.yml`)
**Triggers:** Push en PR naar `main` of `develop` branches

**Wat het doet:**
- Lint code met Black, isort, en Flake8
- Draait pytest tests met PostgreSQL service
- Genereert coverage reports

**Status Badge:**
```markdown
![CI](https://github.com/USERNAME/magistra/workflows/CI%20-%20Tests%20and%20Linting/badge.svg)
```

### 2. Docker Build and Push (`docker.yml`)
**Triggers:** Push naar `main`, tags, en PRs

**Wat het doet:**
- Bouwt Docker image met multi-platform support (AMD64 + ARM64)
- Pusht naar GitHub Container Registry (ghcr.io)
- Tagging strategie:
  - `latest` voor main branch
  - `v1.2.3` voor version tags
  - `main-abc123` voor commit SHA
  - `pr-42` voor pull requests

**Image gebruiken:**
```bash
docker pull ghcr.io/USERNAME/magistra:latest
```

### 3. Deploy (`deploy.yml.example`)
**Template voor deployment** - Configureer voor jouw platform:
- Google Cloud Run
- DigitalOcean App Platform
- AWS ECS
- VPS via SSH

**Activeren:**
1. Hernoem `deploy.yml.example` naar `deploy.yml`
2. Kies een deployment optie (zet `if: true`)
3. Configureer de benodigde secrets in GitHub

## Secrets Configuratie

Ga naar GitHub Repository → Settings → Secrets and variables → Actions

### Voor alle workflows:
- `GITHUB_TOKEN` - Automatisch beschikbaar, geen configuratie nodig

### Voor deployment (afhankelijk van platform):

**Google Cloud Run:**
- `GCP_CREDENTIALS` - Service account JSON
- `SECRET_KEY` - Flask secret key

**DigitalOcean:**
- `DIGITALOCEAN_ACCESS_TOKEN` - API token
- `APP_ID` - App Platform ID

**AWS ECS:**
- `AWS_ACCESS_KEY_ID` - AWS credentials
- `AWS_SECRET_ACCESS_KEY` - AWS credentials

**VPS:**
- `VPS_HOST` - Server IP/hostname
- `VPS_USERNAME` - SSH username
- `VPS_SSH_KEY` - Private SSH key

## Lokaal testen

Test de Docker build lokaal:
```bash
docker build -t magistra:test .
docker run -p 5000:5000 magistra:test
```

Run tests lokaal:
```bash
pip install pytest pytest-cov pytest-flask
pytest --cov=app
```

## Deployment Strategie

**Aanbevolen flow:**
1. Feature branch → PR → CI checks
2. Merge naar `main` → Docker build + push
3. Auto-deploy naar production (optioneel)

**Met version tags:**
```bash
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```
Dit triggert Docker build met tag `v1.0.0` en `1.0`