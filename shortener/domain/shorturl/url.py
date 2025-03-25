class URL(str):
    """A custom string class representing a URL for ShortURL"""

    def __new__(cls, value: str):
        cls._validate_url(value)

    @staticmethod
    def _validate_url(value: str):
        """
        Validate the URL value.

        Args:
            value (str): The URL to be validated.
        
        Returns: 
            None: The URL is valid.

        Raises:
            ...
        """
        