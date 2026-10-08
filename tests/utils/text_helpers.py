def assert_mentions(text: str, *terms: str) -> None:
    """
    Checks what a message has to name, such as a field or a type, without
    fixing its wording, so rewording the message doesn't break the test.
    """
    for term in terms:
        assert term in text, f"{term!r} is not in {text!r}"
