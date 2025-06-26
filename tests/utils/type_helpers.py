from typing import Annotated, get_args, get_origin


def get_annotated_args(obj) -> tuple:
    assert get_origin(obj) is Annotated
    return get_args(obj)
