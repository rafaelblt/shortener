from datetime import datetime, timezone
from shortener.domain.user import User


def test_update_last_login(normal_user: User):
    old_last_login = normal_user.last_login
    expected = datetime.now(tz=timezone.utc)
    timef = "%d/%m/%Y, %H:%M:%S"

    normal_user.update_last_login()

    assert old_last_login != normal_user.last_login
    assert normal_user.last_login.strftime(timef) == expected.strftime(timef)
