import pytest

from san.error import SanValidationError
from san.sanitize import (
    sanitize_gql_string,
    validate_address,
    validate_interval,
    validate_metric,
    validate_positive_int,
    validate_slug,
)


class TestSanitizeGqlString:
    def test_clean_string_unchanged(self):
        assert sanitize_gql_string("bitcoin") == "bitcoin"

    def test_escapes_double_quotes(self):
        assert sanitize_gql_string('bit"coin') == 'bit\\"coin'

    def test_escapes_backslashes(self):
        assert sanitize_gql_string("bit\\coin") == "bit\\\\coin"

    def test_escapes_newlines(self):
        assert sanitize_gql_string("bit\ncoin") == "bit\\ncoin"

    def test_escapes_carriage_returns(self):
        assert sanitize_gql_string("bit\rcoin") == "bit\\rcoin"

    def test_escapes_combined_injection(self):
        # Simulates a GraphQL injection attempt
        result = sanitize_gql_string('bitcoin"}, mutation: {something}')
        assert '"' not in result.replace('\\"', "")

    def test_empty_string(self):
        assert sanitize_gql_string("") == ""


class TestValidateSlug:
    def test_valid_slug(self):
        assert validate_slug("bitcoin") == "bitcoin"

    def test_valid_slug_with_hyphens(self):
        assert validate_slug("my-token") == "my-token"

    def test_valid_slug_with_underscores(self):
        assert validate_slug("my_token") == "my_token"

    def test_empty_slug_raises(self):
        with pytest.raises(SanValidationError, match="Invalid slug"):
            validate_slug("")

    def test_none_slug_raises(self):
        with pytest.raises(SanValidationError, match="Invalid slug"):
            validate_slug(None)

    def test_injection_slug_raises(self):
        with pytest.raises(SanValidationError, match="Invalid slug"):
            validate_slug('bitcoin"}, mutation: {delete}')


class TestValidateMetric:
    def test_valid_metric(self):
        assert validate_metric("daily_active_addresses") == "daily_active_addresses"

    def test_empty_metric_raises(self):
        with pytest.raises(SanValidationError, match="Invalid metric"):
            validate_metric("")

    def test_metric_with_special_chars_raises(self):
        with pytest.raises(SanValidationError, match="Invalid metric"):
            validate_metric("metric/hack")


class TestValidateInterval:
    def test_valid_intervals(self):
        assert validate_interval("1d") == "1d"
        assert validate_interval("4h") == "4h"
        assert validate_interval("30m") == "30m"
        assert validate_interval("1w") == "1w"

    def test_invalid_interval(self):
        with pytest.raises(SanValidationError, match="Invalid interval"):
            validate_interval("invalid")

    def test_non_string_interval(self):
        with pytest.raises(SanValidationError, match="Invalid interval"):
            validate_interval(123)


class TestValidateAddress:
    def test_valid_address(self):
        addr = "0x1f3df0b8390bb8e9e322972c5e75583e87608ec2"
        assert validate_address(addr) == addr

    def test_invalid_address_no_prefix(self):
        with pytest.raises(SanValidationError, match="Invalid address"):
            validate_address("1f3df0b8390bb8e9e322972c5e75583e87608ec2")

    def test_invalid_address_too_short(self):
        with pytest.raises(SanValidationError, match="Invalid address"):
            validate_address("0x1234")

    def test_empty_address_raises(self):
        with pytest.raises(SanValidationError, match="Invalid address"):
            validate_address("")


class TestValidatePositiveInt:
    def test_valid_int(self):
        assert validate_positive_int(5, "limit") == 5

    def test_valid_string_int(self):
        assert validate_positive_int("10", "limit") == 10

    def test_zero_is_valid(self):
        assert validate_positive_int(0, "limit") == 0

    def test_negative_raises(self):
        with pytest.raises(SanValidationError, match="non-negative"):
            validate_positive_int(-1, "limit")

    def test_non_numeric_raises(self):
        with pytest.raises(SanValidationError, match="positive integer"):
            validate_positive_int("abc", "limit")
