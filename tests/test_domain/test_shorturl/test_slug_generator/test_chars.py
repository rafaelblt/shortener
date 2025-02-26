import string

def test_chars(shorturl_slug_generator):
    assert shorturl_slug_generator.chars == string.ascii_letters + string.digits
