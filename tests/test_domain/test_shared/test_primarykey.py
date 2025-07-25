import pytest

from shortener.domain.shared.primarykey import PrimaryKey, PkType


def test_classmethod_create_pk_id():
    pk = PrimaryKey.create_pk_id(1)
    assert isinstance(pk, PrimaryKey)
    assert pk._type == PkType.ID
    assert pk._value == "1"


def test_classmethod_create_pk_undefined():
    pk = PrimaryKey.create_pk_undefined()
    assert isinstance(pk, PrimaryKey)
    assert pk._type == PkType.UNDEFINED
    assert pk._value == ""


def test_property_pk_type():
    pk = PrimaryKey.create_pk_undefined()
    assert pk.pk_type == PkType.UNDEFINED


@pytest.mark.parametrize(
    ["pk", "expected"],
    [
        (PrimaryKey.create_pk_undefined(), -1),
        (PrimaryKey.create_pk_id(1), 1)
    ]
)
def test_method_get_id(pk: PrimaryKey, expected: int):
    if pk.pk_type == PkType.ID:
        assert pk.get_id() == expected
    else:
        with pytest.raises(ValueError, match="The pk is not of type id"):
            pk.get_id()
