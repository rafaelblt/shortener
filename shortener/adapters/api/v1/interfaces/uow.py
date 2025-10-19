from abc import ABC, abstractmethod
from typing import AsyncIterator, Self
from contextlib import asynccontextmanager


class UnitOfWork(ABC):

    @asynccontextmanager
    @abstractmethod
    def transaction(self) -> AsyncIterator[Self]: ...
