import logging
from unittest.mock import patch

import httpx
import pytest

from san.api_config import ApiConfig
from san.error import SanAuthError, SanQueryError, SanRateLimitError
from san.graphql import (
    _build_headers,
    _extract_error_details,
    _is_retryable,
    _raise_status_error,
    _redact_headers,
    _retry_delay,
    execute_gql,
)


class TestBuildHeaders:
    def test_includes_user_agent(self):
        headers = _build_headers()
        assert "User-Agent" in headers
        assert "sanpy/" in headers["User-Agent"]

    @patch("san.graphql.ApiConfig")
    def test_includes_api_key_when_set(self, mock_config):
        mock_config.api_key = "test_key_123"
        mock_config.user_agent = None
        headers = _build_headers()
        assert headers["authorization"] == "Apikey test_key_123"

    @patch("san.graphql.ApiConfig")
    def test_no_auth_when_no_key(self, mock_config):
        mock_config.api_key = None
        mock_config.user_agent = None
        headers = _build_headers()
        assert "authorization" not in headers

    @patch("san.graphql.ApiConfig")
    def test_custom_user_agent(self, mock_config):
        mock_config.api_key = None
        mock_config.user_agent = "custom-agent/1.0"
        headers = _build_headers()
        assert headers["User-Agent"] == "custom-agent/1.0"


class TestExtractErrorDetails:
    def test_extracts_details_from_error_response(self, test_response):
        response = test_response(status_code=500, data={"errors": {"details": "Something went wrong"}})
        result = _extract_error_details(response)
        assert result == "Something went wrong"

    def test_returns_empty_for_no_errors(self, test_response):
        response = test_response(status_code=200, data={"some": "value"})
        result = _extract_error_details(response)
        assert result == ""

    def test_handles_missing_details_key(self, test_response):
        response = test_response(status_code=500, data={"errors": {"message": "error"}})
        result = _extract_error_details(response)
        assert result == ""


class TestExecuteGql:
    def test_successful_query(self, mock_gql_post, test_response):
        mock_gql_post.return_value = test_response(
            status_code=200,
            data={"query_0": [{"value": 1}]},
        )
        result = execute_gql("{query_0: getMetric}")
        assert "query_0" in result

    def test_error_status_raises_query_error(self, mock_gql_post, test_response):
        mock_gql_post.return_value = test_response(
            status_code=500,
            data={"errors": {"details": "Internal error"}},
        )
        with pytest.raises(SanQueryError, match="Status code: 500"):
            execute_gql("{query_0: getMetric}")

    def test_empty_result_raises_query_error(self, mock_gql_post, test_response):
        mock_gql_post.return_value = test_response(status_code=200, data={"query_0": None})
        with pytest.raises(SanQueryError, match="results are empty"):
            execute_gql("{query_0: getMetric}")

    def test_rate_limit_response_raises_rate_limit_error(self, mock_gql_post, test_response):
        mock_gql_post.return_value = test_response(
            status_code=429,
            data={"errors": {"details": "API Rate Limit Reached"}},
        )
        with pytest.raises(SanRateLimitError):
            execute_gql("{query_0: getMetric}")

    def test_auth_error_response_raises_auth_error(self, mock_gql_post, test_response):
        mock_gql_post.return_value = test_response(
            status_code=401,
            data={"errors": {"details": "Unauthorized"}},
        )
        with pytest.raises(SanAuthError):
            execute_gql("{query_0: getMetric}")

    def test_403_raises_auth_error(self, mock_gql_post, test_response):
        mock_gql_post.return_value = test_response(
            status_code=403,
            data={"errors": {"details": "Forbidden"}},
        )
        with pytest.raises(SanAuthError):
            execute_gql("{query_0: getMetric}")

    def test_network_error_raises_query_error(self, mock_gql_post):
        mock_gql_post.side_effect = httpx.ConnectError("Connection refused")
        with pytest.raises(SanQueryError, match="Error running query"):
            execute_gql("{query_0: getMetric}")

    def test_graphql_error_in_200_raises_query_error(self, mock_gql_post, test_response):
        mock_gql_post.return_value = test_response(
            status_code=200,
            data={"errors": [{"message": "Field 'x' not found"}]},
        )
        with pytest.raises(SanQueryError, match="GraphQL error"):
            execute_gql("{query_0: getMetric}")

    def test_graphql_rate_limit_in_200_raises_rate_limit_error(self, mock_gql_post, test_response):
        mock_gql_post.return_value = test_response(
            status_code=200,
            data={"errors": [{"message": "API Rate Limit Reached. Try again in 60 seconds"}]},
        )
        with pytest.raises(SanRateLimitError):
            execute_gql("{query_0: getMetric}")

    def test_uses_configurable_timeout(self, mock_gql_post, test_response):
        mock_gql_post.return_value = test_response(
            status_code=200,
            data={"query_0": [{"value": 1}]},
        )
        original = ApiConfig.request_timeout
        try:
            ApiConfig.request_timeout = 30.0
            execute_gql("{query_0: getMetric}")
            _, call_kwargs = mock_gql_post.call_args
            assert call_kwargs["timeout"] == 30.0
        finally:
            ApiConfig.request_timeout = original

    def test_debug_logging(self, mock_gql_post, test_response, caplog):
        mock_gql_post.return_value = test_response(
            status_code=200,
            data={"query_0": [{"value": 1}]},
        )
        with caplog.at_level(logging.DEBUG, logger="sanpy"):
            execute_gql("{query_0: getMetric}")
        assert any("GQL request" in r.message for r in caplog.records)
        assert any("Response status" in r.message for r in caplog.records)


