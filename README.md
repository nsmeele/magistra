# Magistra

Magistra tests you on your vocab, no messing about. Bung a list of Latin verbs, Greek letters or English phrases in, then keep typing translations till they're properly drilled in. Get one wrong and it comes back round in the same go, and again later in a dedicated practice round, so there's no wriggling out of it. Every quiz you finish earns you XP, and a daily streak keeps you from skiving off.

Under the bonnet it's a Flask app on PostgreSQL, with server-rendered Jinja templates and Tailwind CSS.

Everything runs in Docker, so you don't need Python or Node on your machine. Just Docker, sorted.

---

## Getting it running

**1. Install the frontend packages and build the CSS and JavaScript.**

```bash
docker compose run --rm vite
docker compose run --rm vite yarn build
```

**2. Fire up the app.** This builds the image and starts Postgres along with it:

```bash
docker compose up -d app
```

**3. Create the tables.**

```bash
docker compose run --rm app flask --app run db upgrade
```

**4. Head over to <http://localhost:5001>.** Code changes reload automatically, because the project folder is mounted into the container.

An empty app's a bit of a damp squib. If you want to crack on with practising straight away, chuck some content in:

```bash
docker compose run --rm app python seed_languages.py            # run this one first: the others need the languages
docker compose run --rm app python seed_achievements.py
docker compose run --rm app python seed_greek_alphabet.py
docker compose run --rm app python seed_latin_verbs_extended.py
```

Job's a good 'un.

The database settings are already in `docker-compose.yml`, so you don't need a `.env`. If you do have one, environment variables from Docker take priority over it.

---

## Tinkering with the code

| I want to…                               | Command                                                                  |
| ---------------------------------------- | ------------------------------------------------------------------------ |
| run the tests                            | `docker compose run --rm app pytest`                                     |
| see what the tests don't cover           | `docker compose run --rm app pytest --cov=app --cov-report=term-missing` |
| format and lint the code                 | `docker compose run --rm app sh -c "black . && isort . && flake8 ."`     |
| create a migration for a model change    | `docker compose run --rm app flask --app run db migrate -m "what's changing"` |
| apply that migration                     | `docker compose run --rm app flask --app run db upgrade`                 |
| rebuild CSS and JS as I go               | `docker compose run --rm vite yarn build --watch`                        |
| see what the app is moaning about        | `docker compose logs -f app`                                             |
| pack it all in for the day               | `docker compose down`                                                    |

Worth knowing, so you don't come a cropper:

- **The tests don't need the database.** `tests/conftest.py` runs them on in-memory SQLite. Easy peasy.
- **Give a migration a once-over before you apply it.** Alembic doesn't catch every change, such as renamed columns or altered enum values, and a dodgy migration's a right faff to undo.
- **`yarn dev` won't work here.** Flask finds the assets through `static/dist/.vite/manifest.json` and never talks to Vite's dev server. Use `build --watch` and refresh the page instead.
- **Changed `requirements*.txt`?** Rebuild the image with `docker compose build app`.
- **The database says it's migrated but the tables are missing?** Reset the migration marker and run the migrations again: `docker compose run --rm app sh -c "flask --app run db stamp base && flask --app run db upgrade"`.
- **Using VS Code?** Install the *Dev Containers* extension and pick **Reopen in Container**. `.devcontainer/devcontainer.json` hooks the editor up to the `app` service, so autocomplete, the debugger and the tests use the container's Python, and Black, isort and flake8 come pre-installed. No local venv needed.
- **Using PyCharm?** You'll need PyCharm Pro for this one: set the project interpreter to *Docker Compose*, service `app`. The free version can't use Docker interpreters.

### Where everything lives

Say you answer a quiz question. `app/routes.py` maps the URL to a view in `app/views.py`. That view passes the answer to `QuizService` in `app/services.py`. The service checks the answer, saves it through `app/repositories.py`, then updates your XP and streak through `UserStatsService`. That last step can unlock an achievement through `AchievementService`.

So new logic goes in a service, not a view. For new queries, add a repository method.

Also handy:

- `app/models.py` holds all the tables, from lists and entries to quiz sessions and the gamification bits.
- `app/constants.py` holds the entry types (word, sentence, letter, verb) and their Dutch labels.
- `templates/` has one template per page. They all extend `base.html`.
- `assets/` holds the frontend source files. Vite builds them into `static/dist/`, which isn't in git.

---

## Shipping it

The `Dockerfile` has a `dev` stage for local work and a `production` stage that's built by default. The production stage builds the frontend in a Node stage first and bakes everything into the image:

```bash
docker build -t magistra .
docker run -p 5001:5001 -e SECRET_KEY=… -e DATABASE_URL=… magistra
```

GitHub Actions does the graft for you:

- `ci.yml` lints and tests every push and PR to `main` and `develop`.
- `docker.yml` publishes the production image to GitHub Container Registry on every push to `main`, for amd64 and arm64.
- `deploy.yml.example` is a starting point for deployment. Copy it to `deploy.yml`; that file's in `.gitignore`.

Cheers!
