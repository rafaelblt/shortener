from collections.abc import Callable
from dataclasses import dataclass
from typing import NoReturn


@dataclass(frozen=True)
class Ok[T]:
    value: T

    def map[U](self, function: Callable[[T], U]) -> "Ok[U]":
        return Ok(function(self.value))

    def unwrap(self) -> T:
        return self.value


@dataclass(frozen=True)
class Err[E]:
    error: E

    def map(self, function: Callable[..., object]) -> "Err[E]":
        return self

    def unwrap(self) -> NoReturn:
        """
        Raises:
            ValueError: Always, with the error as its only argument.
        """
        raise ValueError(self.error)


type Result[T, E] = Ok[T] | Err[E]
