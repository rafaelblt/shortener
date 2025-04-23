from shortener.infra.settings import DATABASE_URL
from shortener.infra.settings import ALEMBIC_DATABASE_URL


def test_database_url():
    assert isinstance(DATABASE_URL, str)


def test_alembic_database_url():
    assert isinstance(ALEMBIC_DATABASE_URL, str)
