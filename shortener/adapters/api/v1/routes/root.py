from http import HTTPStatus

from fastapi import APIRouter
from fastapi.responses import RedirectResponse, Response

from shortener.adapters.api.v1.dependencies import ResolveShortURLUseCaseDependency


router = APIRouter()


@router.get("/{slug}")
def resolve_shorturl(
    slug: str,
    use_case: ResolveShortURLUseCaseDependency
):
    url = use_case.resolve_slug(slug)

    if url is None:
        return Response(status_code=HTTPStatus.NOT_FOUND)

    return RedirectResponse(url=url)
