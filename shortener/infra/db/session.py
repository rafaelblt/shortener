from shortener.infra.settings import settings

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


engine = create_async_engine(settings.database_url)
Session = sessionmaker(bind=engine, class_=AsyncSession)


async def get_session():
    async with Session() as session:
        yield session
