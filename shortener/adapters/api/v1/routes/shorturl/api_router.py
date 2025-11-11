from fastapi import APIRouter, Depends

from shortener.adapters.api.v1.dependencies.current_user import require_authenticated_user


router = APIRouter(
    prefix="/api/v1/shorturls",
    tags=["shorturls"],
    dependencies=[Depends(require_authenticated_user)]
)
