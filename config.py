import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env file from project root (override existing env vars)
basedir = Path(__file__).parent
load_dotenv(basedir / ".env", override=True)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "postgresql://localhost/magistra"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
