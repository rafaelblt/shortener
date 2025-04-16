from enum import Enum


class UserStatus(Enum):
    ACTIVE = "active"
    DEACTIVATED = "deactivated"
    BANNED = "banned"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"
