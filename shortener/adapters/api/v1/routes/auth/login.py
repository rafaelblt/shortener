from shortener.adapters.api.v1.schemas.requests.auth import LoginRequest

from shortener.adapters.api.v1.schemas.auth import (
    LoginResponse,
)
from shortener.adapters.api.v1.dependencies import (
    LoginUserUseCaseDependency,
    LoginUserExceptionHandlerDependency,
)

from . import router


@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    use_case: LoginUserUseCaseDependency,
    exception_handler: LoginUserExceptionHandlerDependency
): 
    email = request.get_email()
    try:
        token = await use_case.execute(
            email=email, password=request.password
        )
    except Exception as error:
        exception_handler.handle(error)

    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_minutes": use_case.auth_token_service.expires_minutes,
        "email": email
    }
