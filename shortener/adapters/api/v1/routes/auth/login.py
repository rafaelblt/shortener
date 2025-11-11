from http import HTTPStatus

from shortener.adapters.api.v1.dependencies import LoginUserUseCaseDependency
from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.adapters.api.v1.schemas.requests.auth import LoginRequest
from shortener.adapters.api.v1.schemas.responses.types import FastAPIRouteResponses
from shortener.adapters.api.v1.schemas.responses.auth import SuccessLoginResponse

from shortener.domain.user.exceptions import (
    UserAccessDeniedError, UserNotFoundError, UserPasswordIncorrectError
)

from .api_router import router


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
): 
    email = request.get_email()
    try:
        retrieved = await use_case.execute(
            email=email, password=request.password
        )
    except (UserNotFoundError, UserPasswordIncorrectError):
        detail = "Invalid email or password."
        return responses.get_json_response_by_status_code(
            HTTPStatus.UNAUTHORIZED, {"detail": detail}
        )
    except UserAccessDeniedError:
        detail = "The user cannot be authenticated."
        return responses.get_json_response_by_status_code(
            HTTPStatus.FORBIDDEN, {"detail": detail}
        )

    return SuccessLoginResponse.make_response(
        access_token=retrieved["access_token"],
        refresh_token=retrieved["refresh_token"],
        user=retrieved["user"]
    )
