from http import HTTPStatus

from shortener.adapters.api.v1.dependencies import (
    RegisterUserUseCaseDependency,
    LanguageParserDependency
)
from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.adapters.api.v1.schemas.requests.auth import RegisterRequest
from shortener.adapters.api.v1.schemas.responses.auth import RegisterSuccessResponse
from shortener.adapters.api.v1.schemas.responses.types import FastAPIRouteResponses

from shortener.domain.plan.exceptions import PlanNotFoundError
from shortener.domain.user.exceptions import EmailAlreadyExistsError

from .api_router import router


register_responses = FastAPIRouteResponses()
register_responses.set_response(
    status_code=HTTPStatus.CREATED,
    description="User registered.",
    model=RegisterSuccessResponse
)
register_responses.set_error_response(
    status_code=HTTPStatus.BAD_REQUEST,
    description="Provided Plan ID not found.",
    error_code=ApiErrorCode.ITEM_NOT_FOUND
)
register_responses.set_error_response(
    status_code=HTTPStatus.CONFLICT,
    description="Provided email already exists.",
    error_code=ApiErrorCode.ALREADY_PROCESSED
)


@router.post(
    "/register",
    status_code=HTTPStatus.CREATED,
    responses=register_responses.get_schema()
)
async def register(
    request: RegisterRequest,
    use_case: RegisterUserUseCaseDependency,
    language: LanguageParserDependency
):
    try:
        user = await use_case.execute(
            email=request.get_email(),
            name=request.get_name(),
            plan_pk=request.get_plan_pk(),
            password=request.get_password(),
            lang=language
        )
    except PlanNotFoundError:
        detail = "No plan was found with the ID provided."
        return register_responses.get_json_response_by_status_code(
            HTTPStatus.BAD_REQUEST, {"detail": detail}
        )
    except EmailAlreadyExistsError:
        detail = "The email provided has already been registered."
        return register_responses.get_json_response_by_status_code(
            HTTPStatus.CONFLICT, {"detail": detail}
        )
    
    return RegisterSuccessResponse.with_domain_user(user)
