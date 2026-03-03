import datetime

from san.sanbase_graphql_helper import (
    _format_from_date,
    _format_to_date,
    _parse_iso_date,
    transform_query_args,
    transform_selector,
)


class TestParseIsoDate:
    def test_parses_full_iso_with_tz(self):
        dt = _parse_iso_date("2024-01-15T12:30:00+00:00")
        assert dt.tzinfo is not None
        assert dt.year == 2024
        assert dt.month == 1

    def test_parses_z_suffix(self):
        dt = _parse_iso_date("2024-01-15T12:30:00Z")
        assert dt.tzinfo is not None
        assert dt.year == 2024

    def test_naive_date_gets_utc(self):
        dt = _parse_iso_date("2024-01-15")
        assert dt.tzinfo == datetime.timezone.utc
        assert dt.hour == 0

    def test_naive_datetime_gets_utc(self):
        dt = _parse_iso_date("2024-01-15T12:30:00")
        assert dt.tzinfo == datetime.timezone.utc

    def test_preserves_existing_tz(self):
        dt = _parse_iso_date("2024-01-15T12:30:00+05:00")
        assert dt.utcoffset() == datetime.timedelta(hours=5)


class TestFormatFromDate:
    def test_string_date(self):
        result = _format_from_date("2024-01-15")
        assert "+00:00" in result or "Z" in result

    def test_datetime_object(self):
        dt = datetime.datetime(2024, 1, 15, tzinfo=datetime.timezone.utc)
        result = _format_from_date(dt)
        assert "2024-01-15" in result

    def test_utc_now_passthrough(self):
        result = _format_from_date("utc_now-30d")
        assert result == "utc_now-30d"

    def test_iso_string_with_tz(self):
        result = _format_from_date("2024-01-15T00:00:00+00:00")
        assert "2024-01-15" in result


class TestFormatToDate:
    def test_date_only_adds_end_of_day(self):
        result = _format_to_date("2024-01-15")
        assert "23:59:59" in result

    def test_datetime_string_preserves_time(self):
        result = _format_to_date("2024-01-15T12:30:00+00:00")
        assert "12:30:00" in result

    def test_datetime_object(self):
        dt = datetime.datetime(2024, 1, 15, 12, 0, tzinfo=datetime.timezone.utc)
        result = _format_to_date(dt)
        assert "2024-01-15" in result

    def test_utc_now_passthrough(self):
        result = _format_to_date("utc_now")
        assert result == "utc_now"


class TestTransformSelector:
    def test_string_value(self):
        result = transform_selector({"slug": "bitcoin"})
        assert 'slug: "bitcoin"' in result

    def test_int_value(self):
        result = transform_selector({"limit": 10})
        assert "limit: 10" in result

    def test_numeric_string(self):
        result = transform_selector({"limit": "10"})
        assert "limit: 10" in result

    def test_nested_dict(self):
        result = transform_selector({"owner": {"slug": "bitcoin"}})
        assert "owner:" in result
        assert "bitcoin" in result

    def test_list_value(self):
        result = transform_selector({"slugs": ["bitcoin", "ethereum"]})
        assert '"bitcoin"' in result
        assert '"ethereum"' in result


class TestTransformQueryArgs:
    def test_defaults(self):
        result = transform_query_args("prices")
        assert "from_date" in result
        assert "to_date" in result
        assert result["interval"] == "1d"
        assert result["aggregation"] == "null"
        assert result["include_incomplete_data"] == "false"

    def test_custom_interval(self):
        result = transform_query_args("prices", interval="1h")
        assert result["interval"] == "1h"

    def test_include_incomplete_data_true(self):
        result = transform_query_args("prices", include_incomplete_data=True)
        assert result["include_incomplete_data"] == "true"

    def test_selector_transform(self):
        result = transform_query_args("prices", selector={"slug": "bitcoin"})
        assert "selector:" in result["selector"]
        assert "bitcoin" in result["selector"]
