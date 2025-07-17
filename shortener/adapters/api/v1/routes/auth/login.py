from shortener.domain.user.exceptions import UserNotFoundError, UserPasswordIncorrectError

from shortener.adapters.api.v1.dependencies import (
    LoginUserUseCaseDependency,
    LanguageParserDependency
)

from shortener.adapters.api.v1.schemas.requests.auth import LoginRequest
from shortener.adapters.api.v1.schemas.responses.auth.login import (
    SuccessLoginResponse,
    FailLoginResponse,
    LOGIN_RESPONSES
)

from . import router


@router.post("/login", responses=LOGIN_RESPONSES)
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
