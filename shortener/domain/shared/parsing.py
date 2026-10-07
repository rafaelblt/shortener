def require_non_empty_string(value: object, type_name: str) -> str:
    """
    Raises:
        TypeError: The value isn't a str.
        ValueError: The value is empty.
    """
    if not isinstance(value, str):
        raise TypeError(f"{type_name} must be a str, got {type(value).__name__}")
    if not value:
        raise ValueError(f"{type_name} must not be empty")
    return value
