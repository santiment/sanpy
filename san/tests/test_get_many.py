from copy import deepcopy

import pandas as pd
import pytest

import san
from san.error import SanValidationError


def test_get_many_basic(mock_gql_post, test_response):
    api_call_result = {
        "query_0": {
            "timeseriesDataPerSlugJson": [
                {
                    "datetime": "2024-01-01T00:00:00Z",
                    "data": [
                        {"slug": "bitcoin", "value": 100.0},
                        {"slug": "ethereum", "value": 200.0},
                    ],
                },
                {
                    "datetime": "2024-01-02T00:00:00Z",
                    "data": [
                        {"slug": "bitcoin", "value": 110.0},
                        {"slug": "ethereum", "value": 210.0},
                    ],
                },
            ]
        }
    }
    mock_gql_post.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

    result = san.get_many(
        "daily_active_addresses",
        slugs=["bitcoin", "ethereum"],
        from_date="2024-01-01",
        to_date="2024-01-03",
        interval="1d",
    )

    assert isinstance(result, pd.DataFrame)
    assert "bitcoin" in result.columns
    assert "ethereum" in result.columns
    assert len(result) == 2
    assert result.index.name == "datetime"


def test_get_many_single_slug(mock_gql_post, test_response):
    api_call_result = {
        "query_0": {
            "timeseriesDataPerSlugJson": [
                {
                    "datetime": "2024-01-01T00:00:00Z",
                    "data": [{"slug": "bitcoin", "value": 100.0}],
                },
            ]
        }
    }
    mock_gql_post.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

    result = san.get_many(
        "daily_active_addresses",
        slugs=["bitcoin"],
        from_date="2024-01-01",
        to_date="2024-01-02",
        interval="1d",
    )

    assert isinstance(result, pd.DataFrame)
    assert "bitcoin" in result.columns
    assert len(result) == 1


def test_get_many_missing_slugs():
    with pytest.raises(SanValidationError):
        san.get_many("daily_active_addresses", from_date="2024-01-01", to_date="2024-01-02")


def test_get_many_with_selector(mock_gql_post, test_response):
    api_call_result = {
        "query_0": {
            "timeseriesDataPerSlugJson": [
                {
                    "datetime": "2024-01-01T00:00:00Z",
                    "data": [{"slug": "bitcoin", "value": 100.0}],
                },
            ]
        }
    }
    mock_gql_post.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

    result = san.get_many(
        "daily_active_addresses",
        selector={"slugs": ["bitcoin"]},
        from_date="2024-01-01",
        to_date="2024-01-02",
        interval="1d",
    )

    assert isinstance(result, pd.DataFrame)
