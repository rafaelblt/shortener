from shortener.api.openapi import documented_headers


def test_documented_headers_describes_each_header_as_a_string():
    documented = documented_headers({"Location": "The URL of the value."})

    assert documented == {
        "headers": {
            "Location": {
                "description": "The URL of the value.",
                "schema": {"type": "string"},
            }
        }
    }


def test_documented_headers_is_empty_for_no_headers():
    assert documented_headers({}) == {}
