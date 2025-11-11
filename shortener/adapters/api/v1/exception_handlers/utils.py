from fastapi import FastAPI

from .request_validation_error import custom_request_validation_handler, RequestValidationError


def get_exception_handlers():
    return [
        (RequestValidationError, custom_request_validation_handler)
    ]
