import threading

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from san.api_config import ApiConfig
from san.env_vars import SANBASE_GQL_HOST
from san.error import SanNetworkError, SanTimeoutError, SanTransportError


class RequestsTransport:
    def __init__(self, base_url=SANBASE_GQL_HOST):
        self.base_url = base_url
        self._local = threading.local()

    def execute(self, gql_query_str, headers=None):
        request_headers = headers or {}
        session = self._get_session()

        try:
            return session.post(
                self.base_url,
                json={"query": gql_query_str},
                headers=request_headers,
                timeout=ApiConfig.request_timeout,
            )
        except requests.exceptions.Timeout as exc:
            raise SanTimeoutError(f"Error running query: ({exc})") from exc
        except requests.exceptions.ConnectionError as exc:
            raise SanNetworkError(f"Error running query: ({exc})") from exc
        except requests.exceptions.RequestException as exc:
            raise SanTransportError(f"Error running query: ({exc})") from exc

    def _get_session(self):
        session = getattr(self._local, "session", None)
        config_signature = self._config_signature()
        if session is None or getattr(self._local, "config_signature", None) != config_signature:
            if session is not None:
                session.close()
            session = requests.Session()
            adapter = HTTPAdapter(
                max_retries=self._build_retry_strategy(),
                pool_connections=ApiConfig.pool_connections,
                pool_maxsize=ApiConfig.pool_maxsize,
            )
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            self._local.session = session
            self._local.config_signature = config_signature
        return session

    def _build_retry_strategy(self):
        return Retry(
            total=ApiConfig.request_retry_count,
            connect=ApiConfig.request_retry_count,
            read=ApiConfig.request_retry_count,
            status=ApiConfig.request_retry_count,
            allowed_methods=frozenset(["POST"]),
            status_forcelist=(408, 500, 502, 503, 504),
            backoff_factor=ApiConfig.request_backoff_factor,
            respect_retry_after_header=True,
            raise_on_status=False,
        )

    def _config_signature(self):
        return (
            ApiConfig.request_retry_count,
            ApiConfig.request_backoff_factor,
            ApiConfig.pool_connections,
            ApiConfig.pool_maxsize,
        )
