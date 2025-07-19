from http import HTTPStatus

from shortener.domain.shared.exceptions import DomainError

from shortener.infra.translations import get_translator

from shortener.adapters.api.v1.schemas.requests.auth import RegisterRequest
from shortener.adapters.api.v1.schemas.responses.auth.register import (
    SuccessRegisterResponse,
    PlanNotFoundResponse,
    EmailAlreadyExistsResponse
)

from shortener.adapters.api.v1.dependencies import (
    RegisterUserUseCaseDependency,
    LanguageParserDependency
)
from shortener.adapters.api.v1.schemas.responses.types import FastAPIRouteResponses

from . import router


register_responses = FastAPIRouteResponses()
register_responses.set_response(
    status_code=HTTPStatus.CREATED,
    description="User registered.",
    model=SuccessRegisterResponse
)
register_responses.set_response(
    status_code=HTTPStatus.BAD_REQUEST,
    description="Provided Plan ID not found.",
    model=ErrorResponse
)
register_responses.set_response(
    status_code=HTTPStatus.CONFLICT,
    description="Provided email already exists.",
    model=ErrorResponse
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
    try:
        user = await use_case.execute(
            email=request.get_email(),
            name=request.get_name(),
            plan_id=request.plan_id,
            password=request.password,
            lang=language
        )
    except DomainError as error:
        _  = get_translator(language)
        if error.code == PlanNotFoundResponse.code:
            detail = _("No plan was found with the ID provided.")
            return PlanNotFoundResponse.json_response(detail)
        elif error.code == EmailAlreadyExistsResponse.code:
            detail = _("The email provided has already been registered.")
            return EmailAlreadyExistsResponse.json_response(detail)
        else:
            raise error

    return SuccessRegisterResponse.with_domain_user(user, lang=language)
