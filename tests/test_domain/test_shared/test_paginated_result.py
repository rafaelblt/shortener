import pytest
from shortener.domain.shared.pagination import PaginatedResult


def test_paginated_result_attributes():
    items = [1, 2, 3]
    total = 10
    offset = 0
    limit = 3

    result = PaginatedResult(items, total, offset, limit)

    assert result.items == items
    assert result.total == total
    assert result.offset == offset
    assert result.limit == limit


@pytest.mark.parametrize(
    "offset, limit, expected",
    [
        (0, 3, 1),
        (3, 3, 2),
        (6, 3, 3),
    ]
)
def test_current_page(offset, limit, expected):
    result = PaginatedResult(items=[], total=10, offset=offset, limit=limit)
    assert result.current_page == expected


@pytest.mark.parametrize(
    "total, limit, expected",
    [
        (10, 3, 4),
        (9, 3, 3),
        (0, 3, 0),
    ]
)
def test_total_pages(total, limit, expected):
    result = PaginatedResult(items=[], total=total, offset=0, limit=limit)
    assert result.total_pages == expected


@pytest.mark.parametrize(
    "offset, limit, total, expected",
    [
        (0, 3, 10, True),
        (9, 3, 10, False),
        (10, 3, 10, False),
    ]
)
def test_has_next(offset, limit, total, expected):
    result = PaginatedResult(items=[], total=total, offset=offset, limit=limit)
    assert result.has_next == expected


@pytest.mark.parametrize(
    "offset, limit, expected",
    [
        (0, 3, False),
        (3, 3, True),
        (6, 3, True),
    ]
)
def test_has_previous(offset, limit, expected):
    result = PaginatedResult(items=[], total=10, offset=offset, limit=limit)
    assert result.has_previous == expected


def test_empty_result():
    result = PaginatedResult(items=[], total=0, offset=0, limit=3)
    assert result.items == []
    assert result.total == 0
    assert result.offset == 0
    assert result.limit == 3
    assert result.current_page == 1
    assert result.total_pages == 0
    assert result.has_next is False
    assert result.has_previous is False
