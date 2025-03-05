from shortener.infra.settings import DATABASE_URL

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


engine = create_async_engine(DATABASE_URL)
Session = sessionmaker(bind=engine, class_=AsyncSession)


async def get_session():
    async with Session() as session:
        yield session
