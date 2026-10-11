---
status: open
resolution:
labels: [question, domain]
---

# 0013: `TargetURL` accepts control characters

Opened on 2026-10-11.

`TargetURL.create()` (`shortener/domain/target_url.py`) returns `Ok` for a value with control characters, such as `https://example.com/\r\nSet-Cookie: x=1`, `https://exa\tmple.com` or `https://example.com/\x00`. It only checks the result of `urllib.parse.urlparse`, which removes tabs and line breaks before parsing, so the value has a scheme and a netloc, and `TargetURL` keeps the value as it was given, with them.

Found while adding the redirect of the API (`GET /v1/slugs/{slug}`, `docs/api.md#endpoints`), which sends the target URL in the `Location` header. The `RedirectResponse` of Starlette percent-encodes those characters, as `https://example.com/%0D%0ASet-Cookie:%20x=1`, so no header is injected, but the client is redirected to a URL other than the one the owner sees in the details, such as `https://exa%09mple.com`, whose host isn't valid.

`docs/domain.md` (TargetURL) says the netloc isn't validated, and that `https://exa mple.com` is accepted, but nothing defines what to do with control characters. Whether `TargetURL.create()` should reject them, with `INVALID_FORMAT`, is still to be decided.
