from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    code: str = Field(default="UNKNOWN_ERROR", description="The code error")
    detail: str


class ValidationError(BaseModel):
    code: str
    msg: str
    loc: list[str | int]