class TestRetry:
    def test_retries_on_rate_limit(self, mock_gql_post, test_response):
        ApiConfig.max_retries = 2
        ApiConfig.retry_base_delay = 0.0  # no actual delay in tests
        mock_gql_post.side_effect = [
            test_response(status_code=429, data={"errors": {"details": "API Rate Limit Reached"}}),
            test_response(status_code=200, data={"query_0": [{"value": 1}]}),
        ]
        result = execute_gql("{query_0: getMetric}")
        assert "query_0" in result
        assert mock_gql_post.call_count == 2

    def test_retries_on_server_error(self, mock_gql_post, test_response):
        ApiConfig.max_retries = 2
        ApiConfig.retry_base_delay = 0.0
        mock_gql_post.side_effect = [
            test_response(status_code=500, data={"errors": {"details": "Server error"}}),
            test_response(status_code=200, data={"query_0": [{"value": 1}]}),
        ]
        result = execute_gql("{query_0: getMetric}")
        assert "query_0" in result

    def test_retries_on_connection_error(self, mock_gql_post, test_response):
        ApiConfig.max_retries = 2
        ApiConfig.retry_base_delay = 0.0
        mock_gql_post.side_effect = [
            httpx.ConnectError("Connection refused"),
            test_response(status_code=200, data={"query_0": [{"value": 1}]}),
        ]
        result = execute_gql("{query_0: getMetric}")
        assert "query_0" in result

    def test_does_not_retry_auth_error(self, mock_gql_post, test_response):
        ApiConfig.max_retries = 2
        ApiConfig.retry_base_delay = 0.0
        mock_gql_post.return_value = test_response(
            status_code=401, data={"errors": {"details": "Unauthorized"}},
        )
        with pytest.raises(SanAuthError):
            execute_gql("{query_0: getMetric}")
        assert mock_gql_post.call_count == 1

    def test_raises_after_max_retries_exhausted(self, mock_gql_post, test_response):
        ApiConfig.max_retries = 2
        ApiConfig.retry_base_delay = 0.0
        mock_gql_post.return_value = test_response(
            status_code=429, data={"errors": {"details": "API Rate Limit Reached"}},
        )
        with pytest.raises(SanRateLimitError):
            execute_gql("{query_0: getMetric}")
        assert mock_gql_post.call_count == 3  # initial + 2 retries

    def test_exponential_backoff_delay(self):
        original = ApiConfig.retry_base_delay
        ApiConfig.retry_base_delay = 1.0
        assert _retry_delay(0) == 1.0
        assert _retry_delay(1) == 2.0
        assert _retry_delay(2) == 4.0
        ApiConfig.retry_base_delay = original


class TestIsRetryable:
    def test_rate_limit_is_retryable(self):
        assert _is_retryable(SanRateLimitError("rate limited")) is True

    def test_connection_error_is_retryable(self):
        assert _is_retryable(httpx.ConnectError("refused")) is True

    def test_server_error_is_retryable(self):
        assert _is_retryable(SanQueryError("error", status_code=500)) is True
        assert _is_retryable(SanQueryError("error", status_code=502)) is True

    def test_auth_error_is_not_retryable(self):
        assert _is_retryable(SanAuthError("unauthorized")) is False

    def test_client_error_is_not_retryable(self):
        assert _is_retryable(SanQueryError("error", status_code=400)) is False

    def test_query_error_without_status_is_not_retryable(self):
        assert _is_retryable(SanQueryError("error")) is False


class TestRedactHeaders:
    def test_redacts_authorization(self):
        headers = {"User-Agent": "sanpy/1.0", "authorization": "Apikey secret123"}
        redacted = _redact_headers(headers)
        assert redacted["authorization"] == "Apikey ***"
        assert redacted["User-Agent"] == "sanpy/1.0"

    def test_does_not_modify_original(self):
        headers = {"authorization": "Apikey secret123"}
        _redact_headers(headers)
        assert headers["authorization"] == "Apikey secret123"

    def test_no_auth_header(self):
        headers = {"User-Agent": "sanpy/1.0"}
        redacted = _redact_headers(headers)
        assert redacted == headers


class TestRaiseStatusError:
    def test_429_raises_rate_limit(self, test_response):
        response = test_response(status_code=429, data={"errors": {"details": "Rate limited"}})
        with pytest.raises(SanRateLimitError):
            _raise_status_error(response, "test query")

    def test_rate_limit_marker_in_body(self, test_response):
        response = test_response(status_code=500, data={"errors": {"details": "API Rate Limit Reached"}})
        with pytest.raises(SanRateLimitError):
            _raise_status_error(response, "test query")

    def test_401_raises_auth_error(self, test_response):
        response = test_response(status_code=401, data={"errors": {"details": "Unauthorized"}})
        with pytest.raises(SanAuthError):
            _raise_status_error(response, "test query")

    def test_500_raises_query_error_with_status(self, test_response):
        response = test_response(status_code=500, data={"errors": {"details": "Server error"}})
        with pytest.raises(SanQueryError) as exc_info:
            _raise_status_error(response, "test query")
        assert exc_info.value.status_code == 500
