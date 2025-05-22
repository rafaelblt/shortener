from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from shortener.use_cases import (
    LoginUserUseCase,
    RegisterUserUseCase
)

from shortener.adapters.api.v1.exception_handlers import (
    RegisterUserExceptionHandler, LoginUserExceptionHandler
)
from shortener.adapters.api.v1.schemas import (
    UserLoginSchema, UserRegisterSchema
)
from shortener.adapters.api.v1.dependencies import (
    make_login_user_use_case,
    make_register_user_use_case
)


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login")
async def login(
    data: UserLoginSchema,
    use_case: LoginUserUseCase = Depends(make_login_user_use_case),
    exception_handler = LoginUserExceptionHandler
): 
    try:
        token = await use_case.execute(
            email=data.get_email(), password=data.password
        )
    except Exception as error:
        exception_handler.handle(error)

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={"access_token": token, "token_type": "bearer"}
    )


@router.post("/register")
async def register(
    data: UserRegisterSchema,
    use_case: RegisterUserUseCase = Depends(make_register_user_use_case),
    exception_handler = RegisterUserExceptionHandler
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
