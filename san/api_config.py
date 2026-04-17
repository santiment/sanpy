class ApiConfig:
    api_key = None
    # Match requests' historical default connect timeout while giving reads more time.
    # Tuple form is (connect_timeout, read_timeout).
    request_timeout = (3.05, 30)
    request_retry_count = 3
    request_backoff_factor = 0.5
    # Number of connection pools to cache across different hosts/schemes.
    pool_connections = 10
    # Maximum number of reusable connections kept per pool.
    pool_maxsize = 10
    # When True, passing unknown keyword arguments to san.get / san.get_many /
    # AsyncBatch raises SanError instead of being silently ignored.
    strict_kwargs = True
