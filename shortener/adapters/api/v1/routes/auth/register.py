from http import HTTPStatus

from fastapi.responses import JSONResponse

from shortener.adapters.api.v1.dependencies import (
    RegisterUserUseCaseDependency,
    LanguageParserDependency
)
from shortener.adapters.api.v1.error_codes import ApiErrorCode
from shortener.adapters.api.v1.schemas.entities import PublicUserSchema
from shortener.adapters.api.v1.schemas.requests.auth import RegisterRequest
from shortener.adapters.api.v1.schemas.responses.auth.register import SuccessRegisterResponse
from shortener.adapters.api.v1.schemas.responses.error_response import ErrorResponse
from shortener.adapters.api.v1.schemas.responses.types import FastAPIRouteResponses

from shortener.domain.plan.exceptions import PlanNotFoundError
from shortener.domain.user.exceptions import EmailAlreadyExistsError

from shortener.infra.translations import get_translator

from . import router


register_responses = FastAPIRouteResponses()
register_responses.set_response(
    status_code=HTTPStatus.CREATED,
    description="User registered.",
    model=SuccessRegisterResponse
)
register_responses.set_error_response(
    status_code=HTTPStatus.BAD_REQUEST,
    description="Provided Plan ID not found.",
    example_code=ApiErrorCode.ITEM_NOT_FOUND
)
register_responses.set_error_response(
    status_code=HTTPStatus.CONFLICT,
    description="Provided email already exists.",
    example_code=ApiErrorCode.ALREADY_PROCESSED
)


@router.post(
    "/register",
    status_code=HTTPStatus.CREATED,
    responses=register_responses.get_responses()
)
async def register(
    request: RegisterRequest,
    use_case: RegisterUserUseCaseDependency,
    language: LanguageParserDependency
):
    _  = get_translator(language)
    try:
        user = await use_case.execute(
            email=request.get_email(),
            name=request.get_name(),
            plan_pk=request.get_plan_pk(),
            password=request.get_password(),
            lang=language
        )
    except PlanNotFoundError:
        detail = _("No plan was found with the ID provided.")
        error_code = ApiErrorCode.ITEM_NOT_FOUND
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=ErrorResponse(code=error_code, detail=detail).model_dump()
        )
    except EmailAlreadyExistsError:
        detail = _("The email provided has already been registered.")
        error_code = ApiErrorCode.ALREADY_PROCESSED
        return JSONResponse(
            status_code=HTTPStatus.CONFLICT,
            content=ErrorResponse(code=error_code, detail=detail).model_dump()
        )
    
    msg = _("User registered successfully. Please check your email to verify your account.")
    return SuccessRegisterResponse(
        message=msg, user=PublicUserSchema.from_domain(user)
    )
