from shortener.infra.settings import settings

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


engine = create_async_engine(settings.database_url)
session_factory = sessionmaker(bind=engine, class_=AsyncSession) # type: ignore


async def get_session():
    async with session_factory() as session: # type: ignore
        yield session
