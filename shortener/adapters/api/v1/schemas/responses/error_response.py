from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str = Field(..., description="The code error")
    detail: str = Field(..., description="The error detail")


class ValidationError(BaseModel):
    code: str
    msg: str
    loc: list[str | int]
