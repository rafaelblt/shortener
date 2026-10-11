import json
import threading
import jwt
import pytest

from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from uuid import UUID

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from jwt.algorithms import RSAAlgorithm

from shortener.domain import UserID
from shortener.infra.jwt_access_token_verifier import JWTAccessTokenVerifier
from shortener.use_cases.unavailable_error import UnavailableError


ISSUER = "https://issuer.example.com"
AUDIENCE = "shortener"
SECRET = "a-secret-long-enough-for-hs256-signatures"
KEY_ID = "key-1"
USER_UUID = UUID("0199b2c4-7a3e-7c1a-9b5e-3f2d4c6b8a10")
UNREACHABLE_JWKS_URL = "http://127.0.0.1:1/jwks.json"


def claims(**changes: Any) -> dict[str, Any]:
    """Valid claims, with the changes. A change to None leaves the claim out."""
    valid = {
        "sub": str(USER_UUID),
        "iss": ISSUER,
        "aud": AUDIENCE,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }
    return {
        name: value
        for name, value in {**valid, **changes}.items()
        if value is not None
    }


def hs256_token(**changes: Any) -> str:
    return jwt.encode(claims(**changes), SECRET, algorithm="HS256")


@pytest.fixture(scope="module")
def private_key() -> RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture(scope="module")
def public_key_pem(private_key: RSAPrivateKey) -> str:
    return (
        private_key.public_key()
        .public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        .decode()
    )


@pytest.fixture
def jwks_server(private_key: RSAPrivateKey) -> Iterator[ThreadingHTTPServer]:
    """
    Serves the public key as a JWKS at /jwks.json, or answers status, when
    it is set.
    """
    jwk = RSAAlgorithm.to_jwk(private_key.public_key(), as_dict=True)
    jwks = {"keys": [{**jwk, "kid": KEY_ID, "use": "sig", "alg": "RS256"}]}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            status = getattr(self.server, "status", HTTPStatus.OK)
            body = json.dumps(jwks).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args: Any) -> None:
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    server.server_close()


def jwks_url(server: ThreadingHTTPServer) -> str:
    return f"http://127.0.0.1:{server.server_port}/jwks.json"


@pytest.fixture
def hs256_verifier() -> JWTAccessTokenVerifier:
    return JWTAccessTokenVerifier.with_key(
        SECRET, algorithms=["HS256"], issuer=ISSUER, audience=AUDIENCE
    )


async def test_verify_returns_the_user_id_of_the_subject_of_a_valid_token(
    hs256_verifier: JWTAccessTokenVerifier,
):
    assert await hs256_verifier.verify(hs256_token()) == UserID(USER_UUID)


@pytest.mark.parametrize(
    "token",
    [
        pytest.param(
            hs256_token(exp=datetime.now(timezone.utc) - timedelta(minutes=1)),
            id="expired",
        ),
        pytest.param(hs256_token(exp=None), id="without exp"),
        pytest.param(hs256_token(iss="https://other.example.com"), id="other issuer"),
        pytest.param(hs256_token(iss=None), id="without iss"),
        pytest.param(hs256_token(aud="other"), id="other audience"),
        pytest.param(hs256_token(aud=None), id="without aud"),
        pytest.param(hs256_token(sub=None), id="without sub"),
        pytest.param(hs256_token(sub="user-1"), id="sub that isn't a UUID"),
        pytest.param(
            jwt.encode(claims(), "another-secret-long-enough-for-hs256", "HS256"),
            id="signed with another key",
        ),
        pytest.param(
            jwt.encode(claims(), SECRET + SECRET, algorithm="HS512"),
            id="algorithm that isn't allowed",
        ),
        pytest.param(jwt.encode(claims(), None, algorithm="none"), id="unsigned"),
        pytest.param("not-a-token", id="not a JWT"),
    ],
)
async def test_verify_returns_none_for_a_token_that_is_not_valid(
    hs256_verifier: JWTAccessTokenVerifier, token: str
):
    assert await hs256_verifier.verify(token) is None


