---
status: open
resolution:
labels: [question, domain, use_cases]
---

# 0024: A deleted user can create short URLs until their token expires

Opened on 2026-10-16.

`docs/domain.md#owner` accepts that the short URLs of a deleted user keep working until the event of the deletion is processed, which is issue 0017. That window doesn't cover what happens after it: the service verifies an access token by itself, and doesn't know which users were deleted (`docs/infra.md#access-tokens`), so a token issued to the user before the deletion stays valid until its `exp`. If the user creates a short URL with it after the event was processed, the event doesn't come again, and that short URL is never deleted.

Whether to handle it, and how, is still to be decided. Some ways, from the discussion of issue 0017:

- Accept it, if the tokens are short-lived.
- Keep the IDs of the deleted users, and refuse to create short URLs for them.
- Delete the short URLs of the user again after their tokens can no longer be valid.
