from fastapi import FastAPI

from .request_validation_error import custom_request_validation_handler, RequestValidationError


def get_exception_handlers():
    return [
        (RequestValidationError, custom_request_validation_handler)
    ]


def register_exception_handlers(app: FastAPI):
    for exception, handler in get_exception_handlers():
        app.add_exception_handler(exception, handler)
