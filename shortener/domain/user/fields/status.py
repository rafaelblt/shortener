from enum import Enum


class UserStatus(Enum):
    ACTIVE = "active"
    EMAIL_UNVERIFIED = "email_unverified"
    BANNED = "banned"
    SUSPENDED = "suspended"
    LOCKED = "locked"
