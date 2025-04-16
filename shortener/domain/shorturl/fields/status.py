from enum import Enum


class ShortURLStatus(Enum):
    ACTIVE = "active"
    DEACTIVATED = "deactivated"
    BANNED = "banned"
    SUSPENDED = "suspended"
    EXPIRED = "expired"
