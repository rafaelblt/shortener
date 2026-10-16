import copy
import pickle

from typing import TypeVar

import pytest


T = TypeVar("T")


def pickled(value: T) -> T:
    return pickle.loads(pickle.dumps(value))


COPY_FUNCTIONS = [
    pytest.param(copy.copy, id="copy"),
    pytest.param(copy.deepcopy, id="deepcopy"),
    pytest.param(pickled, id="pickle"),
]
