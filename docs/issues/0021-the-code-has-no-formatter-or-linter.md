---
status: open
resolution:
labels: [question, domain, use_cases, api, infra, bootstrap, docs]
---

# 0021: The code has no formatter or linter

Opened on 2026-10-16.

Nothing checks the formatting or the style of the code: the project has no formatter and no linter, and the conventions of [CONTRIBUTING.md](../../CONTRIBUTING.md) are only kept by review. Whether to adopt one is still to be decided. This issue records what [ruff](https://docs.astral.sh/ruff/) 0.17.1 found when it was tried on commit `8d504a1`, with its default rules and only `target-version = "py312"` set, so that the decision can start from it.

By default, ruff also walks `.claude/`, where the worktrees of the agents keep copies of the code, and they would have to be excluded.

## Formatter

`ruff format` would reformat 31 of the 166 files it reads:

- Python files of every layer and of the tests.
- The migration that Alembic generated, `alembic/versions/f913103e988f_create_the_shorturls_table.py`: single quotes become double quotes and the long calls are broken into several lines. Every new migration would need the same.
- Python code blocks inside Markdown: `docs/shared.md`, and issues 0001, 0003 and 0011. It aligns the comments differently, and in issue 0011 it breaks a call with a long comment into three lines. The content of an issue is append-only (see [the format of issues](README.md#format)), so the Markdown files would have to be excluded, or the rule weighed against the formatter.

## Linter

`ruff check` reports 117 findings, 106 of them fixable automatically:

| Rule     | Findings | What                                                                    |
| -------- | -------- | ----------------------------------------------------------------------- |
| `I001`   | 73       | Unsorted imports                                                        |
| `UP017`  | 20       | `timezone.utc` instead of `UTC`                                         |
| `F401`   | 6        | Unused imports                                                          |
| `UP035`  | 5        | `typing.Callable` and similar instead of `collections.abc`              |
| `UP007`  | 4        | `Union[X, Y]` instead of `X \| Y`                                       |
| `UP045`  | 3        | `Optional[X]` instead of `X \| None`                                    |
| `SIM117` | 2        | Nested `with` statements                                                |
| `PYI034` | 2        | `__new__` doesn't return `Self`                                         |
| `RUF009` | 1        | Function call in a dataclass default                                    |
| `UP047`  | 1        | Generic function without PEP 695 type parameters                        |

- `I001` changes the style of the imports, not only their order: the current code separates `import x` from `from x import y` of the same group with a blank line, and leaves two blank lines after the imports. Ruff joins the third-party imports in one block and keeps one blank line.
- The 6 `F401` are in `shortener/domain/__init__.py`, and are re-exports: ruff asks for an `__all__` or a redundant alias.
- `RUF009` is in `shortener/api/endpoint.py:55`: the default `JSONContent()` of a dataclass field is one instance shared by every instance of the dataclass.
- `PYI034` is in `Slug.__new__` (`shortener/domain/slug.py`) and `TargetURL.__new__` (`shortener/domain/target_url.py`).

Applying the automatic fixes fixes 132 findings, since some fixes reveal others, and leaves 11 to be fixed by hand: the 6 `F401`, the `RUF009`, the 2 `PYI034`, and one `UP007` (`shortener/api/endpoint.py:138`) and one `UP047` (`tests/utils/copy_helpers.py`) whose fixes ruff considers unsafe. Together with the formatter, the change touches 84 files, with 204 lines added and 290 removed, and every layer's tests still pass.
