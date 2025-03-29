from datetime import datetime, timezone

from typing import Optional


class User:
    def __init__(
        self,
        id: Optional[int] = None,
        name: str = "",
        email: str = "",
        hashed_password: str = "",
        is_active: bool = True,
        is_superuser: bool = False,
        created_at: datetime = datetime.now(tz=timezone.utc),
        last_login: Optional[datetime] = None
    ):
        self.id = id
        self.name = name
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.created_at = created_at
        self.last_login = last_login
