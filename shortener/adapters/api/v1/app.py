from fastapi import FastAPI

from shortener.adapters.api.v1.routes import root, auth, shorturl
from .exception_handlers import register_exception_handlers
from .openapi import set_openapi_schema


app = FastAPI()

app.include_router(root.router)
app.include_router(auth.router)
app.include_router(shorturl.router)


@app.get("/")
async def read_root():
    return {"message": "Hello World!"}


register_exception_handlers(app)
set_openapi_schema(app)
