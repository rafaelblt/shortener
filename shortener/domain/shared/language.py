from enum import Enum


class Language(str, Enum):
    EN = "en"
    PT_BR = "pt_br"
    FR = "fr"

    @classmethod
    def default(cls) -> "Language":
        return cls.EN
