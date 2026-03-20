class ApiConfig:
    api_key = None
    request_timeout = (3.05, 30)
    request_retry_count = 3
    request_backoff_factor = 0.5
    pool_connections = 10
    pool_maxsize = 10
