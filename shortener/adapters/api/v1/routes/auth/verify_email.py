from http import HTTPStatus

from fastapi.responses import JSONResponse

from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.adapters.api.v1.schemas import MessageResponse
from shortener.adapters.api.v1.dependencies import VerifyEmailUseCaseDependency, LanguageParserDependency
from shortener.adapters.api.v1.schemas.responses.error_response import ErrorResponse
from shortener.adapters.api.v1.schemas.responses.types import FastAPIRouteResponses

from shortener.domain.services.exceptions import TokenInvalidError, TokenExpiredError
from shortener.domain.user.exceptions import UserNotFoundError, UserStatusInvalidToVerifyEmailError

from shortener.infra.translations.i18n import get_translator

from . import router


responses = FastAPIRouteResponses()
responses.set_response(
    status_code=HTTPStatus.OK,
    description="User verified.",
    model=MessageResponse
)
responses.set_error_response(
    status_code=HTTPStatus.BAD_REQUEST,
    description="Invalid email verification token.",
    example_code=ApiErrorCode.INVALID_ITEM,
)
responses.set_error_response(
    status_code=HTTPStatus.GONE,
    description="Email verification token has expired.",
    example_code=ApiErrorCode.ITEM_EXPIRED,
)
responses.set_error_response(
    status_code=HTTPStatus.CONFLICT,
    description="The user does not have pending email verification.",
    example_code=ApiErrorCode.ALREADY_PROCESSED,
)


@router.get("/verify-email", responses=responses.get_responses())
async def verify_email(
    token: str,
    use_case: VerifyEmailUseCaseDependency,
    language: LanguageParserDependency
):
    _ = get_translator(language)
    try:
        await use_case.execute(token)
    except (TokenInvalidError, UserNotFoundError):
        status_code = HTTPStatus.BAD_REQUEST
        error_code = ApiErrorCode.INVALID_ITEM
        detail = _("Invalid email verification token.")
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(code=error_code, detail=detail).model_dump()
        )
    except TokenExpiredError:
        status_code = HTTPStatus.GONE
        error_code = ApiErrorCode.ITEM_EXPIRED
        detail = _("Email verification token has expired.")
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(code=error_code, detail=detail).model_dump()
        )
    except UserStatusInvalidToVerifyEmailError:
        status_code = HTTPStatus.CONFLICT
        error_code = ApiErrorCode.ALREADY_PROCESSED
        detail = _("The user does not have pending email verification.")
        return JSONResponse(
            status_code=status_code,
            content=ErrorResponse(code=error_code, detail=detail).model_dump()
        )

    return {"message": "Email successfully verified."}
