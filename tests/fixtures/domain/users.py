import pytest
import pytest_asyncio

from typing import TypedDict
from datetime import datetime, timezone

from shortener.domain.plan import Plan
from shortener.domain.shorturl.shorturl import ShortURL
from shortener.domain.user import User
from shortener.domain.user.fields import *

from tests.fixtures import MockPasswordHasherService


class UserMockData(TypedDict):
    plain_password: PlainPassword    


class UserFixture(User):
    mock_data: UserMockData

    def _init_mock_data(self, plain_password: PlainPassword):
        self.mock_data = UserMockData(
            plain_password=plain_password
        )


@pytest_asyncio.fixture
async def normal_user(
    default_plan: Plan,
    normal_shorturl: ShortURL,
    mock_password_hasher: MockPasswordHasherService
):
    password = PlainPassword("_N0rm4lP4ssw0rd$$$$")
    user = UserFixture(
        email=Email("normal.user@gmail.com"),
        name=Name("Normal User Example"),
        hashed_password=mock_password_hasher.hash(password),
        plan=default_plan
    )
    await user.add_shorturl(normal_shorturl)
    user._init_mock_data(plain_password=password)
    return user


@pytest_asyncio.fixture
async def super_user(
    default_plan: Plan,
    mock_password_hasher: MockPasswordHasherService
):
    password = PlainPassword("my_SUPER_password_123_@")
    user = UserFixture(
        email=Email("i-love-superman@super.io"),
        name=Name("I Am Superman"),
        hashed_password=mock_password_hasher.hash(password),
        plan=default_plan
    )
    user._init_mock_data(plain_password=password)
    return user


@pytest_asyncio.fixture
async def old_user(
    default_plan: Plan,
    old_shorturl: ShortURL,
    mock_password_hasher: MockPasswordHasherService
):
    password = PlainPassword("IAMold_019_@!)")
    user = UserFixture(
        email=Email("wiseoldman@outlook.com"),
        name=Name("Richard Park"),
        hashed_password=mock_password_hasher.hash(password),
        plan=default_plan,
        created_at=datetime(year=2000, month=1, day=1, tzinfo=timezone.utc)
    )
    await user.add_shorturl(old_shorturl)
    user._init_mock_data(plain_password=password)
    return user


@pytest.fixture
def unverified_email_user(default_plan: Plan, mock_password_hasher: MockPasswordHasherService):
    password = PlainPassword("_N0rm4lP4ssw0rd$$$$")
    user = UserFixture(
        email=Email("i-was-not-checked@gmail.com"),
        name=Name("Unverified Person"),
        hashed_password=mock_password_hasher.hash(password),
        plan=default_plan,
        status=UserStatus.UNVERIFIED_EMAIL
    )
    user._init_mock_data(plain_password=password)
    return user


@pytest.fixture
def banned_user(default_plan: Plan, mock_password_hasher: MockPasswordHasherService):
    password = PlainPassword("DANGER_!!hacking!!!!!!_54145262543")
    user = UserFixture(
        email=Email("i-was-banned@gmail.com"),
        name=Name("Banned Person"),
        hashed_password=mock_password_hasher.hash(password),
        plan=default_plan,
        status=UserStatus.BANNED
    )
    user._init_mock_data(plain_password=password)
    return user


@pytest.fixture
def suspended_user(default_plan: Plan, mock_password_hasher: MockPasswordHasherService):
    password = PlainPassword("sus 4mongUs &")
    user = UserFixture(
        email=Email("i-was-suspended@gmail.com"),
        name=Name("Suspended Person"),
        hashed_password=mock_password_hasher.hash(password),
        plan=default_plan,
        status=UserStatus.SUSPENDED
    )
    user._init_mock_data(plain_password=password)
    return user


@pytest.fixture
def locked_user(default_plan: Plan, mock_password_hasher: MockPasswordHasherService):
    password = PlainPassword("DANGER_!!hacking!!!!!!_54145262543")
    user = UserFixture(
        email=Email("i-was-locked@gmail.com"),
        name=Name("Locked Person"),
        hashed_password=mock_password_hasher.hash(password),
        plan=default_plan,
        status=UserStatus.LOCKED
    )
    user._init_mock_data(plain_password=password)
    return user


@pytest.fixture
def poor_user(eco_plan: Plan, mock_password_hasher: MockPasswordHasherService):
    password = PlainPassword("ch34p3stP#D")
    user = UserFixture(
        email=Email("cheap_email@gmail.com"),
        name=Name("Poor Person"),
        hashed_password=mock_password_hasher.hash(password),
        plan=eco_plan,
        status=UserStatus.ACTIVE
    )
    user._init_mock_data(plain_password=password)
    return user


@pytest_asyncio.fixture
async def rich_user(
    prime_plan,
    biggest_shorturl,
    mock_password_hasher: MockPasswordHasherService
):
    password = PlainPassword("H!b123i4uf6!*oP!ç1234")
    user = UserFixture(
        email=Email("fortune@gmail.com"),
        name=Name("Rich Person"),
        hashed_password=mock_password_hasher.hash(password),
        plan=prime_plan,
        status=UserStatus.ACTIVE
    )
    await user.add_shorturl(biggest_shorturl)
    user._init_mock_data(plain_password=password)
    return user
