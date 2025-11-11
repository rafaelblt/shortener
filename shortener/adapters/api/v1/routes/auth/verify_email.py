from http import HTTPStatus

from fastapi.responses import JSONResponse
from fastapi import Response

from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.adapters.api.v1.schemas import MessageResponse
from shortener.adapters.api.v1.dependencies import VerifyEmailUseCaseDependency, LanguageParserDependency
from shortener.adapters.api.v1.schemas.responses.error_response import ErrorResponse
from shortener.adapters.api.v1.schemas.responses.types import FastAPIRouteResponses

from shortener.domain.services.exceptions import TokenInvalidError, TokenExpiredError
from shortener.domain.user.exceptions import UserNotFoundError, UserStatusInvalidToVerifyEmailError

from shortener.infra.translations.i18n import get_translator

from .api_router import router


responses = FastAPIRouteResponses()
responses.set_response(
    status_code=HTTPStatus.OK,
    description="User verified.",
    model=MessageResponse
)
responses.set_error_response(
    status_code=HTTPStatus.BAD_REQUEST,
    description="Invalid email verification token.",
    error_code=ApiErrorCode.INVALID_ITEM,
)
responses.set_error_response(
    status_code=HTTPStatus.GONE,
    description="Email verification token has expired.",
    error_code=ApiErrorCode.ITEM_EXPIRED,
)
responses.set_error_response(
    status_code=HTTPStatus.CONFLICT,
    description="The user does not have pending email verification.",
    error_code=ApiErrorCode.ALREADY_PROCESSED,
)


@router.get("/verify-email", responses=responses.get_schema())
async def verify_email(
    token: str,
    use_case: VerifyEmailUseCaseDependency,
    language: LanguageParserDependency
):
    _ = get_translator(language)
    try:
        await use_case.execute(token)
    except (TokenInvalidError, UserNotFoundError):
        detail = _("Invalid email verification token.")
        return responses.get_json_response_by_status_code(
            HTTPStatus.BAD_REQUEST, {"detail": detail}
        )
    except TokenExpiredError:
        detail = _("Email verification token has expired.")
        return responses.get_json_response_by_status_code(
            HTTPStatus.GONE, {"detail": detail}
        )
    except UserStatusInvalidToVerifyEmailError:
        detail = _("The user does not have pending email verification.")
        return responses.get_json_response_by_status_code(
            HTTPStatus.CONFLICT, {"detail": detail}
        )

    return {"message": "Email successfully verified."}
