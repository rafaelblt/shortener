from uuid import UUID

from shortener.domain import UserID
from shortener.use_cases.unit_of_work import UnitOfWork


class DeleteShortURLsOfUser:

    def __init__(self, uow: UnitOfWork):
        self._uow = uow

    async def execute(self, user_id: UUID) -> None:
        """
        Raises:
            TypeError: The user_id isn't a UUID.
        """
        owner_id = UserID(user_id)
        async with self._uow.begin() as transaction:
            await transaction.shorturls.remove_by_owner(owner_id)
            await transaction.commit()
