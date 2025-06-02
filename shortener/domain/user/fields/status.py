from enum import Enum


class UserStatus(Enum):
    ACTIVE = "active"
    UNVERIFIED_EMAIL = "unverified_email"
    BANNED = "banned"
    SUSPENDED = "suspended"
    LOCKED = "locked"
