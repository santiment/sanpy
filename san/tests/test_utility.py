from copy import deepcopy

import pytest

import san
from san.error import SanAuthError, SanError, SanRateLimitError
from san.utility import api_calls_made, api_calls_remaining, is_rate_limit_exception, rate_limit_time_left


class TestIsRateLimitException:
    def test_detects_rate_limit_error_type(self):
        exc = SanRateLimitError("API Rate Limit Reached. Try again in 60 seconds(1 minute)")
        assert is_rate_limit_exception(exc) is True

    def test_detects_rate_limit_by_message(self):
        exc = SanError("API Rate Limit Reached. Try again in 60 seconds(1 minute)")
        assert is_rate_limit_exception(exc) is True

    def test_non_rate_limit_exception(self):
        exc = SanError("Some other error")
        assert is_rate_limit_exception(exc) is False

    def test_regular_exception(self):
        exc = ValueError("API Rate Limit Reached")
        assert is_rate_limit_exception(exc) is True


class TestRateLimitTimeLeft:
    def test_extracts_seconds(self):
        exc = SanRateLimitError("API Rate Limit Reached. Try again in 366 seconds(7 minutes)")
        assert rate_limit_time_left(exc) == 366

    def test_extracts_small_seconds(self):
        exc = SanError("API Rate Limit Reached. Try again in 5 seconds(0 minutes)")
        assert rate_limit_time_left(exc) == 5


class TestApiCallsMade:
    def test_returns_call_history(self, mock_gql_post, test_response):
        san.ApiConfig.api_key = "test_key"
        api_call_result = {
            "currentUser": {
                "apiCallsHistory": [
                    {"datetime": "2024-01-01T00:00:00Z", "apiCallsCount": 10},
                    {"datetime": "2024-01-02T00:00:00Z", "apiCallsCount": 20},
                ]
            }
        }
        mock_gql_post.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

        result = api_calls_made()

        assert len(result) == 2
        assert result[0] == ("2024-01-01T00:00:00Z", 10)
        assert result[1] == ("2024-01-02T00:00:00Z", 20)

    def test_raises_auth_error_without_api_key(self):
        san.ApiConfig.api_key = None
        with pytest.raises(SanAuthError, match="API Key"):
            api_calls_made()


class TestApiCallsRemaining:
    def test_returns_remaining_limits(self, mock_gql_post):
        san.ApiConfig.api_key = "test_key"

        class MockResponse:
            status_code = 200

            def json(self):
                return {"data": {"currentUser": None}}

            @property
            def headers(self):
                return {
                    "x-ratelimit-remaining-month": "5000",
                    "x-ratelimit-remaining-hour": "200",
                    "x-ratelimit-remaining-minute": "10",
                }

        mock_gql_post.return_value = MockResponse()

        result = api_calls_remaining()

        assert result["month_remaining"] == "5000"
        assert result["hour_remaining"] == "200"
        assert result["minute_remaining"] == "10"
