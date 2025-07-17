from http import HTTPStatus

from shortener.adapters.api.v1.schemas.responses import FastAPIResponsesArgType

from .success import SuccessLoginResponse
from .fail import FailLoginResponse

LOGIN_RESPONSES: FastAPIResponsesArgType = {
    HTTPStatus.OK: {
        "description": "Login successfully",
        "response": SuccessLoginResponse
    },
    HTTPStatus.UNAUTHORIZED: {
        "description": "Invalid credentials",
        "response": FailLoginResponse
    }
}
