from typing import Protocol

from shortener.domain import UserID


class AccessTokenVerifier(Protocol):
    async def verify(self, token: str) -> UserID | None:
        """
        Returns the ID of the user the token was issued to, or None when the
        token isn't valid.

        Raises:
            UnavailableError: Something the verification needs, such as the
                keys of the issuer, is unavailable.
        """
        ...


class AccessTokenCurrentUser:
    """The CurrentUser of a request: the user of its access token."""

    def __init__(self, token: str | None, verifier: AccessTokenVerifier):
        self._token = token
        self._verifier = verifier

    async def get_id(self) -> UserID | None:
        if self._token is None:
            return None
        return await self._verifier.verify(self._token)
