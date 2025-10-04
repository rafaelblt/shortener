from fastapi import Depends

from shortener.infra.services.passlib_hasher import PasslibPasswordHasher
from shortener.infra.settings import get_settings


def make_passlib_password_hasher_service():
    return PasslibPasswordHasher()


def get_password_hasher_service():
    match get_settings().password_hasher_service_impl:
        case "passlib":
            dep_func = make_passlib_password_hasher_service
        case _:
            dep_func = make_passlib_password_hasher_service
    return Depends(dep_func)
