# Issues

Until the repository is on GitHub, its issues live here, one Markdown file per issue. They follow the GitHub model: an issue has a state that changes, and a conversation that only grows.

## When to open one

An issue records a problem or a question to be handled apart from the task where it came up. Open one for:

- A problem found during a task, but outside its scope, that has to be analyzed and fixed separately. For example, [issue 0011](0011-copying-a-parsed-value-object-that-breaks-the-rules-raises-value-error.md) was found while implementing the plan of the use cases, and was a problem of the domain, which that task didn't cover.
- A problem complex enough to need a deeper investigation before it is fixed.
- A problem or a question that can be left for later, because it has little impact for now. For example, [issue 0009](0009-listing-short-urls-has-no-pagination.md): pagination wasn't in the initial plan of the use cases, because it still needed more thought, and it can be added later in the phase.

## Files

The file name is `<number>-<title-in-kebab-case>.md`, for example `0001-slug-length-error-messages-are-swapped.md`. The number is the issue's ID: a new issue takes the highest number plus one, and numbers are never reused. The file name and the title never change.

Refer to an issue as `issue 0001`, without `#`: once the repository is on GitHub, `#1` would link to GitHub's own issue 1.

## Format

```markdown
---
status: closed
resolution: fixed
labels: [bug, domain]
---

# 0001: The slug length error messages are swapped

Opened on 2026-10-06.

What happens, how to reproduce it, where in the code.

## 2026-10-09: Closed as fixed

What changed in the code.
```

An issue has two parts.

**The state** is the front matter, and is the only part that can be edited:

- `status`: `open` or `closed`.
- `resolution`: empty while the issue is open. When it is closed, one of:

  | Resolution     | When                                                              |
  | -------------- | ----------------------------------------------------------------- |
  | `fixed`        | The problem was fixed in the code.                                |
  | `not-an-issue` | A later check found that it wasn't a problem.                     |
  | `duplicate`    | Another issue covers the same problem.                            |
  | `wont-fix`     | The problem is real, but it was decided not to fix it.            |
  | `obsolete`     | The code it was about was removed or rewritten for another reason. |

- `labels`: one type (`bug`, `refactor`, `question` or `todo`) and the layers involved (`domain`, `use_cases`, `api`, `consumer`, `infra`, `bootstrap` or `docs`, and `adapters`, the name of the API before the restructuring). A new label is added to this list before it is used.

**The content** is everything after the front matter: the title, the opening text and the entries. It is append-only: what is written is never edited or deleted, and new text goes at the end. A correction is a new entry that says what was wrong. Its links lead to where things were when they were written, and aren't updated when a document or a heading moves.

- The opening text starts with the date, and describes what was observed: what happens, how to reproduce it and where in the code. It states the expected behavior only when something already defines it, such as an error message, a docstring or the documentation. Otherwise, it says that it is still to be decided.
- Each entry has a `## <date>: <summary>` heading. Every change of `status` or `resolution` comes with an entry whose summary says it, such as `Closed as fixed` or `Reopened`, and whose text explains it: what changed in the code, which issue it duplicates, what the check found.

## Workflow

- **Open:** create the file with `status: open`.
- **Close:** set `status: closed` and the `resolution`, and add the closing entry. When a commit fixes the issue, the same commit closes it, and its body says `Closes issue 0001.`
- **Reopen:** set `status: open`, empty the `resolution`, and add a `Reopened` entry that says why.

## Listing

```bash
grep -l '^status: open' docs/issues/[0-9]*.md
grep -l '^labels: .*\bdomain\b' docs/issues/[0-9]*.md
```
