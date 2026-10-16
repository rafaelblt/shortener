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


def _target_url(resolved: ResolvedSlug) -> str:
    return resolved.target_url


def _shorturl_location(details: ShortURLDetails) -> str:
    return PREFIX + _SHORTURL_PATH.format(id=details.id)


ENDPOINTS = (
    Endpoint("GET", "/slugs/{slug}", ResolveSlug),
    Endpoint(
        "GET",
        "/slugs/{slug}/redirect",
        ResolveSlug,
        Redirect(_target_url),
        name="RedirectSlug",
    ),
    Endpoint("POST", "/shorturls", CreateShortURL, Created(_shorturl_location)),
    Endpoint(
        "GET",
        "/shorturls",
        ListShortURLs,
        JSONContent(encode=ShortURLPageContent.from_page),
    ),
    Endpoint("GET", _SHORTURL_PATH, GetShortURL),
    Endpoint("PATCH", _SHORTURL_PATH, UpdateShortURL),
    Endpoint("POST", f"{_SHORTURL_PATH}/enable", EnableShortURL),
    Endpoint("POST", f"{_SHORTURL_PATH}/disable", DisableShortURL),
    Endpoint("DELETE", _SHORTURL_PATH, DeleteShortURL, NoContent()),
)
