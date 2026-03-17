import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest.mock import patch

import pytest
import requests

from san.api_config import ApiConfig
from san.error import (
    SanAuthError,
    SanEmptyResultError,
    SanNetworkError,
    SanQueryError,
    SanRateLimitError,
    SanServerError,
    SanTimeoutError,
)
from san.graphql import execute_gql, get_response_headers
from san.transport import RequestsTransport


class InvalidJsonResponse:
    status_code = 200
    headers = {}

    def json(self):
        raise ValueError("no json")


class InvalidJsonHttpErrorResponse:
    headers = {}

    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text

    def json(self):
        raise ValueError("no json")


@pytest.fixture(autouse=True)
def restore_api_config():
    original_timeout = ApiConfig.request_timeout
    original_retry_count = ApiConfig.request_retry_count
    original_backoff_factor = ApiConfig.request_backoff_factor
    original_pool_connections = ApiConfig.pool_connections
    original_pool_maxsize = ApiConfig.pool_maxsize

    yield

    ApiConfig.request_timeout = original_timeout
    ApiConfig.request_retry_count = original_retry_count
    ApiConfig.request_backoff_factor = original_backoff_factor
    ApiConfig.pool_connections = original_pool_connections
    ApiConfig.pool_maxsize = original_pool_maxsize


@pytest.mark.parametrize(
    ("status_code", "error_payload", "expected_error"),
    [
        (400, {"errors": {"details": "Invalid apikey"}}, SanAuthError),
        (401, {"errors": {"details": "Unauthorized"}}, SanAuthError),
        (429, {"errors": {"details": "API Rate Limit Reached. Try again in 5 seconds"}}, SanRateLimitError),
        (503, {"errors": {"details": "Service unavailable"}}, SanServerError),
    ],
)
def test_transport_maps_http_errors(status_code, error_payload, expected_error, test_response, monkeypatch):
    response = test_response(status_code=status_code, data=error_payload)
    monkeypatch.setattr("san.transport.requests.Session.post", lambda *args, **kwargs: response)

    with pytest.raises(expected_error):
        execute_gql("{ query_0: projectsAll { slug } }")


def test_transport_maps_graphql_rate_limit_error(test_response, monkeypatch):
    response = test_response(status_code=200, data={"errors": {"details": "API Rate Limit Reached. Try again in 5 seconds"}})
    monkeypatch.setattr("san.transport.requests.Session.post", lambda *args, **kwargs: response)

    with pytest.raises(SanRateLimitError):
        execute_gql("{ query_0: projectsAll { slug } }")


def test_transport_maps_graphql_query_error(test_response, monkeypatch):
    response = test_response(status_code=200, data={"errors": [{"message": "Unknown field", "locations": [{"line": 1, "column": 2}]}]})
    monkeypatch.setattr("san.transport.requests.Session.post", lambda *args, **kwargs: response)

    with pytest.raises(SanQueryError):
        execute_gql("{ query_0: projectsAll { slug } }")


def test_transport_maps_graphql_auth_error(test_response, monkeypatch):
    response = test_response(status_code=200, data={"errors": [{"message": "unauthorized"}]})
    monkeypatch.setattr("san.transport.requests.Session.post", lambda *args, **kwargs: response)

    with pytest.raises(SanAuthError):
        execute_gql("{ query_0: projectsAll { slug } }")


def test_transport_raises_on_partial_graphql_failure(test_response, monkeypatch):
    partial_response = {
        "data": {"query_0": [{"slug": "bitcoin"}], "query_1": None},
        "errors": [{"message": "Field failed", "path": ["query_1"]}],
    }
    response = test_response(status_code=200, data=partial_response)
    monkeypatch.setattr("san.transport.requests.Session.post", lambda *args, **kwargs: response)

    with pytest.raises(SanQueryError):
        execute_gql("{ query_0: projectsAll { slug } query_1: getMetric(metric: \"bad\") { metadata { metric } } }")


def test_transport_raises_empty_result_error(test_response, monkeypatch):
    response = test_response(status_code=200, data={"query_0": None})
    monkeypatch.setattr("san.transport.requests.Session.post", lambda *args, **kwargs: response)

    with pytest.raises(SanEmptyResultError) as exc:
        execute_gql("{ query_0: projectsAll { slug } }")

    assert "results are empty" in str(exc.value)


