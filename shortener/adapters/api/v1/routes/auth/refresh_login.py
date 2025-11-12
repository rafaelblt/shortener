from http import HTTPStatus
from typing import Annotated

from fastapi import Body

from shortener.adapters.api.v1.dependencies import RefreshLoginUseCaseDependency
from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.adapters.api.v1.schemas.responses.types import FastAPIRouteResponses
from shortener.adapters.api.v1.schemas.responses.auth import LoginSuccessResponse

from shortener.domain.services.exceptions import TokenExpiredError, TokenInvalidError
from shortener.domain.user.exceptions import UserAccessDeniedError

from .api_router import router


responses = FastAPIRouteResponses()
responses.set_response(
    status_code=HTTPStatus.OK,
    description="Refresh successfully.",
    model=LoginSuccessResponse
)
responses.set_error_response(
    status_code=HTTPStatus.UNAUTHORIZED,
    description="Invalid refresh token.",
    error_code=ApiErrorCode.INVALID_ITEM
)
responses.set_error_response(
    status_code=HTTPStatus.FORBIDDEN,
    description="The user cannot be authenticated.",
    error_code=ApiErrorCode.ITEM_NOT_ALLOWED
)


@router.post("/refresh-login", responses=responses.get_schema())
async def refresh_login(
    refresh_token: Annotated[str, Body(..., embed=True)],
    use_case: RefreshLoginUseCaseDependency
):
    try:
        retrieved = await use_case.execute(refresh_token)
    except (TokenInvalidError, TokenExpiredError):
        detail = "The refresh token is invalid."
        return responses.get_json_response_by_status_code(
            HTTPStatus.UNAUTHORIZED, {"detail": detail}
        )
    except UserAccessDeniedError:
        detail = "The user cannot be authenticated."
        return responses.get_json_response_by_status_code(
            HTTPStatus.FORBIDDEN, {"detail": detail}
        )

    return LoginSuccessResponse.make_response(
        access_token=retrieved["access_token"],
        refresh_token=retrieved["refresh_token"],
        user=retrieved["user"]
    )
