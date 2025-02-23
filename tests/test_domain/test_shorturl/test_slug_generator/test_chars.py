import string

def test_chars(generator):
    assert generator.chars == string.ascii_letters + string.digits
