import json

from datetime import timedelta, datetime

from shortener.adapters.api.v1.schemas.entities.user import PublicUserSchema
from shortener.adapters.api.v1.schemas.responses.auth.login import SuccessLoginResponse

from shortener.domain.shared.datetime_utils import utc_now
from shortener.domain.shared.primarykey import PrimaryKey

from shortener.domain.refresh_token.entity import RefreshToken
from shortener.domain.user.user import User

from tests.utils.date_helpers import assert_datetime


def test_make_response(normal_user: User, active_refresh_token: RefreshToken):
    normal_user._pk = PrimaryKey.create_pk_id(1)
    normal_user.plan._pk = PrimaryKey.create_pk_id(1)

    access_token = "asgfuoihaesuihousaihfvui"
    access_token_expires_in = timedelta(minutes=15)
    refresh_token_expires_in = timedelta(days=1)

    expected_response = {
        "access_token": {
            "token": access_token,
            "token_type": "bearer",
            "expires_at": utc_now() + access_token_expires_in,
            "expires_seconds": access_token_expires_in.seconds
        },
        "refresh_token": {
            "token": active_refresh_token.token,
            "expires_at": active_refresh_token.expires_at,
            "expires_seconds": refresh_token_expires_in.seconds
        },
        "user": PublicUserSchema.from_domain(normal_user).model_dump()
    }

    retrieved = SuccessLoginResponse.make_response(
        access_token=access_token,
        access_token_type="",
        access_token_expires_in=access_token_expires_in,
        refresh_token=active_refresh_token.token,
        refresh_token_expires_in=refresh_token_expires_in,
        user=normal_user
    )

    model = retrieved.model_dump()

    assert model["access_token"]["token"] == expected_response["access_token"]["token"]
    assert model["access_token"]["token_type"] == expected_response["access_token"]["token_type"]
    assert model["access_token"]["expires_seconds"] == expected_response["access_token"]["expires_seconds"]
    assert model["refresh_token"]["token"] == expected_response["refresh_token"]["token"]
    assert model["refresh_token"]["expires_seconds"] == expected_response["refresh_token"]["expires_seconds"]

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