def test_transport_raises_timeout_error(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout("timed out")

    monkeypatch.setattr("san.transport.requests.Session.post", raise_timeout)

    with pytest.raises(SanTimeoutError):
        execute_gql("{ query_0: projectsAll { slug } }")


def test_transport_raises_connection_error(monkeypatch):
    def raise_connection_error(*args, **kwargs):
        raise requests.exceptions.ConnectionError("connection reset")

    monkeypatch.setattr("san.transport.requests.Session.post", raise_connection_error)

    with pytest.raises(SanNetworkError):
        execute_gql("{ query_0: projectsAll { slug } }")


def test_transport_raises_invalid_json_error(monkeypatch):
    monkeypatch.setattr("san.transport.requests.Session.post", lambda *args, **kwargs: InvalidJsonResponse())

    with pytest.raises(SanQueryError):
        execute_gql("{ query_0: projectsAll { slug } }")


def test_transport_maps_non_json_401_to_auth_error(monkeypatch):
    response = InvalidJsonHttpErrorResponse(status_code=401, text="<html>Unauthorized</html>")
    monkeypatch.setattr("san.transport.requests.Session.post", lambda *args, **kwargs: response)

    with pytest.raises(SanAuthError):
        execute_gql("{ query_0: projectsAll { slug } }")


def test_transport_maps_non_json_429_to_rate_limit_error(monkeypatch):
    response = InvalidJsonHttpErrorResponse(status_code=429, text="Too many requests")
    monkeypatch.setattr("san.transport.requests.Session.post", lambda *args, **kwargs: response)

    with pytest.raises(SanRateLimitError):
        execute_gql("{ query_0: projectsAll { slug } }")


def test_transport_maps_non_json_503_to_server_error(monkeypatch):
    response = InvalidJsonHttpErrorResponse(status_code=503, text="<html>Service unavailable</html>")
    monkeypatch.setattr("san.transport.requests.Session.post", lambda *args, **kwargs: response)

    with pytest.raises(SanServerError):
        execute_gql("{ query_0: projectsAll { slug } }")


def test_get_response_headers_returns_headers(test_response, monkeypatch):
    response = test_response(
        status_code=200,
        data={"query_0": []},
        headers={"x-ratelimit-remaining-minute": "59", "x-ratelimit-remaining-hour": "999", "x-ratelimit-remaining-month": "4999"},
    )
    monkeypatch.setattr("san.transport.requests.Session.post", lambda *args, **kwargs: response)

    headers = get_response_headers("{ query_0: projectsAll { slug } }")

    assert headers["x-ratelimit-remaining-minute"] == "59"


def test_transport_reuses_session_per_thread():
    transport = RequestsTransport()

    session1 = transport._get_session()
    session2 = transport._get_session()

    assert session1 is session2


def test_transport_rebuilds_session_when_retry_config_changes():
    transport = RequestsTransport()

    session1 = transport._get_session()
    ApiConfig.request_retry_count += 1
    session2 = transport._get_session()

    assert session1 is not session2


def test_transport_passes_retry_configuration_to_adapter():
    ApiConfig.request_retry_count = 5
    ApiConfig.request_backoff_factor = 0.75
    ApiConfig.pool_connections = 12
    ApiConfig.pool_maxsize = 24

    transport = RequestsTransport()
    session = transport._get_session()
    https_adapter = session.adapters["https://"]
    retry = https_adapter.max_retries

    assert retry.total == 5
    assert retry.connect == 5
    assert retry.read == 5
    assert retry.status == 5
    assert retry.backoff_factor == 0.75
    assert https_adapter._pool_connections == 12
    assert https_adapter._pool_maxsize == 24


def test_transport_uses_configured_timeout(test_response):
    ApiConfig.request_timeout = (1.0, 9.0)
    response = test_response(status_code=200, data={"query_0": [{"slug": "bitcoin"}]})

    with patch("san.transport.requests.Session.post", return_value=response) as mock_post:
        execute_gql("{ query_0: projectsAll { slug } }")

    assert mock_post.call_args.kwargs["timeout"] == (1.0, 9.0)


def test_transport_retries_until_success_on_retryable_status():
    class RetryHandler(BaseHTTPRequestHandler):
        call_count = 0

        def do_POST(self):
            RetryHandler.call_count += 1
            length = int(self.headers.get("Content-Length", "0"))
            self.rfile.read(length)

            if RetryHandler.call_count < 3:
                self.send_response(503)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"errors": {"details": "Service unavailable"}}).encode())
                return

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"data": {"query_0": [{"slug": "bitcoin"}]}}).encode())

        def log_message(self, format, *args):
            return

    ApiConfig.request_retry_count = 3
    ApiConfig.request_backoff_factor = 0

    server = HTTPServer(("127.0.0.1", 0), RetryHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        transport = RequestsTransport(base_url=f"http://127.0.0.1:{server.server_port}")
        response = transport.execute("{ query_0: projectsAll { slug } }")

        assert response.status_code == 200
        assert response.json() == {"data": {"query_0": [{"slug": "bitcoin"}]}}
        assert RetryHandler.call_count == 3
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)
