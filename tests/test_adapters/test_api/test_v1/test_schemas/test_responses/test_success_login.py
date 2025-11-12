from datetime import timedelta

from shortener.adapters.api.v1.schemas.entities.user import PublicUserSchema
from shortener.adapters.api.v1.schemas.responses.auth.login import LoginSuccessResponse

from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.shared.primarykey import PrimaryKey
from shortener.domain.shared.token import Token

from shortener.domain.user import User

from tests.utils.date_helpers import assert_datetime


def test_make_response(normal_user: User):
    normal_user._pk = PrimaryKey.create_pk_id(1)
    normal_user.plan._pk = PrimaryKey.create_pk_id(1)
    now = utc_now()

    access_token = Token(
        value="asdtgasg",
        purpose="testpurpose",
        created_at=now,
        expires_at=now + timedelta(minutes=15)
    )
    refresh_token = Token(
        value="dso0igjo8ahuaw",
        purpose="refresh",
        created_at=now,
        expires_at=now + timedelta(days=1)
    )

    expected_response = {
        "access_token": {
            "token": access_token.value,
            "token_type": "bearer",
            "expires_at": access_token.expires_at,
            "expires_seconds": access_token.time_remaining.seconds
        },
        "refresh_token": {
            "token": refresh_token.value,
            "expires_at": refresh_token.expires_at,
            "expires_seconds": refresh_token.time_remaining.seconds
        },
        "user": PublicUserSchema.from_domain(normal_user).model_dump()
    }

    retrieved = LoginSuccessResponse.make_response(
        user=normal_user,
        access_token=access_token,
        refresh_token=refresh_token
    )
    model = retrieved.model_dump()

    assert model["access_token"]["token"] == expected_response["access_token"]["token"]
    assert model["access_token"]["token_type"] == expected_response["access_token"]["token_type"]
    assert abs(model["access_token"]["expires_seconds"] - expected_response["access_token"]["expires_seconds"]) <= 5
    assert model["refresh_token"]["token"] == expected_response["refresh_token"]["token"]
    assert abs(model["refresh_token"]["expires_seconds"] - expected_response["refresh_token"]["expires_seconds"]) <= 5

    assert_datetime(
        model["access_token"]["expires_at"],
        expected_response["access_token"]["expires_at"],
        year=True, month=True, day=True, hour=True, minute=True, second=True
    )
    assert_datetime(
        model["refresh_token"]["expires_at"],
        expected_response["refresh_token"].pop("expires_at"),
        year=True, month=True, day=True, hour=True, minute=True, second=True
    )
