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

## 2026-10-13: More consequences, and decided to reject them

A correction: the redirect is now at `GET /v1/slugs/{slug}/redirect`. `GET /v1/slugs/{slug}` answers the target URL as JSON, as it was stored, with the control characters.

The two endpoints of a slug don't agree: a browser that follows the URL of the JSON, such as from a link, removes tabs and line breaks, as the URL standard of WHATWG says, and goes to `https://example.com`, while the redirect goes to `https://exa%09mple.com`. And a system that uses the API, and writes the URL of the JSON in a header of its own without encoding it, can have a header injected.

A value with a NUL character (`\x00`) can't be stored: Postgres doesn't accept it in a `text`, and `add()` fails with `CharacterNotInRepertoireError` (SQLSTATE `22021`), which isn't transient. So `POST /v1/shorturls` answers `500` to a value the client sent. Checked against Postgres 17.

Decided that `TargetURL.create()` rejects control characters, with `INVALID_FORMAT`. Which characters it rejects is still to be decided.

## 2026-10-14: Decided to lean to rejecting more characters

Which characters `TargetURL.create()` rejects is decided when the issue is fixed, rejecting more rather than fewer when in doubt, since accepting a character later is easier than rejecting one that is already accepted. The ones considered so far are those of C0 (U+0000 to U+001F), DEL (U+007F), those of C1 (U+0080 to U+009F) and the space, which `docs/domain.md` (TargetURL) says is accepted.
