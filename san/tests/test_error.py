import pytest

from san.error import SanAuthError, SanError, SanQueryError, SanRateLimitError, SanValidationError


class TestExceptionHierarchy:
    """Verify that all specific exceptions inherit from SanError for backward compatibility."""

    def test_validation_error_is_san_error(self):
        exc = SanValidationError("bad input")
        assert isinstance(exc, SanError)
        assert isinstance(exc, ValueError)

    def test_rate_limit_error_is_san_error(self):
        exc = SanRateLimitError("rate limited")
        assert isinstance(exc, SanError)
        assert isinstance(exc, ValueError)

    def test_auth_error_is_san_error(self):
        exc = SanAuthError("unauthorized")
        assert isinstance(exc, SanError)
        assert isinstance(exc, ValueError)

    def test_query_error_is_san_error(self):
        exc = SanQueryError("query failed")
        assert isinstance(exc, SanError)
        assert isinstance(exc, ValueError)

    def test_catch_all_with_san_error(self):
        """Existing except SanError blocks should catch all specific types."""
        for exc_class in (SanValidationError, SanRateLimitError, SanAuthError, SanQueryError):
            with pytest.raises(SanError):
                raise exc_class("test")


class TestRateLimitError:
    def test_seconds_left_attribute(self):
        exc = SanRateLimitError("rate limited", seconds_left=60)
        assert exc.seconds_left == 60

    def test_seconds_left_defaults_to_none(self):
        exc = SanRateLimitError("rate limited")
        assert exc.seconds_left is None

    def test_message_preserved(self):
        exc = SanRateLimitError("API Rate Limit Reached. Try again in 60 seconds")
        assert "API Rate Limit Reached" in str(exc)


class TestQueryError:
    def test_status_code_attribute(self):
        exc = SanQueryError("server error", status_code=500)
        assert exc.status_code == 500

    def test_status_code_defaults_to_none(self):
        exc = SanQueryError("query failed")
        assert exc.status_code is None
