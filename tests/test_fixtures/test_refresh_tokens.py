from shortener.domain.refresh_token import RefreshToken
from shortener.domain.user.user import User


def test_active_refresh_token(
    active_refresh_token: RefreshToken, normal_user: User
):
    assert isinstance(active_refresh_token, RefreshToken)
    assert active_refresh_token.user == normal_user
    assert active_refresh_token.is_expired() == False
    assert active_refresh_token.is_revoked() == False


def test_revoked_refresh_token(
    revoked_refresh_token: RefreshToken, normal_user: User
):
    assert isinstance(revoked_refresh_token, RefreshToken)
    assert revoked_refresh_token.user == normal_user
    assert revoked_refresh_token.is_expired() == False
    assert revoked_refresh_token.is_revoked() == True
