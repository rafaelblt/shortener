from typing import Annotated

from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from shortener.use_cases import (
    LoginUserUseCase,
    RegisterUserUseCase,
    VerifyEmailUseCase
)

from shortener.adapters.api.v1.exception_handlers import (
    RegisterUserExceptionHandler,
    LoginUserExceptionHandler,
    VerifyEmailExceptionHandler
)
from shortener.adapters.api.v1.schemas import (
    MessageResponse,
    UserRegisterSchema
)
from shortener.adapters.api.v1.schemas.auth import (
    LoginRequest,
    LoginResponse
)
from shortener.adapters.api.v1.dependencies import (
    make_login_user_use_case,
    make_register_user_use_case,
    make_verify_email_use_case
)


LoginUserUseCaseDependency = Annotated[
    LoginUserUseCase, Depends(make_login_user_use_case)
]
LoginUserExceptionHandlerDependency = Annotated[
    LoginUserExceptionHandler, Depends(LoginUserExceptionHandler)
]

RegisterUserUseCaseDependency = Annotated[
    RegisterUserUseCase, Depends(make_register_user_use_case)
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


@router.post("/register")
async def register(
    data: UserRegisterSchema,
    use_case: RegisterUserUseCaseDependency,
    exception_handler: RegisterUserExceptionHandlerDependency
):
    try:
        user = await use_case.execute(
            email=data.get_email(),
            name=data.get_name(),
            plan_id=data.plan_id,
            password=data.password
        )
    except Exception as error:
        exception_handler.handle(error)

    return JSONResponse(
        status_code=HTTPStatus.CREATED,
        content={"message": "User registered successfully."}
    )


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
