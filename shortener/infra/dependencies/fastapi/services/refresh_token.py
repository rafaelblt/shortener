from fastapi import Depends

from shortener.infra.db.session import get_session
from shortener.infra.services.refresh_token import SQLAlchemyRefreshAuthTokenService
from shortener.infra.settings import get_settings


def make_sqlalchemy_refresh_auth_token_service(
    session = Depends(get_session)
):
    return SQLAlchemyRefreshAuthTokenService(
        session=session, expires_in=get_settings().refresh_token_expiration
    )


def get_refresh_auth_token_service():
    match get_settings().refresh_token_service_impl:
        case "sqlalchemy":
            dep_func = make_sqlalchemy_refresh_auth_token_service
        case _:
            dep_func = make_sqlalchemy_refresh_auth_token_service
    return Depends(dep_func)
