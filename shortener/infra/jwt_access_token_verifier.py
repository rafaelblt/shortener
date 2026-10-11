import asyncio

from collections.abc import Sequence
from typing import Any, Protocol
from uuid import UUID

import jwt

from jwt.algorithms import get_default_algorithms

from shortener.domain import UserID
from shortener.use_cases.unavailable_error import UnavailableError


class JWTAccessTokenVerifier:
    """
    Verifies access tokens that are JWTs, whose subject is the UUID of the
    user. Build it with with_key() or with_jwks(). See docs/infra.md#access-tokens
    """

    def __init__(
        self,
        keys: "_SigningKeys",
        algorithms: Sequence[str],
        issuer: str,
        audience: str,
    ):
        self._keys = keys
        self._algorithms = list(algorithms)
        self._issuer = issuer
        self._audience = audience

    @classmethod
    def with_key(
        cls, key: str, algorithms: Sequence[str], issuer: str, audience: str
    ) -> "JWTAccessTokenVerifier":
        """
        Verifies the tokens with a single key: the secret of the HMAC
        algorithms, or the public key of the others, in PEM.

        Raises:
            ValueError: An algorithm isn't supported, or the key doesn't suit
                one of the algorithms.
        """
        _check_algorithms(algorithms)
        _check_key(key, algorithms)
        return cls(_StaticKey(key), algorithms, issuer, audience)

    @classmethod
    def with_jwks(
        cls, url: str, algorithms: Sequence[str], issuer: str, audience: str
    ) -> "JWTAccessTokenVerifier":
        """
        Verifies the tokens with the keys the issuer publishes at a JWKS URL.

        Raises:
            ValueError: An algorithm isn't supported, or the URL isn't http
                or https.
        """
        _check_algorithms(algorithms)
        return cls(_JWKSKeys(url), algorithms, issuer, audience)

    async def verify(self, token: str) -> UserID | None:
        """
        Returns None when the token isn't valid.

        Raises:
            UnavailableError: The keys couldn't be fetched from the JWKS URL.
        """
        try:
            key = await self._keys.key_for(token)
            claims = jwt.decode(
                token,
                key,
                algorithms=self._algorithms,
                issuer=self._issuer,
                audience=self._audience,
                options={"require": ["exp", "sub"]},
            )
        except jwt.PyJWTError:
            return None
        return _user_id(claims["sub"])


class _SigningKeys(Protocol):
    async def key_for(self, token: str) -> Any: ...


class _StaticKey:

    def __init__(self, key: str):
        self._key = key

    async def key_for(self, token: str) -> str:
        return self._key


class _JWKSKeys:

    def __init__(self, url: str):
        try:
            self._client = jwt.PyJWKClient(url)
        except jwt.PyJWKClientError as error:
            raise ValueError(str(error)) from error

    async def key_for(self, token: str) -> jwt.PyJWK:
        # PyJWKClient fetches the keys with urllib, which blocks, so it runs
        # in a thread.
        try:
            return await asyncio.to_thread(
                self._client.get_signing_key_from_jwt, token
            )
        except jwt.PyJWKClientConnectionError as error:
            raise UnavailableError() from error


def _check_algorithms(algorithms: Sequence[str]) -> None:
    if not algorithms:
        raise ValueError("At least one algorithm is needed")
    supported = get_default_algorithms().keys() - {"none"}
    for algorithm in algorithms:
        if algorithm not in supported:
            raise ValueError(
                f"The algorithm {algorithm} isn't supported. Use one of "
                f"{', '.join(sorted(supported))}"
            )


def _check_key(key: str, algorithms: Sequence[str]) -> None:
    for name in algorithms:
        algorithm = get_default_algorithms()[name]
        try:
            prepared_key = algorithm.prepare_key(key)
        except jwt.InvalidKeyError as error:
            raise ValueError(f"The key doesn't suit {name}: {error}") from error
        if message := algorithm.check_key_length(prepared_key):
            raise ValueError(f"The key doesn't suit {name}: {message}")


def _user_id(subject: str) -> UserID | None:
    try:
        return UserID(UUID(subject))
    except ValueError:
        return None
