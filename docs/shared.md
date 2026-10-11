# Shared

`shortener/shared/` holds code that any layer can use, because it isn't about a layer or a concept of the shortener. It imports nothing from the layers (`domain`, `use_cases`, `adapters` and `infra`).

This document describes `shortener/shared/` as it is in the code.

## Overview

```
shortener/shared/
├── result.py          Result, Ok and Err
├── validation.py      StringValidation, IntegerValidation, ValidationError, ValidationIssue
│                      and IssueCode
├── parsing.py         require_non_empty_string()
└── type_checks.py     check_parameter_type()
```

## Result

`result.py`

`Result[T, E]` is `Ok[T] | Err[E]`, modeled after Rust's `Result`: the outcome of an operation that can fail, returned instead of raising an exception. `Ok` holds the result in `value`, and `Err` holds the failure in `error`. Both are frozen dataclasses, so they compare by content and can be matched:

```python
match result:
    case Ok(value): ...
    case Err(error): ...
```

| Method          | On `Ok(value)`        | On `Err(error)`                                     |
| --------------- | --------------------- | --------------------------------------------------- |
| `map(function)` | `Ok(function(value))` | The same `Err`, without calling `function`          |
| `unwrap()`      | `value`               | Raises `ValueError`, whose only argument is `error` |

## Validation

`validation.py`

`StringValidation(value)` and `IntegerValidation(value)` validate a value with rules chained one after the other, and `result()` ends the chain:

```python
StringValidation(value).min_length(3).max_length(30).result()
IntegerValidation(value).min_value(1).max_value(100).result()
```

Each rule records a `ValidationIssue` when the value breaks it, and the chain goes on, so every broken rule is recorded, in the order of the chain. A value that isn't of the type the class validates gets an `INVALID_TYPE` issue when the validation is created, and every rule is skipped. `StringValidation` validates a `str`, and `IntegerValidation` an `int`, but not a `bool`, even though `bool` is a subclass of `int`.

| Class               | Method                  | Records                                                                                  |
| ------------------- | ----------------------- | ---------------------------------------------------------------------------------------- |
| `StringValidation`  | `min_length(length)`    | `TOO_SHORT` when `len(value) < length`                                                   |
| `StringValidation`  | `max_length(length)`    | `TOO_LONG` when `len(value) > length`                                                    |
| `StringValidation`  | `matches(pattern)`      | `INVALID_FORMAT` when `pattern.fullmatch(value)` is `None`: the whole value has to match |
| `IntegerValidation` | `min_value(minimum)`    | `TOO_SMALL` when `value < minimum`                                                       |
| `IntegerValidation` | `max_value(maximum)`    | `TOO_LARGE` when `value > maximum`                                                       |
| Both                | `satisfies(rule, code)` | `code` when `rule(value)` is false. It adds a rule the methods above don't cover.        |

`result()` returns a [`Result`](#result): `Ok(value)` when no issue was recorded. Otherwise, it returns `Err` with a `ValidationError`: a frozen dataclass whose `issues` holds the recorded `ValidationIssue`s, as a tuple. A `ValidationIssue` is a frozen dataclass with a single field, `code`, an `IssueCode`. The codes describe the kind of rule that was broken, not what was validated, so a code means the same thing wherever it comes from:

| `IssueCode`      | Value              | The value...                       |
| ---------------- | ------------------ | ---------------------------------- |
| `INVALID_TYPE`   | `"invalid_type"`   | isn't of the expected type         |
| `TOO_SHORT`      | `"too_short"`      | is shorter than the minimum length |
| `TOO_LONG`       | `"too_long"`       | is longer than the maximum length  |
| `INVALID_FORMAT` | `"invalid_format"` | doesn't have the expected format   |
| `TOO_SMALL`      | `"too_small"`      | is smaller than the minimum value  |
| `TOO_LARGE`      | `"too_large"`      | is larger than the maximum value   |

## Parsing

`parsing.py`

`require_non_empty_string(value, type_name)` returns `value` when it is a non-empty `str`. Otherwise, it raises `TypeError` if it isn't a `str`, or `ValueError` if it's empty, with `type_name` in the message.

## Type checks

`type_checks.py`

`check_parameter_type(parameter, value, expected_type)` checks the type of a value received by a function. It returns `None` when `value` is an instance of `expected_type`. Otherwise, it raises `TypeError` with a message naming the parameter, the expected type and the type received, such as `The now parameter must be an instance of datetime, got str`. The check uses `isinstance`, so subclasses pass.
