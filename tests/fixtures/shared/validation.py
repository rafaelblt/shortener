from shortener.shared.result import Err
from shortener.shared.validation import (
    IssueCode,
    ValidationError,
    ValidationIssue,
)


def invalid(*codes: IssueCode) -> Err[ValidationError]:
    return Err(ValidationError(tuple(ValidationIssue(code) for code in codes)))
