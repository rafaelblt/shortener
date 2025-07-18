from fastapi import Depends
from typing import Annotated

from ..exception_handlers import (
    VerifyEmailExceptionHandler
)


VerifyEmailExceptionHandlerDependency = Annotated[
    VerifyEmailExceptionHandler, Depends(VerifyEmailExceptionHandler)
]
