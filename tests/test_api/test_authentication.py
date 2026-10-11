from unittest.mock import NonCallableMagicMock

from shortener.api.authentication import AccessTokenCurrentUser
from shortener.domain import UserID


async def test_get_id_returns_none_without_verifying_when_there_is_no_token(
    access_token_verifier: NonCallableMagicMock,
):
    current_user = AccessTokenCurrentUser(None, access_token_verifier)

    assert await current_user.get_id() is None
    access_token_verifier.verify.assert_not_awaited()


async def test_get_id_returns_the_user_the_verifier_returns_for_the_token(
    access_token_verifier: NonCallableMagicMock, owner_id: UserID
):
    current_user = AccessTokenCurrentUser("token", access_token_verifier)

    assert await current_user.get_id() == owner_id
    access_token_verifier.verify.assert_awaited_once_with("token")


async def test_get_id_returns_none_when_the_verifier_does_not_accept_the_token(
    access_token_verifier: NonCallableMagicMock,
):
    access_token_verifier.verify.return_value = None
    current_user = AccessTokenCurrentUser("token", access_token_verifier)

    assert await current_user.get_id() is None
