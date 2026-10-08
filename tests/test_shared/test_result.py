import pytest

from shortener.shared.result import Err, Ok, Result


def fail(value):
    raise AssertionError("the function must not be called")


def describe(result: Result[int, str]) -> str:
    match result:
        case Ok(value):
            return f"ok {value}"
        case Err(error):
            return f"err {error}"


def test_ok_map_applies_the_function_to_the_value():
    assert Ok(2).map(lambda value: value * 10) == Ok(20)


def test_err_map_returns_itself_without_calling_the_function():
    err = Err("error")
    assert err.map(fail) is err


def test_ok_unwrap_returns_the_value():
    assert Ok(2).unwrap() == 2


def test_err_unwrap_raises_value_error_with_the_error_as_its_argument():
    with pytest.raises(ValueError) as raised:
        Err("error").unwrap()
    assert raised.value.args == ("error",)


def test_ok_and_err_compare_by_content():
    assert Ok(2) == Ok(2)
    assert Err(2) == Err(2)
    assert Ok(2) != Err(2)


def test_ok_and_err_can_be_matched_by_their_content():
    assert describe(Ok(2)) == "ok 2"
    assert describe(Err("error")) == "err error"
