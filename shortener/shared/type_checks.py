def check_parameter_type(parameter: str, value: object, expected_type: type) -> None:
    """
    Raises:
        TypeError: The value isn't an instance of expected_type.
    """
    if not isinstance(value, expected_type):
        raise TypeError(
            f"The {parameter} parameter must be an instance of "
            f"{expected_type.__name__}, got {type(value).__name__}"
        )
