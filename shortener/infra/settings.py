import os


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///default.db")
ALEMBIC_DATABASE_URL = os.getenv("ALEMBIC_DATABASE_URL", "sqlite:///default.db")
