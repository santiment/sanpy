import pytest

import san.sanbase_graphql as sgql
from san.error import SanValidationError


class TestSimpleSlugQueries:
    def test_prices_generates_query(self):
        result = sgql.prices(0, "bitcoin", from_date="2024-01-01", to_date="2024-01-31", interval="1d")
        assert "historyPrice" in result
        assert '"bitcoin"' in result
        assert "query_0" in result

    def test_ohlc_generates_query(self):
        result = sgql.ohlc(0, "ethereum", from_date="2024-01-01", to_date="2024-01-31", interval="1d")
        assert "ohlc" in result
        assert '"ethereum"' in result

    def test_miners_balance_generates_query(self):
        result = sgql.miners_balance(0, "bitcoin", from_date="2024-01-01", to_date="2024-01-31", interval="1d")
        assert "minersBalance" in result


class TestCustomTemplateQueries:
    def test_historical_balance(self):
        result = sgql.historical_balance(
            0, "santiment",
            address="0x1f3df0b8390bb8e9e322972c5e75583e87608ec2",
            from_date="2024-01-01", to_date="2024-01-31", interval="1d",
        )
        assert "historicalBalance" in result
        assert "0x1f3df0b8390bb8e9e322972c5e75583e87608ec2" in result
        assert '"santiment"' in result

    def test_top_holders_percent(self):
        result = sgql.top_holders_percent_of_total_supply(
            0, "bitcoin",
            number_of_holders=10,
            from_date="2024-01-01", to_date="2024-01-31",
        )
        assert "topHoldersPercentOfTotalSupply" in result
        assert "numberOfHolders: 10" in result

    def test_top_transfers(self):
        result = sgql.top_transfers(
            0, "bitcoin",
            from_date="2024-01-01", to_date="2024-01-31",
        )
        assert "topTransfers" in result
        assert "fromAddress" in result

    def test_top_transfers_nested_return_fields(self):
        result = sgql.top_transfers(
            0, "bitcoin",
            from_date="2024-01-01", to_date="2024-01-31",
        )
        # Verify nested braces are properly unescaped
        assert "fromAddress{address}" in result
        assert "toAddress{address}" in result
        assert "{{" not in result


class TestProjectBySlugQueries:
    def test_eth_top_transactions(self):
        result = sgql.eth_top_transactions(
            0, "santiment",
            from_date="2024-01-01", to_date="2024-01-31",
            limit=5, transaction_type="ALL",
        )
        assert "projectBySlug" in result
        assert "ethTopTransactions" in result
        assert "fromAddress{address isExchange}" in result
        assert "{{" not in result


class TestUniqueLogicQueries:
    def test_emerging_trends(self):
        result = sgql.emerging_trends(
            0, from_date="2024-01-01", to_date="2024-01-31",
            interval="1d", size=5,
        )
        assert "getTrendingWords" in result
        assert "topWords{score word}" in result
        assert "{{" not in result

    def test_projects_all(self):
        result = sgql.projects(0, "all")
        assert "allProjects" in result

    def test_projects_erc20(self):
        result = sgql.projects(0, "erc20")
        assert "allErc20Projects" in result

    def test_projects_unknown_raises(self):
        with pytest.raises(SanValidationError, match="Unknown project group"):
            sgql.projects(0, "unknown_group")

    def test_social_volume_projects(self):
        result = sgql.social_volume_projects(0)
        assert "socialVolumeProjects" in result

    def test_topic_search(self):
        # topic_search needs return_fields kwarg since it's not in QUERY_MAPPING
        result = sgql.topic_search(
            0, from_date="2024-01-01", to_date="2024-01-31",
            interval="1d", source="TELEGRAM", search_text="bitcoin",
            return_fields=["datetime", "chartData"],
        )
        assert "topicSearch" in result


class TestMetricQueries:
    def test_get_metric_timeseries_with_slug(self):
        result = sgql.get_metric_timeseries_data(
            0, "daily_active_addresses", slug="bitcoin",
            from_date="2024-01-01", to_date="2024-01-31", interval="1d",
        )
        assert "getMetric" in result
        assert "daily_active_addresses" in result
        assert "timeseriesDataJson" in result
        assert 'slug:"bitcoin"' in result

    def test_get_metric_timeseries_with_selector(self):
        result = sgql.get_metric_timeseries_data(
            0, "daily_active_addresses",
            selector={"slug": "bitcoin"},
            from_date="2024-01-01", to_date="2024-01-31", interval="1d",
        )
        assert "selector:" in result
        assert "bitcoin" in result

    def test_get_metric_timeseries_missing_slug_raises(self):
        with pytest.raises(SanValidationError, match="slug.*selector"):
            sgql.get_metric_timeseries_data(
                0, "daily_active_addresses",
                from_date="2024-01-01", to_date="2024-01-31", interval="1d",
            )

    def test_get_metric_per_slug(self):
        result = sgql.get_metric_timeseries_data_per_slug(
            0, "daily_active_addresses", slugs=["bitcoin", "ethereum"],
            from_date="2024-01-01", to_date="2024-01-31", interval="1d",
        )
        assert "timeseriesDataPerSlugJson" in result
        assert '"bitcoin"' in result
        assert '"ethereum"' in result

    def test_get_metric_with_transform(self):
        result = sgql.get_metric_timeseries_data(
            0, "daily_active_addresses", slug="bitcoin",
            from_date="2024-01-01", to_date="2024-01-31", interval="1d",
            transform={"type": "moving_average", "moving_average_base": 7},
        )
        assert "transform:" in result
        assert "moving_average" in result


class TestTransformArgHelper:
    def test_no_transform(self):
        assert sgql._transform_arg_helper({}) == ""

    def test_with_int_value(self):
        result = sgql._transform_arg_helper({"transform": {"moving_average_base": 7}})
        assert "moving_average_base: 7" in result

    def test_with_string_value(self):
        result = sgql._transform_arg_helper({"transform": {"type": "moving_average"}})
        assert 'type: "moving_average"' in result

    def test_invalid_transform_value_raises(self):
        with pytest.raises(SanValidationError):
            sgql._transform_arg_helper({"transform": {"bad": [1, 2, 3]}})


class TestApiCallsMade:
    def test_generates_query(self):
        result = sgql.get_api_calls_made()
        assert "currentUser" in result
        assert "apiCallsHistory" in result
        assert "apiCallsCount" in result
