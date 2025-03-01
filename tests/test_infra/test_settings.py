from shortener.infra.settings import DATABASE_URL


def test_database_url():
    assert isinstance(DATABASE_URL, str)
