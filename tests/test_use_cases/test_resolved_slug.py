from dataclasses import FrozenInstanceError

import pytest

from shortener.domain import TargetURL
from shortener.use_cases.resolved_slug import ResolvedSlug


def test_from_target_url_keeps_the_target_url_as_a_plain_string():
    resolved = ResolvedSlug.from_target_url(TargetURL("https://example.com"))
    assert resolved == ResolvedSlug(target_url="https://example.com")
    assert type(resolved.target_url) is str


def test_is_immutable():
    resolved = ResolvedSlug.from_target_url(TargetURL("https://example.com"))
    with pytest.raises(FrozenInstanceError):
        resolved.target_url = "https://other.example.com"  # type: ignore[misc]
