from datetime import datetime, timedelta, timezone

from shortener.domain.shared.token import Token, TokenDecoded


def test_token_attributes():
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=1)
    token = Token(
        value="abc123",
        purpose="access",
        created_at=now,
        expires_at=expires,
        extra_claims={"role": "admin"}
    )

    assert token.value == "abc123"
    assert token.purpose == "access"
    assert token.created_at == now
    assert token.expires_at == expires
    assert token.extra_claims == {"role": "admin"}


def test_token_time_remaining():
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=30)
    token = Token(
        value="xyz789",
        purpose="refresh",
        created_at=now,
        expires_at=expires
    )
    remaining = token.time_remaining
    # Should be close to 30 minutes, allow small delta for execution time
    assert timedelta(minutes=29, seconds=50) < remaining <= timedelta(minutes=30)


def test_token_extra_claims_none():
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=10)
    token = Token(
        value="no_claims",
        purpose="other",
        created_at=now,
        expires_at=expires
    )
    assert token.extra_claims is None


def test_token_decoded_typeddict():
    claims = {"foo": "bar"}
    decoded: TokenDecoded = {
        "subject": "user_id",
        "purpose": "access",
        "extra_claims": claims
    }
    assert decoded["subject"] == "user_id"
    assert decoded["purpose"] == "access"
    assert decoded["extra_claims"]