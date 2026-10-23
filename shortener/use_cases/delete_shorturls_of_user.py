from typing import Final
from uuid import UUID

from shortener.domain import UserID
from shortener.use_cases.unit_of_work import UnitOfWork


BATCH_SIZE: Final = 1000


class DeleteShortURLsOfUser:
    """
    Deletes the short URLs in batches, each committed on its own, so a failure
    keeps the batches before it.
    See docs/architecture/use_cases.md#deleteshorturlsofuser
    """

    def __init__(self, uow: UnitOfWork, batch_size: int = BATCH_SIZE):
        self._uow = uow
        self._batch_size = batch_size

    async def execute(self, user_id: UUID) -> None:
        """
        Raises:
            TypeError: The user_id isn't a UUID.
        """
        owner_id = UserID(user_id)
        while True:
            async with self._uow.begin() as transaction:
                removed = await transaction.shorturls.remove_by_owner(
                    owner_id, self._batch_size
                )
                await transaction.commit()
            if removed == 0:
                return
