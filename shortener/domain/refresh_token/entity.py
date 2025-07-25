from datetime import datetime

from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.user.user import User

from shortener.domain.refresh_token.exceptions import (
    RefreshTokenExpiredError, RefreshTokenRevokedError
)


class RefreshToken:
    def __init__(
        self,
        pk: PrimaryKey,
        token: str,
        user: User,
        expires_at: datetime,
        created_at: datetime = utc_now(),
        revoked: bool = False,
    ):
        self._pk = pk
        self._token = token
        self._user = user
        self._revoked = revoked
        self._created_at = created_at
        self._expires_at = expires_at
    
    @property
    def user(self):
        return self._user
    
    @property
    def token(self):
        return self._token
    
    def consume(self):
        """
        Raises:
            RefreshTokenRevokedError: The token is revoked.
            RefreshTokenExpiredError: The token is expired.
            UserEmailNotVerifiedError: The user has not been verified.
            UserSuspendedError: The user has been suspended.
            UserLockedError: The user has been locked.
            UserBannedError: The user has been banned.
        """
        self.validate()
        self.user.ensure_can_login()
        self.revoke()
    
    def validate(self):
        """
        Raises:
            RefreshTokenRevokedError: The token is revoked.
            RefreshTokenExpiredError: The token is expired.
        """
        if self.is_revoked():
            raise RefreshTokenRevokedError()
        if self.is_expired():
            raise RefreshTokenExpiredError()

    def is_revoked(self):
        return self._revoked
    
    def is_expired(self):
        return self._expires_at < utc_now()
    
    def revoke(self):
        self._revoked = True
