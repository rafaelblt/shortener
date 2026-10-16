import re

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Self

from shortener.shared.result import Err, Ok, Result


class IssueCode(Enum):
    INVALID_TYPE = "invalid_type"
    TOO_SHORT = "too_short"
    TOO_LONG = "too_long"
    INVALID_FORMAT = "invalid_format"
    TOO_SMALL = "too_small"
    TOO_LARGE = "too_large"


@dataclass(frozen=True)
class ValidationIssue:
    code: IssueCode


@dataclass(frozen=True)
class ValidationError:
    issues: tuple[ValidationIssue, ...]


class _Validation[T]:
    """
    Checks a value against chained rules, and records an issue for each rule
    the value breaks. A value that isn't of the type the subclass validates
    only gets INVALID_TYPE, and the rules are skipped.
    """

    def __init__(self, value: object):
        self._value: Any = value
        self._issues: list[ValidationIssue] = []
        self._has_type = self._is_of_type(value)
        if not self._has_type:
            self._issues.append(ValidationIssue(IssueCode.INVALID_TYPE))

    @staticmethod
    def _is_of_type(value: object) -> bool:
        raise NotImplementedError

    def satisfies(self, rule: Callable[[T], bool], code: IssueCode) -> Self:
        if self._has_type and not rule(self._value):
            self._issues.append(ValidationIssue(code))
        return self

    def result(self) -> Result[T, ValidationError]:
        if self._issues:
            return Err(ValidationError(tuple(self._issues)))
        return Ok(self._value)


class StringValidation(_Validation[str]):
    @staticmethod
    def _is_of_type(value: object) -> bool:
        return isinstance(value, str)

    def min_length(self, length: int) -> Self:
        return self.satisfies(lambda value: len(value) >= length, IssueCode.TOO_SHORT)

    def max_length(self, length: int) -> Self:
        return self.satisfies(lambda value: len(value) <= length, IssueCode.TOO_LONG)

    def matches(self, pattern: re.Pattern[str]) -> Self:
        return self.satisfies(
            lambda value: pattern.fullmatch(value) is not None,
            IssueCode.INVALID_FORMAT,
        )


class IntegerValidation(_Validation[int]):
    @staticmethod
    def _is_of_type(value: object) -> bool:
        # bool is a subclass of int, but True isn't a number a client means.
        return isinstance(value, int) and not isinstance(value, bool)

    def min_value(self, minimum: int) -> Self:
        return self.satisfies(lambda value: value >= minimum, IssueCode.TOO_SMALL)

    def max_value(self, maximum: int) -> Self:
        return self.satisfies(lambda value: value <= maximum, IssueCode.TOO_LARGE)
