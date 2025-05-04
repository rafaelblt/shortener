import os


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///default.db")
ALEMBIC_DATABASE_URL = os.getenv("ALEMBIC_DATABASE_URL", "sqlite:///default.db")

JWT_AUTH_SECRET_KEY = os.getenv("JWT_AUTH_SECRET_KEY", "ko@34i!1@!3$!345Aba71")
JWT_AUTH_TOKEN_EXPIRES_MINUTES = os.getenv("JWT_AUTH_TOKEN_EXPIRES_MINUTES", 60)
