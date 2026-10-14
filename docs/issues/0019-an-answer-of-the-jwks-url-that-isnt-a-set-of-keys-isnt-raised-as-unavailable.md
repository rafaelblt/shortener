---
status: open
resolution:
labels: [bug, infra]
---

# 0019: An answer of the JWKS URL that isn't a set of keys isn't raised as unavailable

Opened on 2026-10-13.

`JWTAccessTokenVerifier.verify()` (`shortener/infra/jwt_access_token_verifier.py`), built with `with_jwks()`, raises `UnavailableError` when the published keys can't be fetched: the URL can't be reached, takes too long, or answers an HTTP error, such as a `404` of a wrong URL. The API answers `503`. But when the URL answers `200` with something that isn't a set of keys, it doesn't (see `docs/infra.md#access-tokens`):

- An answer that isn't JSON, such as an HTML page, raises the error of `json` as it is, and the API answers `500`.
- An answer that is JSON, but not a set of keys, makes `verify()` return `None` for every token, and the API answers `401`, as if the token of the client were wrong.

Neither is a problem of the token, and the service can't tell a wrong setting from a failure of the issuer, as with an HTTP error.

## 2026-10-13: Decided to raise `UnavailableError`

Both answers are a failure to fetch the keys, like an HTTP error, so `verify()` raises `UnavailableError` from them, and the API answers `503`. A token whose `kid` isn't in a valid set of keys is still not valid, and `verify()` still returns `None` for it.
