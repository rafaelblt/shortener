from http import HTTPStatus
from typing import Annotated

from fastapi import Body

from shortener.adapters.api.v1.dependencies import RefreshLoginUseCaseDependency, LanguageParserDependency
from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.adapters.api.v1.schemas.responses.types import FastAPIRouteResponses
from shortener.adapters.api.v1.schemas.responses.auth import SuccessLoginResponse

from shortener.domain.refresh_token.exceptions import (
    RefreshTokenNotFoundError, RefreshTokenExpiredError, RefreshTokenRevokedError
)
from shortener.domain.user.exceptions import UserAccessDeniedError
from shortener.infra.translations.i18n import get_translator

from . import router


responses = FastAPIRouteResponses()
responses.set_response(
    status_code=HTTPStatus.OK,
    description="Refresh successfully.",
    model=SuccessLoginResponse
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
    use_case: RefreshLoginUseCaseDependency,
    lang: LanguageParserDependency
):
    _ = get_translator(lang)
    try:
        retrieved = await use_case.execute(refresh_token)
    except (RefreshTokenNotFoundError, RefreshTokenExpiredError, RefreshTokenRevokedError):
        detail = _("The refresh token is invalid.")
        return responses.get_json_response_by_status_code(
            HTTPStatus.UNAUTHORIZED, {"detail": detail}
        )
    except UserAccessDeniedError:
        detail = _("The user cannot be authenticated.")
        return responses.get_json_response_by_status_code(
            HTTPStatus.FORBIDDEN, {"detail": detail}
        )

    return SuccessLoginResponse.make_response(
        access_token=retrieved["access_token"],
        access_token_type="bearer",
        access_token_expires_in=use_case.access_token_expires_in,
        refresh_token=retrieved["refresh_token"].token,
        refresh_token_expires_in=use_case.refresh_token_expires_in,
        user=retrieved["user"]
    )
