from fastapi import Depends
from typing import Annotated

from ..exception_handlers import (
    LoginUserExceptionHandler,
    RegisterUserExceptionHandler,
    VerifyEmailExceptionHandler
)


LoginUserExceptionHandlerDependency = Annotated[
    LoginUserExceptionHandler, Depends(LoginUserExceptionHandler)
]

RegisterUserExceptionHandlerDependency = Annotated[
    RegisterUserExceptionHandler, Depends(RegisterUserExceptionHandler)
]

VerifyEmailExceptionHandlerDependency = Annotated[
    VerifyEmailExceptionHandler, Depends(VerifyEmailExceptionHandler)
]
