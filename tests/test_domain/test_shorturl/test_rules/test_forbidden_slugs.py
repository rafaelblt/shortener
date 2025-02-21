from pytest import mark

from shortener.domain.shorturl.rules.forbidden_slugs import (
    FORBIDDEN_SLUGS, is_slug_forbidden
)


def test_type_forbidden_slugs():
    assert FORBIDDEN_SLUGS.__class__ == set


@mark.parametrize(
    "slug,expected", 
    [
        ("admin", True),       
        ("LOGIN", True),       
        ("logout", True),      
        ("dashboard", True),   
        ("Api", True),         
        ("Config", True),      
        ("random", False),     
        ("user123", False),    
        ("about-us", False),   
        ("helpdesk", False)    
    ]
)
def test_is_slug_fobidden(slug, expected):
    assert is_slug_forbidden(slug) == expected
