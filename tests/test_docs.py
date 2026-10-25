"""
Checks that the links of the documents, and the references of the code to
them, lead to a file and a heading that exist.
"""

import re

from pathlib import Path
from typing import Final

import pytest


ROOT: Final = Path(__file__).parents[1]
DOCUMENTS: Final = sorted([*ROOT.glob("*.md"), *ROOT.glob("docs/**/*.md")])
CODE: Final = sorted(
    [
        *ROOT.glob("shortener/**/*.py"),
        *ROOT.glob("tests/**/*.py"),
        *ROOT.glob("alembic/**/*.py"),
        ROOT / "compose.yaml",
        ROOT / ".env.example",
    ]
)

FENCED_BLOCK: Final = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
INLINE_CODE: Final = re.compile(r"`[^`\n]*`")
MARKDOWN_LINK: Final = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
HEADING: Final = re.compile(r"^#{1,6} (.+)$", re.MULTILINE)
# A document the code names, as a comment does with "See docs/<file>#<heading>".
CODE_REFERENCE: Final = re.compile(
    r"\b((?:docs/[\w./-]+|[A-Z]+)\.(?:md|yaml)(?:#[\w-]+)?)"
)


def anchors_of(document: Path) -> set[str]:
    """The anchors GitHub gives the headings of the document."""
    anchors: set[str] = set()
    for heading in HEADING.findall(FENCED_BLOCK.sub("", document.read_text())):
        anchor = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        repeated = anchor
        count = 1
        while repeated in anchors:
            repeated = f"{anchor}-{count}"
            count += 1
        anchors.add(repeated)
    return anchors


def broken(target: Path, anchor: str) -> bool:
    if not target.exists():
        return True
    return bool(anchor) and target.suffix == ".md" and anchor not in anchors_of(target)


def links_of(document: Path) -> list[str]:
    text = INLINE_CODE.sub("", FENCED_BLOCK.sub("", document.read_text()))
    return [
        link
        for link in MARKDOWN_LINK.findall(text)
        if not re.match(r"[a-z]+:", link)  # http:, https: and mailto:
    ]


@pytest.mark.parametrize(
    "document",
    [pytest.param(path, id=str(path.relative_to(ROOT))) for path in DOCUMENTS],
)
def test_the_links_of_the_document_lead_to_a_file_and_a_heading(document: Path):
    broken_links = []
    for link in links_of(document):
        path, _, anchor = link.partition("#")
        target = (document.parent / path).resolve() if path else document
        if broken(target, anchor):
            broken_links.append(link)
    assert broken_links == []


@pytest.mark.parametrize(
    "file", [pytest.param(path, id=str(path.relative_to(ROOT))) for path in CODE]
)
def test_the_documents_the_code_names_have_the_heading_it_names(file: Path):
    broken_references = []
    for reference in CODE_REFERENCE.findall(file.read_text()):
        path, _, anchor = reference.partition("#")
        if broken(ROOT / path, anchor):
            broken_references.append(reference)
    assert broken_references == []
