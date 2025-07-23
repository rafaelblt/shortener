from http import HTTPStatus

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from shortener.adapters.api.v1.schemas.responses import ValidationError

from shortener.domain.shared.exceptions import MultiValidationError


async def multi_validation_handler(request, exc):
    assert isinstance(exc, MultiValidationError)

    errors = []

    for error in exc.errors:
        code = error.code
        msg = error.message
        loc: list[int | str] = ["body", error.field]
        
        validation_error = ValidationError(code=code, msg=msg, loc=loc)

        errors.append(validation_error)
    
    return JSONResponse(
        status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
        content={"detail": jsonable_encoder(errors)},
    )
