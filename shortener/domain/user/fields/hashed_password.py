class HashedPassword(str):
    def __new__(cls, value: str):
        value = str(value)
        return super().__new__(cls, value)
