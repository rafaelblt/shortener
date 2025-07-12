from http import HTTPStatus

from shortener.adapters.api.v1.schemas.responses import FastAPIResponsesArgType

from .success_response import SuccessRegisterResponse
from .email_already_exists import EmailAlreadyExistsResponse
from .plan_not_found import PlanNotFoundResponse


REGISTER_RESPONSES: FastAPIResponsesArgType = {
    HTTPStatus.CREATED: {
        "description": "User registered.",
        "model": SuccessRegisterResponse
    },
    HTTPStatus.BAD_REQUEST: {
        "description": "Provided Plan ID not found.",
        "model": PlanNotFoundResponse
    },
    HTTPStatus.CONFLICT: {
        "description": "Provided email already exists.",
        "model": EmailAlreadyExistsResponse
    },
}
