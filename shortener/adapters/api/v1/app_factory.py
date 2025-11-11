from fastapi import FastAPI, APIRouter
from fastapi.openapi.utils import get_openapi

from shortener.adapters.api.v1.exception_handlers.request_validation_error import (
    custom_request_validation_handler, RequestValidationError
)
from shortener.adapters.api.v1.routes import root, auth, shorturl
from shortener.adapters.api.v1.schemas.responses import ValidationError

from shortener.infra.settings import settings


DEFAULT_EXCEPTION_HANDLERS = {
    RequestValidationError: custom_request_validation_handler
}
DEFAULT_ROUTERS = [
    root.router,
    auth.router,
    shorturl.router
]


def create_app(
    routers: list[APIRouter] = DEFAULT_ROUTERS,
    exception_handlers: dict = DEFAULT_EXCEPTION_HANDLERS,
    middlewares: list = [],
    dependency_overrides: dict = {},
):
    app = FastAPI(
        exception_handlers=exception_handlers,
    )
    for router in routers:
        app.include_router(router)
    for dependency, override in dependency_overrides.items():
        app.dependency_overrides[dependency] = override
    for middleware in middlewares:
        app.add_middleware(middleware, arg1=1)

    openapi_schema = get_openapi(
        title=f"{settings.app_name} API",
        version=settings.app_version,
        description="description",
        routes=app.routes,
    )
    openapi_schema["components"]["schemas"]["ValidationError"] = ValidationError.model_json_schema()

    return app
