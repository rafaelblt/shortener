import pytest

from datetime import timedelta

from shortener.domain.refresh_token import RefreshToken
from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.shared.primarykey import PrimaryKey


@pytest.fixture
def active_refresh_token(normal_user):
    return RefreshToken(
        pk=PrimaryKey.create_pk_undefined(),
        token="test_token",
        user=normal_user,
        expires_at=utc_now() + timedelta(days=1)
    )


@pytest.fixture
def expired_refresh_token(normal_user):
    return RefreshToken(
        pk=PrimaryKey.create_pk_undefined(),
        token="test_token",
        user=normal_user,
        expires_at=utc_now(),
    )


@pytest.fixture
def revoked_refresh_token(normal_user):
    return RefreshToken(
        pk=PrimaryKey.create_pk_undefined(),
        token="test_token",
        user=normal_user,
        expires_at=utc_now() + timedelta(days=1),
        revoked=True
    )
