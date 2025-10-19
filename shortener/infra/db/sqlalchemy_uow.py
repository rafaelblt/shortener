from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from shortener.adapters.api.v1.interfaces.uow import UnitOfWork


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session

    @asynccontextmanager
    async def transaction(self):
        async with self.session.begin():
            yield self
