from datetime import datetime
from unittest.mock import NonCallableMagicMock

import pytest

from shortener.domain import ShortURL, ShortURLID, Slug, TargetURL, UserID
from shortener.shared.result import Err, Ok
from shortener.shared.validation import IssueCode, ValidationError
from shortener.use_cases.errors import (
    FieldError,
    InvalidInputError,
    NotAuthenticatedError,
    NothingToUpdateError,
    ShortURLNotFoundError,
)
from shortener.use_cases.shorturl_details import ShortURLDetails
from shortener.use_cases.shorturl_repository import SlugTakenError
from shortener.use_cases.update_shorturl import UpdateShortURL
from tests.fixtures.shared.validation import invalid
from tests.fixtures.use_cases.doubles import call_names, record_copies


OLD_TARGET_URL = "https://old.example.com"
OLD_SLUG = "old-slug"
NEW_TARGET_URL = "https://new.example.com"
NEW_SLUG = "new-slug"


def validation_error(*codes: IssueCode) -> ValidationError:
    return invalid(*codes).error


@pytest.fixture
def update_shorturl(
    uow: NonCallableMagicMock, current_user: NonCallableMagicMock
) -> UpdateShortURL:
    return UpdateShortURL(uow=uow, current_user=current_user)


@pytest.fixture
def shorturl(
    transaction: NonCallableMagicMock, owner_id: UserID, now: datetime
) -> ShortURL:
    shorturl = ShortURL.create(
        slug=Slug(OLD_SLUG),
        target_url=TargetURL(OLD_TARGET_URL),
        owner_id=owner_id,
        now=now,
    )
    transaction.shorturls.get_by_id.return_value = shorturl
    return shorturl


async def test_returns_not_authenticated_before_checking_the_input(
    update_shorturl: UpdateShortURL,
    current_user: NonCallableMagicMock,
    uow: NonCallableMagicMock,
    shorturl: ShortURL,
):
    current_user.get_id.return_value = None

    result = await update_shorturl.execute(shorturl.id.value)

    assert result == Err(NotAuthenticatedError())
    uow.begin.assert_not_called()


async def test_returns_nothing_to_update_without_any_value(
    update_shorturl: UpdateShortURL, uow: NonCallableMagicMock, shorturl: ShortURL
):
    result = await update_shorturl.execute(shorturl.id.value)

    assert result == Err(NothingToUpdateError())
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
            NEW_TARGET_URL,
            "ab",
            [FieldError("slug", validation_error(IssueCode.TOO_SHORT))],
            id="slug, with a valid target_url",
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
    update_shorturl: UpdateShortURL,
    uow: NonCallableMagicMock,
    shorturl: ShortURL,
    target_url: str | None,
    slug: str | None,
    field_errors: list[FieldError],
):
    result = await update_shorturl.execute(
        shorturl.id.value, target_url=target_url, slug=slug
    )

    assert result == Err(InvalidInputError(tuple(field_errors)))
    uow.begin.assert_not_called()


async def test_reads_the_shorturl_by_id_through_the_transaction(
    update_shorturl: UpdateShortURL,
    transaction: NonCallableMagicMock,
    shorturl: ShortURL,
):
    await update_shorturl.execute(shorturl.id.value, slug=NEW_SLUG)
    transaction.shorturls.get_by_id.assert_awaited_once_with(
        ShortURLID(shorturl.id.value)
    )


async def test_raises_for_an_id_that_is_not_a_uuid_before_beginning_a_transaction(
    update_shorturl: UpdateShortURL, uow: NonCallableMagicMock, shorturl: ShortURL
):
    not_a_uuid = str(shorturl.id.value)
    with pytest.raises(TypeError):
        await update_shorturl.execute(not_a_uuid, slug=NEW_SLUG)  # type: ignore[arg-type]
    uow.begin.assert_not_called()


async def test_returns_not_found_without_saving_when_no_shorturl_has_the_id(
    update_shorturl: UpdateShortURL,
    transaction: NonCallableMagicMock,
    normal_shorturl: ShortURL,
):
    result = await update_shorturl.execute(normal_shorturl.id.value, slug=NEW_SLUG)

    assert result == Err(ShortURLNotFoundError())
    transaction.shorturls.save.assert_not_awaited()
    transaction.commit.assert_not_awaited()


async def test_returns_not_found_without_saving_for_a_shorturl_of_another_user(
    update_shorturl: UpdateShortURL,
    current_user: NonCallableMagicMock,
    transaction: NonCallableMagicMock,
    shorturl: ShortURL,
    other_user_id: UserID,
):
    current_user.get_id.return_value = other_user_id

    result = await update_shorturl.execute(shorturl.id.value, slug=NEW_SLUG)

    assert result == Err(ShortURLNotFoundError())
    transaction.shorturls.save.assert_not_awaited()
    transaction.commit.assert_not_awaited()


@pytest.mark.parametrize(
    "target_url, slug, saved_target_url, saved_slug",
    [
        pytest.param(NEW_TARGET_URL, None, NEW_TARGET_URL, OLD_SLUG, id="target_url"),
        pytest.param(None, NEW_SLUG, OLD_TARGET_URL, NEW_SLUG, id="slug"),
        pytest.param(NEW_TARGET_URL, NEW_SLUG, NEW_TARGET_URL, NEW_SLUG, id="both"),
    ],
)
async def test_saves_the_given_values_keeping_the_others_and_then_commits(
    update_shorturl: UpdateShortURL,
    transaction: NonCallableMagicMock,
    shorturl: ShortURL,
    target_url: str | None,
    slug: str | None,
    saved_target_url: str,
    saved_slug: str,
):
    saved = record_copies(transaction.shorturls.save)

    await update_shorturl.execute(shorturl.id.value, target_url=target_url, slug=slug)

    transaction.shorturls.save.assert_awaited_once_with(shorturl)
    assert (saved[0].target_url, saved[0].slug) == (saved_target_url, saved_slug)
    transaction.commit.assert_awaited_once()
    assert call_names(transaction) == [
        "shorturls.get_by_id",
        "shorturls.save",
        "commit",
    ]


async def test_returns_the_details_of_the_updated_shorturl(
    update_shorturl: UpdateShortURL,
    transaction: NonCallableMagicMock,
    shorturl: ShortURL,
):
    saved = record_copies(transaction.shorturls.save)

    result = await update_shorturl.execute(
        shorturl.id.value, target_url=NEW_TARGET_URL, slug=NEW_SLUG
    )

    assert result == Ok(ShortURLDetails.from_entity(saved[0]))


async def test_returns_slug_taken_without_committing(
    update_shorturl: UpdateShortURL,
    transaction: NonCallableMagicMock,
    shorturl: ShortURL,
):
    taken = Err(SlugTakenError(Slug(NEW_SLUG)))
    transaction.shorturls.save.return_value = taken

    result = await update_shorturl.execute(shorturl.id.value, slug=NEW_SLUG)

    assert result == taken
    transaction.commit.assert_not_awaited()
