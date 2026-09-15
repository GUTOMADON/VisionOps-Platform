"""Create database tables for local development without running psql.

Production deployments should apply database/init.sql directly (it is also
what the Docker Postgres image runs automatically on first start). This
script is a convenience for developers running the backend against a fresh
local Postgres instance or SQLite file without the psql client installed.

Usage:
    python scripts/init_db.py
"""

from app.db.models import Base  # noqa: F401  (import registers all models on Base.metadata)
from app.db.session import engine


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


if __name__ == "__main__":
    main()
