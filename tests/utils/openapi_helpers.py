"""
Writes the OpenAPI schema of the API to docs/service/openapi.yaml, with
`poetry run task openapi`. See docs/architecture/api.md#openapi
"""

from pathlib import Path
from typing import Final
from unittest.mock import create_autospec

import yaml

from fastapi import FastAPI

from shortener.api.app import create_app
from shortener.api.authentication import AccessTokenVerifier
from shortener.api.health_check import HealthCheck
from shortener.api.rate_limit import RateLimiter
from tests.fixtures.api.doubles import UseCaseDoubles


OPENAPI_FILE: Final = Path(__file__).parents[2] / "docs" / "service" / "openapi.yaml"


def openapi_yaml(app: FastAPI) -> str:
    return yaml.safe_dump(app.openapi(), sort_keys=False, allow_unicode=True)


def write_openapi_file() -> None:
    # The schema comes only from the routes, so doubles of the abstractions
    # give the same one as their implementations.
    app = create_app(
        use_cases=UseCaseDoubles(),
        access_token_verifier=create_autospec(AccessTokenVerifier, instance=True),
        rate_limiter=create_autospec(RateLimiter, instance=True),
        health_check=create_autospec(HealthCheck, instance=True),
    )
    OPENAPI_FILE.write_text(openapi_yaml(app))


if __name__ == "__main__":
    write_openapi_file()
