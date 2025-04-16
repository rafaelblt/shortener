import re


NAME_MAX_LENGTH = 200
NAME_MIN_LENGTH = 2
NAME_REGEX_PATTERN = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$")


class Name(str):
    """A custom string class representing a name for User"""

    def __new__(cls, value: str):
        value = str(value)
        cls.validate_name(value)

    def __repr__(self):
        return f"<Name {super().__repr__()}>"

    @staticmethod
    def validate_name(value: str):
        if len(value) > NAME_MAX_LENGTH:
            raise Exception()
        
        if len(value) < NAME_MIN_LENGTH:
            raise Exception()
        
        if not NAME_REGEX_PATTERN.match(value):
            raise ValueError(
                "Name must contain only letters, spaces, hyphens (-), "
                "and apostrophes (')."
            )
