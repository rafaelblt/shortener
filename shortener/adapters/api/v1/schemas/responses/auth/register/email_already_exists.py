from http import HTTPStatus
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from shortener.domain.user.exceptions import EmailAlreadyExistsError


class EmailAlreadyExistsResponse(BaseModel):
    code: str = EmailAlreadyExistsError.code
    detail: str

    @classmethod
    def json_response(cls, detail: str):
        response = cls(detail=detail)
        return JSONResponse(
            status_code=HTTPStatus.CONFLICT,
            content=response
        )
