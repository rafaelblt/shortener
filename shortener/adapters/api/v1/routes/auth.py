from http import HTTPStatus

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from shortener.domain.user.exceptions import (
    UserNotFoundInDatabaseError,
    UserPasswordIncorrectError
)

from shortener.use_cases import (
    LoginUserUseCase
)

from shortener.adapters.api.v1.schemas import (
    UserLoginSchema
)
from shortener.adapters.api.v1.dependencies import (
    make_login_user_use_case
)


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/login")
async def login(
    data: UserLoginSchema,
    use_case: LoginUserUseCase = Depends(make_login_user_use_case)
): 
    try:
        token = await use_case.execute(
            email=data.get_email(), password=data.password
        )
    except (UserNotFoundInDatabaseError, UserPasswordIncorrectError):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Invalid email or password."
        )

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={"access_token": token, "token_type": "bearer"}
    )
