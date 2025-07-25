from datetime import datetime, timedelta
import pytest

from shortener.domain.refresh_token import RefreshToken
from shortener.domain.refresh_token.exceptions import RefreshTokenExpiredError, RefreshTokenRevokedError
from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user.exceptions import UserBannedError
from shortener.domain.user.fields.status import UserStatus



@pytest.fixture
def expired_token(normal_user):
    return RefreshToken(
        pk=PrimaryKey.create_pk_undefined(),
        token="test_token",
        user=normal_user,
        expires_at=utc_now(),
    )


@pytest.fixture
def revoked_token(normal_user):
    return RefreshToken(
        pk=PrimaryKey.create_pk_undefined(),
        token="test_token",
        user=normal_user,
        expires_at=utc_now() + timedelta(days=1),
        revoked=True
    )


@pytest.fixture
def active_token(normal_user):
    return RefreshToken(
        pk=PrimaryKey.create_pk_undefined(),
        token="test_token",
        user=normal_user,
        expires_at=utc_now() + timedelta(days=1)
    )


def test_method_is_revoked(active_token: RefreshToken, revoked_token: RefreshToken):
    assert active_token.is_revoked() == False
    assert revoked_token.is_revoked() == True


def test_method_is_expired(active_token: RefreshToken, expired_token: RefreshToken):
    assert active_token.is_expired() == False
    assert expired_token.is_expired() == True


def test_method_validate_with_active_token(active_token: RefreshToken):
    assert active_token.validate() == None


def test_method_validate_with_expired_token(expired_token: RefreshToken):
    with pytest.raises(RefreshTokenExpiredError):
        expired_token.validate()


def test_method_validate_with_revoked_token(revoked_token: RefreshToken):
    with pytest.raises(RefreshTokenRevokedError):
        revoked_token.validate()


def test_method_consume_with_active_token(active_token: RefreshToken):
    active_token.consume()
    assert active_token.is_revoked() == True


def test_method_consume_calls_token_validation(revoked_token: RefreshToken):
    with pytest.raises(RefreshTokenRevokedError):
        revoked_token.consume()


def test_method_consume_calls_ensure_user_can_login(active_token: RefreshToken):
    active_token._user._status = UserStatus.BANNED
    with pytest.raises(UserBannedError):
        active_token.consume()
