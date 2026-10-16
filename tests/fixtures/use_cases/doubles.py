import copy

from datetime import datetime
from unittest.mock import DEFAULT, AsyncMock, NonCallableMagicMock, create_autospec

import pytest

from shortener.domain import ShortURL, UserID
from shortener.shared.result import Ok
from shortener.use_cases.clock import Clock
from shortener.use_cases.current_user import CurrentUser
from shortener.use_cases.shorturl_repository import ShortURLReader, ShortURLRepository
from shortener.use_cases.unit_of_work import Transaction, UnitOfWork


# A method of a double that no test set returns a MagicMock, which a use case
# would take without any error. So each double starts with returns that are
# valid by the contract of its abstraction, and each test changes only what
# matters to it.


@pytest.fixture
def clock(now: datetime) -> NonCallableMagicMock:
    clock = create_autospec(Clock, instance=True)
    clock.now.return_value = now
    return clock


@pytest.fixture
def current_user(owner_id: UserID) -> NonCallableMagicMock:
    current_user = create_autospec(CurrentUser, instance=True)
    current_user.get_id.return_value = owner_id
    return current_user


@pytest.fixture
def shorturl_reader() -> NonCallableMagicMock:
    return _with_empty_reads(create_autospec(ShortURLReader, instance=True))


@pytest.fixture
def transaction() -> NonCallableMagicMock:
    shorturls = _with_empty_reads(create_autospec(ShortURLRepository, instance=True))
    shorturls.add.return_value = Ok(None)
    shorturls.save.return_value = Ok(None)
    shorturls.remove.return_value = None
    shorturls.remove_by_owner.return_value = None

    transaction = create_autospec(Transaction, instance=True)
    # create_autospec makes shorturls, a property, a MagicMock without the
    # methods of ShortURLRepository. Assigned here, it is a double of the
    # repository, whose calls are recorded with the transaction's.
    transaction.shorturls = shorturls
    transaction.commit.return_value = None
    return transaction


@pytest.fixture
def uow(transaction: NonCallableMagicMock) -> NonCallableMagicMock:
    uow = create_autospec(UnitOfWork, instance=True)
    # begin() returns a MagicMock, which is also an async context manager.
    uow.begin.return_value.__aenter__.return_value = transaction
    return uow


def record_copies(method: AsyncMock) -> list[ShortURL]:
    """
    Makes the double of add() or save() keep a deep copy of the short URL
    each time it is awaited, and returns the list where the copies go. A
    double keeps the argument itself, so a short URL changed after the await
    would look as if it had been awaited already changed. The double still
    returns its return_value.
    """
    copies: list[ShortURL] = []

    def record(shorturl: ShortURL) -> object:
        copies.append(copy.deepcopy(shorturl))
        return DEFAULT

    method.side_effect = record
    return copies


def call_names(double: NonCallableMagicMock) -> list[str]:
    """
    The names of the methods called on the double, in order, with the
    attribute they belong to, such as "shorturls.save". Unlike comparing
    mock_calls, it doesn't depend on how the arguments were passed.
    """
    return [name for name, _args, _kwargs in double.mock_calls]


def _with_empty_reads(shorturls: NonCallableMagicMock) -> NonCallableMagicMock:
    shorturls.get_by_id.return_value = None
    shorturls.get_by_slug.return_value = None
    shorturls.list_by_owner.return_value = []
    return shorturls
