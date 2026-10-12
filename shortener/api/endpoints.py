from http import HTTPStatus

from shortener.api.endpoint import Endpoint
from shortener.api.responses import JSONContent, NoContent, Redirect
from shortener.api.shorturl_page_content import ShortURLPageContent
from shortener.use_cases.create_shorturl import CreateShortURL
from shortener.use_cases.delete_shorturl import DeleteShortURL
from shortener.use_cases.disable_shorturl import DisableShortURL
from shortener.use_cases.enable_shorturl import EnableShortURL
from shortener.use_cases.get_shorturl import GetShortURL
from shortener.use_cases.list_shorturls import ListShortURLs
from shortener.use_cases.resolve_slug import ResolveSlug
from shortener.use_cases.resolved_slug import ResolvedSlug
from shortener.use_cases.update_shorturl import UpdateShortURL


def _target_url(resolved: ResolvedSlug) -> str:
    return resolved.target_url


ENDPOINTS = (
    Endpoint("GET", "/slugs/{slug}", ResolveSlug),
    Endpoint(
        "GET",
        "/slugs/{slug}/redirect",
        ResolveSlug,
        Redirect(_target_url),
        name="RedirectSlug",
    ),
    Endpoint("POST", "/shorturls", CreateShortURL, JSONContent(HTTPStatus.CREATED)),
    Endpoint(
        "GET",
        "/shorturls",
        ListShortURLs,
        JSONContent(encode=ShortURLPageContent.from_page),
    ),
    Endpoint("GET", "/shorturls/{id}", GetShortURL),
    Endpoint("PATCH", "/shorturls/{id}", UpdateShortURL),
    Endpoint("POST", "/shorturls/{id}/enable", EnableShortURL),
    Endpoint("POST", "/shorturls/{id}/disable", DisableShortURL),
    Endpoint("DELETE", "/shorturls/{id}", DeleteShortURL, NoContent()),
)
