from shortener.domain.user.exceptions import UserNotFoundError, UserPasswordIncorrectError

from shortener.adapters.api.v1.dependencies import (
    LoginUserUseCaseDependency,
    LanguageParserDependency
)

from shortener.adapters.api.v1.schemas.requests.auth import LoginRequest
from shortener.adapters.api.v1.schemas.responses.auth.login import (
    SuccessLoginResponse,
    FailLoginResponse,
)
from shortener.adapters.api.v1.schemas.responses.types import FastAPIRouteResponses

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
        token = await use_case.execute(
            email=email, password=request.password
        )
    except (UserNotFoundError, UserPasswordIncorrectError):
        return FailLoginResponse.json_response(language)

    expires_minutes = use_case.auth_token_service.expires_minutes
    return SuccessLoginResponse(
        access_token=token,
        token_type="bearer",
        expires_minutes=expires_minutes,
        email=email
    )
