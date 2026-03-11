import pytest
import requests

from san.error import SanAuthError, SanRateLimitError, SanServerError, SanTimeoutError
from san.graphql import execute_gql, get_response_headers


@pytest.mark.parametrize(
    ("status_code", "error_payload", "expected_error"),
    [
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


def test_transport_raises_timeout_error(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout("timed out")

    monkeypatch.setattr("san.transport.requests.Session.post", raise_timeout)

    with pytest.raises(SanTimeoutError):
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
