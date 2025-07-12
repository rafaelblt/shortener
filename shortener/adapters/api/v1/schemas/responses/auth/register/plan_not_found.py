from http import HTTPStatus
from pydantic import BaseModel
from fastapi.responses import JSONResponse

from shortener.domain.plan.exceptions import PlanNotFoundError


class PlanNotFoundResponse(BaseModel):
    code: str = PlanNotFoundError.code
    detail: str

    @staticmethod
    def json_response(detail: str):
        response = PlanNotFoundResponse(detail=detail)
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=response
        )
