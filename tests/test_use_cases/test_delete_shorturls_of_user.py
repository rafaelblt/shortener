from unittest.mock import NonCallableMagicMock

import pytest

from shortener.domain import UserID
from shortener.use_cases.delete_shorturls_of_user import DeleteShortURLsOfUser
from tests.fixtures.use_cases.doubles import call_names


@pytest.fixture
def delete_shorturls_of_user(uow: NonCallableMagicMock) -> DeleteShortURLsOfUser:
    return DeleteShortURLsOfUser(uow=uow)


async def test_removes_the_shorturls_of_the_user_through_the_transaction_and_then_commits(
    delete_shorturls_of_user: DeleteShortURLsOfUser,
    transaction: NonCallableMagicMock,
    owner_id: UserID,
):
    await delete_shorturls_of_user.execute(owner_id.value)

    transaction.shorturls.remove_by_owner.assert_awaited_once_with(owner_id)
    transaction.commit.assert_awaited_once()
    assert call_names(transaction) == ["shorturls.remove_by_owner", "commit"]


async def test_raises_for_a_user_id_that_is_not_a_uuid_before_beginning_a_transaction(
    delete_shorturls_of_user: DeleteShortURLsOfUser,
    uow: NonCallableMagicMock,
    owner_id: UserID,
):
    with pytest.raises(TypeError):
        await delete_shorturls_of_user.execute(str(owner_id.value))  # type: ignore
    uow.begin.assert_not_called()
