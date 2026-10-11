from shortener.shared.result import Ok
from shortener.shared.validation import IssueCode
from shortener.use_cases.errors import FieldError, collect_field_errors
from tests.fixtures.shared.validation import invalid


TOO_SHORT = invalid(IssueCode.TOO_SHORT)
INVALID_FORMAT = invalid(IssueCode.INVALID_FORMAT)


def test_collect_field_errors_returns_a_field_error_for_each_err_in_order():
    field_errors = collect_field_errors(
        slug=TOO_SHORT, name=Ok("my-name"), target_url=INVALID_FORMAT
    )
    assert field_errors == (
        FieldError("slug", TOO_SHORT.error),
        FieldError("target_url", INVALID_FORMAT.error),
    )


def test_collect_field_errors_returns_an_empty_tuple_when_every_result_is_ok():
    assert collect_field_errors(slug=Ok("my-slug"), target_url=Ok(None)) == ()
