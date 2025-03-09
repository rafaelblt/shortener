from fastapi import FastAPI

from shortener.adapters.api.v1.routes import root, shorturl


app = FastAPI()

app.include_router(root.router)
app.include_router(shorturl.router)


@app.get("/")
async def read_root():
    return {"message": "Hello World!"}
