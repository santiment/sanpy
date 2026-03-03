class ApiConfig:
    api_key: str | None = None
    user_agent: str | None = None
    request_timeout: float = 60.0
    max_retries: int = 3
    retry_base_delay: float = 1.0
