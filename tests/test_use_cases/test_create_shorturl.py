import pytest

from datetime import datetime
from unittest.mock import Mock, NonCallableMagicMock

from shortener.domain import Slug, TargetURL, UserID
from shortener.shared.result import Err, Ok
from shortener.shared.validation import IssueCode, ValidationError
from shortener.use_cases.create_shorturl import (
    MAX_GENERATED_SLUG_ATTEMPTS,
    CreateShortURL,
)
from shortener.use_cases.errors import (
    FieldError,
    InvalidInputError,
    NotAuthenticatedError,
)
from shortener.use_cases.shorturl_details import ShortURLDetails
from shortener.use_cases.shorturl_repository import SlugTakenError
from tests.fixtures.shared.validation import invalid
from tests.fixtures.use_cases.doubles import call_names, record_copies


TARGET_URL = "https://example.com"


def validation_error(*codes: IssueCode) -> ValidationError:
    return invalid(*codes).error


@pytest.fixture
def create_shorturl(
    uow: NonCallableMagicMock,
    current_user: NonCallableMagicMock,
    clock: NonCallableMagicMock,
) -> CreateShortURL:
    return CreateShortURL(uow=uow, current_user=current_user, clock=clock)


@pytest.fixture
def generate(monkeypatch: pytest.MonkeyPatch) -> Mock:
    generate = Mock(return_value=Slug("Gen123"))
    monkeypatch.setattr(Slug, "generate", generate)
    return generate


async def test_returns_not_authenticated_before_checking_the_input(
    create_shorturl: CreateShortURL,
    current_user: NonCallableMagicMock,
    uow: NonCallableMagicMock,
):
    current_user.get_id.return_value = None

    result = await create_shorturl.execute(target_url="http://example.com")

    assert result == Err(NotAuthenticatedError())
    uow.begin.assert_not_called()


@pytest.mark.parametrize(
    "target_url, slug, field_errors",
    [
        pytest.param(
            "http://example.com",
            None,
            [FieldError("target_url", validation_error(IssueCode.INVALID_FORMAT))],
            id="target_url",
        ),
        pytest.param(
            TARGET_URL,
            "ab",
            [FieldError("slug", validation_error(IssueCode.TOO_SHORT))],
            id="slug",
        ),
        pytest.param(
            "http://example.com",
            "",
            [
                FieldError("target_url", validation_error(IssueCode.INVALID_FORMAT)),
                FieldError(
                    "slug",
                    validation_error(IssueCode.INVALID_FORMAT, IssueCode.TOO_SHORT),
                ),
            ],
            id="both, with an empty slug",
        ),
    ],
)
async def test_returns_invalid_input_with_a_field_error_for_each_invalid_value(
    create_shorturl: CreateShortURL,
    uow: NonCallableMagicMock,
    target_url: str,
    slug: str | None,
    field_errors: list[FieldError],
):
    result = await create_shorturl.execute(target_url=target_url, slug=slug)

    assert result == Err(InvalidInputError(tuple(field_errors)))
    uow.begin.assert_not_called()


async def test_adds_a_shorturl_of_the_user_with_the_given_values_and_then_commits(
    create_shorturl: CreateShortURL,
    transaction: NonCallableMagicMock,
    owner_id: UserID,
    now: datetime,
):
    added = record_copies(transaction.shorturls.add)

    await create_shorturl.execute(target_url=TARGET_URL, slug="my-slug")

    transaction.shorturls.add.assert_awaited_once()
    assert added[0].slug == Slug("my-slug")
    assert added[0].target_url == TargetURL(TARGET_URL)
    assert added[0].owner_id == owner_id
    assert added[0].created_at == now
    transaction.commit.assert_awaited_once()
    assert call_names(transaction) == ["shorturls.add", "commit"]


async def test_returns_the_details_of_the_added_shorturl(
    create_shorturl: CreateShortURL, transaction: NonCallableMagicMock
):
    added = record_copies(transaction.shorturls.add)

    result = await create_shorturl.execute(target_url=TARGET_URL, slug="my-slug")

    assert result == Ok(ShortURLDetails.from_entity(added[0]))


async def test_returns_slug_taken_for_a_given_slug_without_retrying_or_committing(
    create_shorturl: CreateShortURL, transaction: NonCallableMagicMock
):
    taken = Err(SlugTakenError(Slug("my-slug")))
    transaction.shorturls.add.return_value = taken

    result = await create_shorturl.execute(target_url=TARGET_URL, slug="my-slug")

    assert result == taken
    transaction.shorturls.add.assert_awaited_once()
    transaction.commit.assert_not_awaited()


async def test_adds_a_shorturl_with_a_generated_slug_when_no_slug_is_given(
    create_shorturl: CreateShortURL,
    transaction: NonCallableMagicMock,
    generate: Mock,
):
    added = record_copies(transaction.shorturls.add)

    result = await create_shorturl.execute(target_url=TARGET_URL)

    assert added[0].slug == generate.return_value
    assert result == Ok(ShortURLDetails.from_entity(added[0]))
    transaction.commit.assert_awaited_once()


async def test_tries_another_generated_slug_when_one_is_taken(
    create_shorturl: CreateShortURL,
    transaction: NonCallableMagicMock,
    generate: Mock,
):
    generate.side_effect = [Slug("Taken1"), Slug("Free12")]
    transaction.shorturls.add.side_effect = [
        Err(SlugTakenError(Slug("Taken1"))),
        Ok(None),
    ]

    result = await create_shorturl.execute(target_url=TARGET_URL)

    assert result.unwrap().slug == "Free12"
    assert call_names(transaction) == ["shorturls.add", "shorturls.add", "commit"]
    transaction.commit.assert_awaited_once()


async def test_raises_without_committing_when_every_generated_slug_is_taken(
    create_shorturl: CreateShortURL, transaction: NonCallableMagicMock
):
    transaction.shorturls.add.return_value = Err(SlugTakenError(Slug("Taken1")))

    with pytest.raises(RuntimeError):
        await create_shorturl.execute(target_url=TARGET_URL)
    assert transaction.shorturls.add.await_count == MAX_GENERATED_SLUG_ATTEMPTS
    transaction.commit.assert_not_awaited()


async def test_does_not_retry_when_adding_raises(
    create_shorturl: CreateShortURL, transaction: NonCallableMagicMock
):
    transaction.shorturls.add.side_effect = ConnectionError("the database is down")

    with pytest.raises(ConnectionError):
        await create_shorturl.execute(target_url=TARGET_URL)
    transaction.shorturls.add.assert_awaited_once()
    transaction.commit.assert_not_awaited()
