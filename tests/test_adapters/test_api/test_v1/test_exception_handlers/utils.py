import pytest

from shortener.adapters.api.v1.exception_handlers import ExceptionHandler


def test_raise_unhandled_exception(exception_handler: ExceptionHandler):
    message = "Another error occurred."    
    with pytest.raises(RuntimeError, match=message):
        exception_handler.handle(RuntimeError(message))
