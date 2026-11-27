import os
from pathlib import Path

from dotenv import load_dotenv

# Repo root is three levels up from this file: core -> app -> backend -> root
ROOT = Path(__file__).resolve().parents[3]
load_dotenv(ROOT / ".env")


def get_database_url() -> str:
    url = os.environ["DATABASE_URL"]
    # SQLAlchemy needs the driver named in the URL
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def get_secret_key() -> str:
    return os.environ["SECRET_KEY"]
