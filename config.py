import os
import re
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from project root; real env vars (e.g. from docker-compose) win
basedir = Path(__file__).parent
load_dotenv(basedir / ".env")


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    # psycopg 3 driver; rewrite legacy postgresql:// URLs (e.g. old .env files)
    SQLALCHEMY_DATABASE_URI = re.sub(
        r"^postgres(ql)?://",
        "postgresql+psycopg://",
        os.environ.get("DATABASE_URL") or "postgresql+psycopg://localhost/magistra",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
