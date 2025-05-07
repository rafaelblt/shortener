import pytest
from shortener.domain.user.fields.name import Name
from shortener.domain.user.exceptions import NameInvalidPatternError


def test_new_name():
    name = Name("Leo")
    assert isinstance(name, Name)
    assert isinstance(name, str)
    assert name == "Leo"


def test_name_repr():
    name = Name("Leo")
    assert name.__repr__() == f"<Name 'Leo'>"


def test_new_name_raises_type_error():
    with pytest.raises(TypeError, match="Name value arg must be a str."):
        Name(1)


def test_new_name_raises_validation_error():
    value = "12"
    with pytest.raises(NameInvalidPatternError):
        Name(value)
