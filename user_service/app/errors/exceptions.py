class EmailAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing email."""

    pass

class TokenReuseDetectedError(Exception):
    """Raised when a refresh token is reused after being rotated."""

    pass