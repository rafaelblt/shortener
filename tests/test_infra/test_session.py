from sqlalchemy.orm import Session

from shortener.infra.settings import DATABASE_URL
from shortener.infra.db.session import get_session


def test_get_session():
    session = next(get_session())
    assert isinstance(session, Session)
    assert str(session.bind.url) == DATABASE_URL
