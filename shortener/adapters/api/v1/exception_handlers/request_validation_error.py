from http import HTTPStatus

from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from shortener.adapters.api.v1.schemas.responses import ValidationError


async def custom_request_validation_handler(request, exc):
    assert isinstance(exc, RequestValidationError)

    errors = []

    for error in exc.errors():
        code = error.get("type", "VALIDATION_ERROR").upper()
        msg = error.get("msg", "")
        loc = error.get("loc", [])
        
        validation_error = ValidationError(code=code, msg=msg, loc=loc)

        errors.append(validation_error)
    
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(errors)},
    )
