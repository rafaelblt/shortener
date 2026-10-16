class UnavailableError(Exception):
    """
    Raised by the implementations of the abstractions for a failure that
    trying again may fix. See docs/architecture/use_cases.md#unavailableerror
    """
