class SanError(ValueError):
    """Base exception for all sanpy errors.

    All specific exception types inherit from this, so existing
    ``except SanError`` blocks will continue to work.
    """

    pass


class SanValidationError(SanError):
    """Raised when user-provided input fails validation before an API call.

    Examples: invalid slug, invalid metric name, missing required arguments.
    """

    pass


class SanRateLimitError(SanError):
    """Raised when the Santiment API returns a rate-limit response.

    The ``seconds_left`` attribute contains the retry delay when available.
    """

    def __init__(self, message: str, seconds_left: int | None = None) -> None:
        super().__init__(message)
        self.seconds_left = seconds_left


class SanAuthError(SanError):
    """Raised for authentication or authorization failures.

    Examples: missing API key, invalid API key, 401/403 HTTP responses.
    """

    pass


class SanQueryError(SanError):
    """Raised when a GraphQL query execution fails on the server side.

    Examples: GraphQL errors, empty results, non-200 HTTP status codes
    (other than 401/403/429).
    """

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
