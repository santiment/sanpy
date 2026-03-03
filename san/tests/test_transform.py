import pandas as pd
import pytest

from san.error import SanValidationError
from san.transform import (
    emerging_trends_transform,
    eth_top_transactions_transform,
    news_transform,
    path_to_data,
    top_social_gainers_losers_transform,
    top_transfers_transform,
    transform_timeseries_data_per_slug_query_result,
    transform_timeseries_data_query_result,
)


class TestPathToData:
    def test_navigates_nested_structure(self):
        data = {"query_0": {"ethTopTransactions": [{"value": 1}]}}
        result = path_to_data(0, "eth_top_transactions", data)
        assert result == [{"value": 1}]

    def test_get_metric_path(self):
        data = {"query_0": {"timeseriesDataJson": [{"datetime": "2024-01-01", "value": 42}]}}
        result = path_to_data(0, "get_metric", data)
        assert result == [{"datetime": "2024-01-01", "value": 42}]

    def test_with_nonzero_idx(self):
        data = {"query_3": {"ethSpentOverTime": [{"ethSpent": 10}]}}
        result = path_to_data(3, "eth_spent_over_time", data)
        assert result == [{"ethSpent": 10}]

    def test_missing_key_raises(self):
        data = {"query_0": {"wrong_key": []}}
        with pytest.raises(KeyError):
            path_to_data(0, "eth_top_transactions", data)


class TestTransformTimeseriesResult:
    def test_query_in_path_map(self):
        data = {
            "query_0": {
                "timeseriesDataJson": [
                    {"datetime": "2024-01-01T00:00:00Z", "value": 100},
                    {"datetime": "2024-01-02T00:00:00Z", "value": 200},
                ]
            }
        }
        result = transform_timeseries_data_query_result(0, "get_metric", data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert result.index.name == "datetime"

    def test_query_in_query_mapping(self):
        data = {
            "query_0": [
                {"datetime": "2024-01-01T00:00:00Z", "priceUsd": "100.0"},
                {"datetime": "2024-01-02T00:00:00Z", "priceUsd": "200.0"},
            ]
        }
        result = transform_timeseries_data_query_result(0, "prices", data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2

    def test_unknown_query_falls_back_to_get_metric(self):
        data = {
            "query_0": {
                "timeseriesDataJson": [
                    {"datetime": "2024-01-01T00:00:00Z", "value": 42},
                ]
            }
        }
        result = transform_timeseries_data_query_result(0, "some_custom_metric", data)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1


class TestTransformPerSlug:
    def test_raises_for_query_mapping_metric(self):
        with pytest.raises(SanValidationError, match="get_many call is available only for get_metric"):
            transform_timeseries_data_per_slug_query_result(0, "prices", {})

    def test_transforms_per_slug_data(self):
        data = {
            "query_0": {
                "timeseriesDataPerSlugJson": [
                    {
                        "datetime": "2024-01-01T00:00:00Z",
                        "data": [
                            {"slug": "bitcoin", "value": 100},
                            {"slug": "ethereum", "value": 200},
                        ],
                    },
                ]
            }
        }
        result = transform_timeseries_data_per_slug_query_result(0, "daily_active_addresses", data)
        assert isinstance(result, pd.DataFrame)
        assert "bitcoin" in result.columns
        assert "ethereum" in result.columns


class TestEthTopTransactionsTransform:
    def test_flattens_addresses(self):
        data = [
            {
                "datetime": "2024-01-01T00:00:00Z",
                "fromAddress": {"address": "0xaaa", "isExchange": True},
                "toAddress": {"address": "0xbbb", "isExchange": False},
                "trxHash": "0xhash",
                "trxValue": 42.0,
            }
        ]
        result = eth_top_transactions_transform(data)
        assert len(result) == 1
        assert result[0]["fromAddress"] == "0xaaa"
        assert result[0]["fromAddressIsExchange"] is True
        assert result[0]["toAddress"] == "0xbbb"
        assert result[0]["toAddressIsExchange"] is False


class TestTopTransfersTransform:
    def test_flattens_addresses(self):
        data = [
            {
                "datetime": "2024-01-01T00:00:00Z",
                "fromAddress": {"address": "0xaaa"},
                "toAddress": {"address": "0xbbb"},
                "trxHash": "0xhash",
                "trxValue": 10.0,
            }
        ]
        result = top_transfers_transform(data)
        assert result[0]["fromAddress"] == "0xaaa"
        assert result[0]["toAddress"] == "0xbbb"


class TestNewsTransform:
    def test_extracts_fields(self):
        data = [
            {
                "datetime": "2024-01-01T00:00:00Z",
                "title": "Test",
                "description": "Desc",
                "sourceName": "Source",
                "url": "https://example.com",
            }
        ]
        result = news_transform(data)
        assert result[0]["title"] == "Test"
        assert result[0]["url"] == "https://example.com"


class TestEmergingTrendsTransform:
    def test_flattens_top_words(self):
        data = [
            {
                "datetime": "2024-01-01T00:00:00Z",
                "topWords": [
                    {"word": "bitcoin", "score": 100},
                    {"word": "ethereum", "score": 80},
                ],
            },
            {
                "datetime": "2024-01-02T00:00:00Z",
                "topWords": [
                    {"word": "defi", "score": 60},
                ],
            },
        ]
        result = emerging_trends_transform(data)
        assert len(result) == 3
        # Should be sorted by datetime
        assert result[0]["datetime"] <= result[-1]["datetime"]
        words = [r["word"] for r in result]
        assert "bitcoin" in words
        assert "defi" in words


class TestTopSocialGainersLosersTransform:
    def test_flattens_projects(self):
        data = [
            {
                "datetime": "2024-01-01T00:00:00Z",
                "projects": [
                    {"slug": "bitcoin", "change": 10.0, "status": "gainer"},
                    {"slug": "ethereum", "change": -5.0, "status": "loser"},
                ],
            }
        ]
        result = top_social_gainers_losers_transform(data)
        assert len(result) == 2
        assert result[0]["slug"] == "bitcoin"
        assert result[1]["status"] == "loser"
