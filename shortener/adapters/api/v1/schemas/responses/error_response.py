from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    detail: str


class ValidationError(BaseModel):
    code: str
    msg: str
    loc: list[str | int]
