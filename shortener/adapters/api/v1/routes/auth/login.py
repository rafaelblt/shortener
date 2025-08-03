from http import HTTPStatus

from shortener.adapters.api.v1.dependencies import (
    LoginUserUseCaseDependency,
    LanguageParserDependency
)
from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.adapters.api.v1.schemas.requests.auth import LoginRequest
from shortener.adapters.api.v1.schemas.responses.types import FastAPIRouteResponses
from shortener.adapters.api.v1.schemas.responses.auth import SuccessLoginResponse

from shortener.domain.user.exceptions import UserAccessDeniedError, UserNotFoundError, UserPasswordIncorrectError

from shortener.infra.translations.i18n import get_translator

from . import router


responses = FastAPIRouteResponses()
responses.set_response(
    status_code=HTTPStatus.OK,
    description="Login successfully.",
    model=SuccessLoginResponse
)
responses.set_error_response(
    status_code=HTTPStatus.UNAUTHORIZED,
    description="Invalid credentials.",
    error_code=ApiErrorCode.INVALID_CREDENTIALS
)
responses.set_error_response(
    status_code=HTTPStatus.FORBIDDEN,
    description="The User cannot be logged in.",
    error_code=ApiErrorCode.ITEM_NOT_ALLOWED
)


@router.post("/login", responses=responses.get_schema())
async def login(
    request: LoginRequest,
    use_case: LoginUserUseCaseDependency,
    language: LanguageParserDependency
): 
    email = request.get_email()
    try:
        retrieved = await use_case.execute(
            email=email, password=request.password
        )
    except (UserNotFoundError, UserPasswordIncorrectError):
        _ = get_translator(language)
        detail = _("Invalid email or password.")
        return responses.get_json_response_by_status_code(
            HTTPStatus.UNAUTHORIZED, {"detail": detail}
        )
    except UserAccessDeniedError:
        _ = get_translator(language)
        detail = _("The user cannot be logged in.")
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
