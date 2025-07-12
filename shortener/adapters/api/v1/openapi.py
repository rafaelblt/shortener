from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from shortener.adapters.api.v1.schemas.responses import ValidationError

from shortener.infra.settings import settings


def set_openapi_schema(app: FastAPI):
    if app.openapi_schema:
        return
    
    openapi_schema = get_openapi(
        title=f"{settings.APP_NAME} API",
        version=settings.APP_VERSION,
        description="description",
        routes=app.routes,
    )
    
    openapi_schema["components"]["schemas"]["ValidationError"] = ValidationError.model_json_schema()
    
    app.openapi_schema = openapi_schema
