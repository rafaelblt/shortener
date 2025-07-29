from shortener.domain.shared.datetime_utils import utc_now

from shortener.domain.user import User
from tests.utils.date_helpers import assert_datetime


def test_update_last_login(normal_user: User):
    old_last_login = normal_user.last_login
    expected = utc_now()

    normal_user.update_last_login()

    assert old_last_login != normal_user.last_login
    assert normal_user.last_login is not None
    assert_datetime(
        normal_user.last_login, expected,
        year=True, month=True, day=True, hour=True, minute=True, second=True
    )
