
import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parents[1]
DATABASE_DIR = BACKEND_DIR / "database"

DB_PATH = Path(
    os.getenv("LIBRARY_DB_PATH", str(DATABASE_DIR / "library.db"))
)


def get_connection() -> sqlite3.Connection:
    """Create a SQLite connection with row access and foreign keys enabled."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 10000")

    return conn


def initialize_database(seed: bool = False) -> None:
    """Create database tables and optionally load seed data into an empty database."""
    schema_path = DATABASE_DIR / "schema.sql"
    seed_path = DATABASE_DIR / "seed.sql"

    if not schema_path.exists():
        raise FileNotFoundError(f"Database schema not found: {schema_path}")

    conn = get_connection()

    try:
        schema_sql = schema_path.read_text(encoding="utf-8")
        conn.executescript(schema_sql)

        if seed:
            branch_count = conn.execute(
                "SELECT COUNT(*) FROM branches"
            ).fetchone()[0]

            if branch_count == 0:
                if not seed_path.exists():
                    raise FileNotFoundError(
                        f"Database seed file not found: {seed_path}"
                    )

                seed_sql = seed_path.read_text(encoding="utf-8")
                conn.executescript(seed_sql)

        conn.commit()

    except (sqlite3.Error, OSError):
        conn.rollback()
        raise

    finally:
        conn.close()

