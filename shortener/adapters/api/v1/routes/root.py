from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, Response

from shortener.use_cases import ResolveShortURLUseCase
from shortener.adapters.api.v1.dependencies import make_resolve_shorturl_use_case


router = APIRouter()


@router.get("/{slug}")
def resolve_shorturl(
    slug: str,
    use_case: ResolveShortURLUseCase = Depends(make_resolve_shorturl_use_case)
):
    url = use_case.resolve_slug(slug)

    if url is None:
        return Response(status_code=HTTPStatus.NOT_FOUND)

    return RedirectResponse(url=url)
