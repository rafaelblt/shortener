from fastapi import APIRouter


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


from . import login, register, verify_email, refresh_login
