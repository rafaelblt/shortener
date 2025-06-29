from typing import Annotated

from http import HTTPStatus

from fastapi import APIRouter, Depends

from shortener.use_cases import (
    LoginUserUseCase,
    VerifyEmailUseCase
)

from shortener.adapters.api.v1.exception_handlers import (
    RegisterUserExceptionHandler,
    LoginUserExceptionHandler,
    VerifyEmailExceptionHandler
)
from shortener.adapters.api.v1.schemas import MessageResponse
from shortener.adapters.api.v1.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest
)
from shortener.adapters.api.v1.dependencies import (
    make_login_user_use_case,
    RegisterUserUseCaseDependency,
    make_verify_email_use_case,
    LanguageParserDependency
)


LoginUserUseCaseDependency = Annotated[
    LoginUserUseCase, Depends(make_login_user_use_case)
]
LoginUserExceptionHandlerDependency = Annotated[
    LoginUserExceptionHandler, Depends(LoginUserExceptionHandler)
]

RegisterUserExceptionHandlerDependency = Annotated[
    RegisterUserExceptionHandler, Depends(RegisterUserExceptionHandler)
]

VerifyEmailUseCaseDependency = Annotated[
    VerifyEmailUseCase, Depends(make_verify_email_use_case)
]
VerifyEmailExceptionHandlerDependency = Annotated[
    VerifyEmailExceptionHandler, Depends(VerifyEmailExceptionHandler)
]


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


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


@router.post(
    "/register", status_code=HTTPStatus.CREATED, response_model=MessageResponse
)
async def register(
    request: RegisterRequest,
    use_case: RegisterUserUseCaseDependency,
    exception_handler: RegisterUserExceptionHandlerDependency,
    language: LanguageParserDependency
):
    try:
        user = await use_case.execute(
            email=request.get_email(),
            name=request.get_name(),
            plan_id=request.plan_id,
            password=request.password,
            lang=language
        )
    except Exception as error:
        exception_handler.handle(error)

    return {"message": "User registered successfully."}


@router.get("/verify-email/{token}", response_model=MessageResponse)
async def verify_email(
    token: str,
    use_case: VerifyEmailUseCaseDependency,
    exception_handler: VerifyEmailExceptionHandlerDependency
):
    try:
        await use_case.execute(token)
    except Exception as error:
        exception_handler.handle(error)
    
    return {"message": "Email successfully verified."}
