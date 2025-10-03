import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from shortener.infra.settings import settings
from shortener.infra.db.session import get_session


@pytest.mark.asyncio
async def test_get_session():
    async for session in get_session():
        assert isinstance(session, AsyncSession)
        assert str(session.bind.url) == settings.database_url
