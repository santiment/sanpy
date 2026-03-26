class SanError(ValueError):
    pass


class SanTransportError(SanError):
    pass


class SanNetworkError(SanTransportError):
    pass


class SanTimeoutError(SanNetworkError):
    pass


class SanAuthError(SanError):
    pass


class SanRateLimitError(SanError):
    pass


class SanResponseSizeLimitError(SanError):
    pass


class SanServerError(SanError):
    pass


class SanGraphqlQueryError(SanError):
    pass


class SanEmptyResultError(SanError):
    pass


class SanPartialResultWarning(UserWarning):
    pass


SanQueryError = SanGraphqlQueryError
