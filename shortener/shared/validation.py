import re

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Self

from shortener.shared.result import Err, Ok, Result


class IssueCode(Enum):
    INVALID_TYPE = "invalid_type"
    TOO_SHORT = "too_short"
    TOO_LONG = "too_long"
    INVALID_FORMAT = "invalid_format"


@dataclass(frozen=True)
class ValidationIssue:
    code: IssueCode


@dataclass(frozen=True)
class ValidationError:
    issues: tuple[ValidationIssue, ...]


class StringValidation:
    """
    Checks a value against chained rules, and records an issue for each rule
    the value breaks. A value that isn't a str only gets INVALID_TYPE, and the
    rules are skipped.
    """

    def __init__(self, value: object):
        self._value = value
        self._issues: list[ValidationIssue] = []
        if not isinstance(value, str):
            self._issues.append(ValidationIssue(IssueCode.INVALID_TYPE))

    def min_length(self, length: int) -> Self:
        return self.satisfies(
            lambda value: len(value) >= length, IssueCode.TOO_SHORT
        )

    def max_length(self, length: int) -> Self:
        return self.satisfies(
            lambda value: len(value) <= length, IssueCode.TOO_LONG
        )

    def matches(self, pattern: re.Pattern[str]) -> Self:
        return self.satisfies(
            lambda value: pattern.fullmatch(value) is not None,
            IssueCode.INVALID_FORMAT,
        )

    def satisfies(self, rule: Callable[[str], bool], code: IssueCode) -> Self:
        if isinstance(self._value, str) and not rule(self._value):
            self._issues.append(ValidationIssue(code))
        return self

    def result(self) -> Result[str, ValidationError]:
        if self._issues:
            return Err(ValidationError(tuple(self._issues)))
        return Ok(self._value)
