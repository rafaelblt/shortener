class PlanAttributeTypeError(TypeError):
    def __init__(self, attr: str, type_expected: str, got):
        super().__init__(
            f"The Plan {attr} must be an instance of {type_expected}, got "
            f"{type(got).__name__}"
        )


class PlanNotFoundInDatabaseError(Exception):
    def __init__(self, plan_id: int):
        self.plan_id = plan_id
        super().__init__(f"Plan with id={plan_id} not found.")


class PlanIdIsNotIntError(ValueError):
    def __init__(self, value):
        self.value = value
        super().__init__(
            f"The Plan id is not an integer. Value: {value} ({value.__class__.__name__})"
        )
