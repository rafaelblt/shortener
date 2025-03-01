from sqlalchemy.orm import Session

from shortener.infra.db import get_db
from shortener.infra.settings import DATABASE_URL


def test_get_db():
    db = next(get_db())
    assert isinstance(db, Session)
    assert str(db.bind.url) == DATABASE_URL
