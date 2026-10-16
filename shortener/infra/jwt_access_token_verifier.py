import asyncio

from collections.abc import Sequence
from datetime import timedelta
from typing import Any, Protocol
from uuid import UUID

import jwt

from jwt.algorithms import get_default_algorithms

from shortener.domain import UserID
from shortener.use_cases.unavailable_error import UnavailableError


class JWTAccessTokenVerifier:
    """
    Verifies access tokens that are JWTs, whose subject is the UUID of the
    user. Build it with with_key() or with_jwks().
    See docs/architecture/infra.md#access-tokens
    """

    def __init__(
        self,
        keys: "_SigningKeys",
        algorithms: Sequence[str],
        issuer: str,
        audience: str,
        leeway: timedelta,
    ):
        self._keys = keys
        self._algorithms = list(algorithms)
        self._issuer = issuer
        self._audience = audience
        self._leeway = leeway

    @classmethod
    def with_key(
        cls,
        key: str,
        algorithms: Sequence[str],
        issuer: str,
        audience: str,
        leeway: timedelta,
    ) -> "JWTAccessTokenVerifier":
        """
        Verifies the tokens with a single key: the secret of the HMAC
        algorithms, or the public key of the others, in PEM. The leeway is
        the difference allowed between the clock of the issuer and the one of
        the service.

        Raises:
            ValueError: An algorithm isn't supported, or the key doesn't suit
                one of the algorithms.
        """
        _check_algorithms(algorithms)
        _check_key(key, algorithms)
        return cls(_StaticKey(key), algorithms, issuer, audience, leeway)

    @classmethod
    def with_jwks(
        cls,
        url: str,
        algorithms: Sequence[str],
        issuer: str,
        audience: str,
        leeway: timedelta,
        timeout: timedelta,
    ) -> "JWTAccessTokenVerifier":
        """
        Verifies the tokens with the keys the issuer publishes at a JWKS URL.
        The leeway is the same as in with_key(), and the timeout is the most
        it waits for an answer of the URL.

        Raises:
            ValueError: An algorithm isn't supported, or the URL isn't http
                or https.
        """
        _check_algorithms(algorithms)
        return cls(_JWKSKeys(url, timeout), algorithms, issuer, audience, leeway)

    async def verify(self, token: str) -> UserID | None:
        """
        Returns None when the token isn't valid.

        Raises:
            UnavailableError: The keys couldn't be fetched from the JWKS URL,
                or its answer isn't a set of keys.
        """
        try:
            key = await self._keys.key_for(token)
            claims = jwt.decode(
                token,
                key,
                algorithms=self._algorithms,
                issuer=self._issuer,
                audience=self._audience,
                leeway=self._leeway,
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
    def __init__(self, url: str, timeout: timedelta):
        try:
            self._client = _JWKSClient(url, timeout=timeout.total_seconds())
        except jwt.PyJWKClientError as error:
            raise ValueError(str(error)) from error

    async def key_for(self, token: str) -> jwt.PyJWK:
        # PyJWKClient fetches the keys with urllib, which blocks, so it runs
        # in a thread.
        return await asyncio.to_thread(self._client.get_signing_key_from_jwt, token)


class _JWKSClient(jwt.PyJWKClient):
    """
    Raises UnavailableError when the keys can't be fetched, or the answer
    isn't a set of keys, so that PyJWKClientError only means that the key ID
    of the token isn't in the set. See docs/architecture/infra.md#access-tokens
    """

    def get_signing_keys(self, refresh: bool = False) -> list[jwt.PyJWK]:
        # get_signing_key() gets the keys here, also when it fetches them
        # again for a key ID that isn't in the set.
        try:
            return super().get_signing_keys(refresh)
        except (jwt.PyJWTError, ValueError) as error:
            # json raises ValueError for an answer that isn't JSON.
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
