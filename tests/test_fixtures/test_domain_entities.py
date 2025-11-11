import pytest

from shortener.domain.plan import Plan
from shortener.domain.shorturl import ShortURL
from shortener.domain.user import User

from shortener.domain.user.fields.status import UserStatus
from tests.fixtures.domain.users import UserFixture
from tests.fixtures.mocks.password_hasher import MockPasswordHasherService


def test_default_plan(default_plan: Plan):
    assert isinstance(default_plan, Plan)


def test_eco_plan(eco_plan: Plan):
    assert isinstance(eco_plan, Plan)


def test_prime_plan(prime_plan: Plan):
    assert isinstance(prime_plan, Plan)


def test_normal_shorturl(normal_shorturl: ShortURL):
    assert isinstance(normal_shorturl, ShortURL)


def test_other_shorturl(other_shorturl: ShortURL):
    assert isinstance(other_shorturl, ShortURL)


def test_old_shorturl(old_shorturl: ShortURL):
    assert isinstance(old_shorturl, ShortURL)


def test_expired_shorturl(expired_shorturl: ShortURL):
    assert isinstance(expired_shorturl, ShortURL)
    assert expired_shorturl.is_available is False


def test_biggest_shorturl(biggest_shorturl: ShortURL):
    assert isinstance(biggest_shorturl, ShortURL)


@pytest.mark.asyncio
async def test_normal_user(
    default_plan: Plan,
    normal_user: User,
    normal_shorturl: ShortURL,
    mock_password_hasher: MockPasswordHasherService
):
    assert isinstance(normal_user, UserFixture)
    assert normal_user.status == UserStatus.ACTIVE
    assert normal_user.plan == default_plan
    assert await normal_user.shorturls.get_by_slug(normal_shorturl.slug) is not None
    assert normal_user.mock_data["plain_password"]
    assert (
        mock_password_hasher.hash(normal_user.mock_data["plain_password"]) ==
        normal_user.hashed_password
    )


@pytest.mark.asyncio
async def test_super_user(
    default_plan: Plan,
    super_user: User,
    mock_password_hasher: MockPasswordHasherService
):
    assert isinstance(super_user, UserFixture)
    assert super_user.status == UserStatus.ACTIVE
    assert super_user.is_superuser
    assert super_user.plan == default_plan
    assert await super_user.shorturls.count() == 0
    assert super_user.mock_data["plain_password"]
    assert (
        mock_password_hasher.hash(super_user.mock_data["plain_password"]) ==
        super_user.hashed_password
    )


@pytest.mark.asyncio
async def test_old_user(
    default_plan: Plan,
    old_user: User,
    old_shorturl: ShortURL,
    mock_password_hasher: MockPasswordHasherService
):
    assert isinstance(old_user, UserFixture)
    assert old_user.status == UserStatus.ACTIVE
    assert old_user.plan == default_plan
    assert await old_user.shorturls.get_by_slug(old_shorturl.slug) is not None
    assert old_user.mock_data["plain_password"]
    assert (
        mock_password_hasher.hash(old_user.mock_data["plain_password"]) ==
        old_user.hashed_password
    )


@pytest.mark.asyncio
async def test_unverified_email_user(
    default_plan: Plan,
    unverified_email_user: User,
    mock_password_hasher: MockPasswordHasherService
):
    assert isinstance(unverified_email_user, UserFixture)
    assert unverified_email_user.status == UserStatus.UNVERIFIED_EMAIL
    assert unverified_email_user.plan == default_plan
    assert await unverified_email_user.shorturls.count() == 0
    assert unverified_email_user.mock_data["plain_password"]
    assert (
        mock_password_hasher.hash(unverified_email_user.mock_data["plain_password"]) ==
        unverified_email_user.hashed_password
    )


@pytest.mark.asyncio
async def test_banned_user(
    default_plan: Plan,
    banned_user: User,
    mock_password_hasher: MockPasswordHasherService
):
    assert isinstance(banned_user, UserFixture)
    assert banned_user.status == UserStatus.BANNED
    assert banned_user.plan == default_plan
    assert await banned_user.shorturls.count() == 0
    assert banned_user.mock_data["plain_password"]
    assert (
        mock_password_hasher.hash(banned_user.mock_data["plain_password"]) ==
        banned_user.hashed_password
    )


@pytest.mark.asyncio
async def test_suspended_user(
    default_plan: Plan,
    suspended_user: User,
    mock_password_hasher: MockPasswordHasherService
):
    assert isinstance(suspended_user, UserFixture)
    assert suspended_user.status == UserStatus.SUSPENDED
    assert suspended_user.plan == default_plan
    assert await suspended_user.shorturls.count() == 0
    assert suspended_user.mock_data["plain_password"]
    assert (
        mock_password_hasher.hash(suspended_user.mock_data["plain_password"]) ==
        suspended_user.hashed_password
    )


@pytest.mark.asyncio
async def test_locked_user(
    default_plan: Plan,
    locked_user: User,
    mock_password_hasher: MockPasswordHasherService
):
    assert isinstance(locked_user, UserFixture)
    assert locked_user.status == UserStatus.LOCKED
    assert locked_user.plan == default_plan
    assert await locked_user.shorturls.count() == 0
    assert locked_user.mock_data["plain_password"]
    assert (
        mock_password_hasher.hash(locked_user.mock_data["plain_password"]) ==
        locked_user.hashed_password
    )


@pytest.mark.asyncio
async def test_poor_user(
    eco_plan: Plan,
    poor_user: User,
    mock_password_hasher: MockPasswordHasherService
):
    assert isinstance(poor_user, UserFixture)
    assert poor_user.status == UserStatus.ACTIVE
    assert poor_user.plan == eco_plan
    assert await poor_user.shorturls.count() == 0
    assert poor_user.mock_data["plain_password"]
    assert (
        mock_password_hasher.hash(poor_user.mock_data["plain_password"]) ==
        poor_user.hashed_password
    )


@pytest.mark.asyncio
async def test_rich_user(
    prime_plan: Plan,
    rich_user: User,
    biggest_shorturl: ShortURL,
    mock_password_hasher: MockPasswordHasherService
):
    assert isinstance(rich_user, UserFixture)
    assert rich_user.plan == prime_plan
    assert await rich_user.shorturls.get_by_slug(biggest_shorturl.slug) is not None
    assert rich_user.mock_data["plain_password"]
    assert (
        mock_password_hasher.hash(rich_user.mock_data["plain_password"]) ==
        rich_user.hashed_password
    )
