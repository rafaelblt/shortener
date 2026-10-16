from fastapi import FastAPI
from fastapi.routing import APIRoute

from shortener.api.endpoints import ENDPOINTS


def test_every_endpoint_is_under_v1(app: FastAPI):
    paths = {route.path for route in app.routes if isinstance(route, APIRoute)}
    assert paths == {f"/v1{endpoint.path}" for endpoint in ENDPOINTS} | {"/v1/health"}
