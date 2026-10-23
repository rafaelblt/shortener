from unittest.mock import NonCallableMagicMock, call

import pytest

from shortener.domain import UserID
from shortener.use_cases.delete_shorturls_of_user import (
    BATCH_SIZE,
    DeleteShortURLsOfUser,
)
from shortener.use_cases.unavailable_error import UnavailableError
from tests.fixtures.use_cases.doubles import call_names


# The calls of a batch on the unit of work, which records the ones of its
# transaction too: it begins a transaction, removes and commits in it, and
# leaves it.
BATCH_CALLS = [
    "begin",
    "begin().__aenter__",
    "begin().__aenter__().shorturls.remove_by_owner",
    "begin().__aenter__().commit",
    "begin().__aexit__",
]


@pytest.fixture
def delete_shorturls_of_user(uow: NonCallableMagicMock) -> DeleteShortURLsOfUser:
    return DeleteShortURLsOfUser(uow=uow)


@pytest.mark.parametrize(
    "removed_by_batch",
    [
        pytest.param([0], id="no shorturls"),
        pytest.param([3, 0], id="fewer than a batch"),
        pytest.param([BATCH_SIZE, BATCH_SIZE, 3, 0], id="more than a batch"),
    ],
)
async def test_removes_the_shorturls_in_batches_each_committed_until_one_removes_none(
    delete_shorturls_of_user: DeleteShortURLsOfUser,
    uow: NonCallableMagicMock,
    transaction: NonCallableMagicMock,
    owner_id: UserID,
    removed_by_batch: list[int],
):
    transaction.shorturls.remove_by_owner.side_effect = removed_by_batch

    await delete_shorturls_of_user.execute(owner_id.value)

    assert transaction.shorturls.remove_by_owner.await_args_list == [
        call(owner_id, BATCH_SIZE)
    ] * len(removed_by_batch)
    assert call_names(uow) == BATCH_CALLS * len(removed_by_batch)


async def test_keeps_the_batches_committed_before_one_that_fails(
    delete_shorturls_of_user: DeleteShortURLsOfUser,
    uow: NonCallableMagicMock,
    transaction: NonCallableMagicMock,
    owner_id: UserID,
):
    transaction.shorturls.remove_by_owner.side_effect = [
        BATCH_SIZE,
        UnavailableError(),
    ]

    with pytest.raises(UnavailableError):
        await delete_shorturls_of_user.execute(owner_id.value)

    assert call_names(uow) == [
        *BATCH_CALLS,
        "begin",
        "begin().__aenter__",
        "begin().__aenter__().shorturls.remove_by_owner",
        "begin().__aexit__",
    ]


async def test_raises_for_a_user_id_that_is_not_a_uuid_before_beginning_a_transaction(
    delete_shorturls_of_user: DeleteShortURLsOfUser,
    uow: NonCallableMagicMock,
    owner_id: UserID,
):
    with pytest.raises(TypeError):
        await delete_shorturls_of_user.execute(str(owner_id.value))  # type: ignore[arg-type]
    uow.begin.assert_not_called()
