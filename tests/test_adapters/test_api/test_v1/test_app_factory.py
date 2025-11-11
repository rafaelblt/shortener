from fastapi import FastAPI

from shortener.adapters.api.v1.app_factory import (
    create_app, DEFAULT_EXCEPTION_HANDLERS, DEFAULT_ROUTERS
)


def test_create_app_type():
    retrieved = create_app()
    assert isinstance(retrieved, FastAPI)


def test_default_routers():
    app = create_app()
    expected_routes = []
    missing_routes = []
    for router in DEFAULT_ROUTERS:
        expected_routes.extend(router.routes)
    for route in expected_routes:
        if route not in app.routes:
            missing_routes.append(route)
    assert missing_routes == []


def test_default_exception_handlers():
    app = create_app()
    expected_handlers = DEFAULT_EXCEPTION_HANDLERS
    for exc, handler in expected_handlers.items():
        assert exc in app.exception_handlers
        assert app.exception_handlers.get(exc) == handler


def test_create_app_with_dependency_overrides():
    def example_dep(): ...
    def example_override(): ...
    dep_overrides = {
        example_dep: example_override
    }
    app = create_app(dependency_overrides=dep_overrides)
    assert app.dependency_overrides == dep_overrides