async def test_verify_with_a_public_key_returns_the_user_id_of_a_valid_token(
    private_key: RSAPrivateKey, public_key_pem: str
):
    verifier = JWTAccessTokenVerifier.with_key(
        public_key_pem, algorithms=["RS256"], issuer=ISSUER, audience=AUDIENCE
    )
    token = jwt.encode(claims(), private_key, algorithm="RS256")

    assert await verifier.verify(token) == UserID(USER_UUID)


@pytest.mark.parametrize(
    "key, algorithms",
    [
        pytest.param(SECRET, [], id="no algorithm"),
        pytest.param(SECRET, ["XS256"], id="unknown algorithm"),
        pytest.param(SECRET, ["none"], id="none"),
        pytest.param("short", ["HS256"], id="secret shorter than the hash"),
        pytest.param(SECRET, ["RS256"], id="secret for an asymmetric algorithm"),
    ],
)
def test_with_key_raises_for_algorithms_or_a_key_that_cannot_verify_tokens(
    key: str, algorithms: list[str]
):
    with pytest.raises(ValueError):
        JWTAccessTokenVerifier.with_key(
            key, algorithms=algorithms, issuer=ISSUER, audience=AUDIENCE
        )


def test_with_key_raises_for_a_public_key_as_the_secret_of_an_hmac_algorithm(
    public_key_pem: str,
):
    with pytest.raises(ValueError):
        JWTAccessTokenVerifier.with_key(
            public_key_pem, algorithms=["HS256"], issuer=ISSUER, audience=AUDIENCE
        )


async def test_verify_with_jwks_returns_the_user_id_of_a_token_of_a_published_key(
    jwks_server: ThreadingHTTPServer, private_key: RSAPrivateKey
):
    verifier = JWTAccessTokenVerifier.with_jwks(
        jwks_url(jwks_server), algorithms=["RS256"], issuer=ISSUER, audience=AUDIENCE
    )
    token = jwt.encode(
        claims(), private_key, algorithm="RS256", headers={"kid": KEY_ID}
    )

    assert await verifier.verify(token) == UserID(USER_UUID)


async def test_verify_with_jwks_returns_none_for_a_key_id_that_is_not_published(
    jwks_server: ThreadingHTTPServer, private_key: RSAPrivateKey
):
    verifier = JWTAccessTokenVerifier.with_jwks(
        jwks_url(jwks_server), algorithms=["RS256"], issuer=ISSUER, audience=AUDIENCE
    )
    token = jwt.encode(
        claims(), private_key, algorithm="RS256", headers={"kid": "other-key"}
    )

    assert await verifier.verify(token) is None


async def test_verify_with_jwks_raises_unavailable_when_the_keys_cannot_be_fetched(
    private_key: RSAPrivateKey,
):
    verifier = JWTAccessTokenVerifier.with_jwks(
        UNREACHABLE_JWKS_URL, algorithms=["RS256"], issuer=ISSUER, audience=AUDIENCE
    )
    token = jwt.encode(
        claims(), private_key, algorithm="RS256", headers={"kid": KEY_ID}
    )

    with pytest.raises(UnavailableError) as raised:
        await verifier.verify(token)
    assert raised.value.__cause__ is not None


async def test_verify_with_jwks_raises_unavailable_when_the_jwks_url_answers_an_error(
    jwks_server: ThreadingHTTPServer, private_key: RSAPrivateKey
):
    jwks_server.status = HTTPStatus.SERVICE_UNAVAILABLE  # type: ignore
    verifier = JWTAccessTokenVerifier.with_jwks(
        jwks_url(jwks_server), algorithms=["RS256"], issuer=ISSUER, audience=AUDIENCE
    )
    token = jwt.encode(
        claims(), private_key, algorithm="RS256", headers={"kid": KEY_ID}
    )

    with pytest.raises(UnavailableError):
        await verifier.verify(token)


@pytest.mark.parametrize(
    "url, algorithms",
    [
        pytest.param("file:///etc/jwks.json", ["RS256"], id="URL that isn't http"),
        pytest.param("https://issuer.example.com/jwks", ["none"], id="none"),
    ],
)
def test_with_jwks_raises_for_a_url_or_algorithms_that_cannot_verify_tokens(
    url: str, algorithms: list[str]
):
    with pytest.raises(ValueError):
        JWTAccessTokenVerifier.with_jwks(
            url, algorithms=algorithms, issuer=ISSUER, audience=AUDIENCE
        )
