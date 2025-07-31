from http import HTTPStatus

from fastapi.responses import JSONResponse

from shortener.adapters.api.v1.dependencies import (
    LoginUserUseCaseDependency,
    LanguageParserDependency
)
from shortener.adapters.api.v1.schemas.requests.auth import LoginRequest
from shortener.adapters.api.v1.schemas.responses import ErrorResponse
from shortener.adapters.api.v1.schemas.responses.types import FastAPIRouteResponses
from shortener.adapters.api.v1.schemas.responses.auth.login import SuccessLoginResponse

from shortener.domain.user.exceptions import UserNotFoundError, UserPasswordIncorrectError

from shortener.infra.translations.i18n import get_translator

from . import router


login_responses = FastAPIRouteResponses()
login_responses.set_response(
    status_code=HTTPStatus.OK,
    description="Login successfully.",
    model=SuccessLoginResponse
)
login_responses.set_response(
    status_code=HTTPStatus.UNAUTHORIZED,
    description="Invalid credentials.",
    model=ErrorResponse
)


@router.post("/login", responses=login_responses.get_responses())
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
        return JSONResponse(
            status_code=HTTPStatus.UNAUTHORIZED,
            content={"code": "INVALID_CREDENTIALS", "detail": detail}
        )

    return SuccessLoginResponse.make_response(
        access_token=retrieved["access_token"],
        access_token_type="bearer",
        access_token_expires_in=use_case.access_token_expires_in,
        refresh_token=retrieved["refresh_token"].token,
        refresh_token_expires_in=use_case.refresh_token_expires_in,
        user=retrieved["user"]
    )
