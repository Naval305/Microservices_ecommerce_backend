class EmailAlreadyExistsError(Exception):
    """Raised when attempting to create a user with an existing email."""

    pass


class TokenReuseDetectedError(Exception):
    """Raised when a refresh token is reused after being rotated."""

    pass


class InvalidTokenError(Exception):
    """Raised when an invalid token is provided."""

    pass


class UnauthorizedError(Exception):
    """Raised when a user attempts to access a resource without proper authorization."""

    pass


class UserNotFoundError(Exception):
    """Raised when a user is not found."""

    pass


class RedisUnavailableError(Exception):
    """Raised when Redis is unavailable for a non-degradable operation."""

    pass
