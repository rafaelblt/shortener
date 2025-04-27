class PlanAttributeTypeError(TypeError):
    def __init__(self, attr: str, type_expected: str, got):
        super().__init__(
            f"The Plan {attr} must be an instance of {type_expected}, got "
            f"{type(got).__name__}"
        )



class PlanInvalidToUpdateError(Exception): ...
class PlanNotFoundInDatabaseError(Exception): ...
