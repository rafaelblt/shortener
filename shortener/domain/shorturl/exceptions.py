class ShortURLException(Exception):
    """Base Exception for ShortURL"""
    pass

class SlugAlreadyExistsException(ShortURLException): ...
