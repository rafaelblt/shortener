from typing import Final

from shortener.api.endpoint import Endpoint
from shortener.api.prefix import PREFIX
from shortener.api.responses import Created, JSONContent, NoContent, Redirect
from shortener.api.shorturl_page_content import ShortURLPageContent
from shortener.use_cases.create_shorturl import CreateShortURL
from shortener.use_cases.delete_shorturl import DeleteShortURL
from shortener.use_cases.disable_shorturl import DisableShortURL
from shortener.use_cases.enable_shorturl import EnableShortURL
from shortener.use_cases.get_shorturl import GetShortURL
from shortener.use_cases.list_shorturls import ListShortURLs
from shortener.use_cases.resolve_slug import ResolveSlug
from shortener.use_cases.resolved_slug import ResolvedSlug
from shortener.use_cases.shorturl_details import ShortURLDetails
from shortener.use_cases.update_shorturl import UpdateShortURL


_SHORTURL_PATH: Final = "/shorturls/{id}"
_SLUGS_TAG: Final = "Slugs"
_SHORTURLS_TAG: Final = "Short URLs"


def _target_url(resolved: ResolvedSlug) -> str:
    return resolved.target_url


def _shorturl_location(details: ShortURLDetails) -> str:
    return PREFIX + _SHORTURL_PATH.format(id=details.id)


ENDPOINTS = (
    Endpoint(
        "GET",
        "/slugs/{slug}",
        ResolveSlug,
        summary="Resolve a slug",
        tag=_SLUGS_TAG,
    ),
    Endpoint(
        "GET",
        "/slugs/{slug}/redirect",
        ResolveSlug,
        Redirect(_target_url),
        summary="Redirect to the target URL of a slug",
        tag=_SLUGS_TAG,
        name="RedirectSlug",
    ),
    Endpoint(
        "POST",
        "/shorturls",
        CreateShortURL,
        Created(_shorturl_location),
        summary="Create a short URL",
        tag=_SHORTURLS_TAG,
    ),
    Endpoint(
        "GET",
        "/shorturls",
        ListShortURLs,
        JSONContent(encode=ShortURLPageContent.from_page),
        summary="List the short URLs of the user",
        tag=_SHORTURLS_TAG,
    ),
    Endpoint(
        "GET",
        _SHORTURL_PATH,
        GetShortURL,
        summary="Get a short URL",
        tag=_SHORTURLS_TAG,
    ),
    Endpoint(
        "PATCH",
        _SHORTURL_PATH,
        UpdateShortURL,
        summary="Update a short URL",
        tag=_SHORTURLS_TAG,
    ),
    Endpoint(
        "POST",
        f"{_SHORTURL_PATH}/enable",
        EnableShortURL,
        summary="Enable a short URL",
        tag=_SHORTURLS_TAG,
    ),
    Endpoint(
        "POST",
        f"{_SHORTURL_PATH}/disable",
        DisableShortURL,
        summary="Disable a short URL",
        tag=_SHORTURLS_TAG,
    ),
    Endpoint(
        "DELETE",
        _SHORTURL_PATH,
        DeleteShortURL,
        NoContent(),
        summary="Delete a short URL",
        tag=_SHORTURLS_TAG,
    ),
)
