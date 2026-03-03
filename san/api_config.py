class ApiConfig:
    """Global configuration for the sanpy SDK.

    Attributes:
        api_key: Santiment API key for accessing restricted metrics.
            Can also be set via the SANPY_APIKEY environment variable.
        user_agent: Custom User-Agent header for API requests.
        request_timeout: HTTP request timeout in seconds (default 60).
        max_retries: Max retries for transient failures (default 3).
        retry_base_delay: Base delay in seconds for exponential backoff.
            Actual delay = retry_base_delay * 2^attempt (default 1.0).
    """

    api_key: str | None = None
    user_agent: str | None = None
    request_timeout: float = 60.0
    max_retries: int = 3
    retry_base_delay: float = 1.0
