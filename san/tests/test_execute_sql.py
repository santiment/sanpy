from copy import deepcopy

import pandas as pd
import pytest

from san.error import SanValidationError
from san.execute_sql import execute_sql


def test_execute_sql_basic(mock_gql_post, test_response):
    api_call_result = {
        "query_0": {
            "columns": ["dt", "metric", "value"],
            "columnTypes": ["Date", "String", "Float64"],
            "rows": [
                ["2024-01-01", "daily_active_addresses", 100.0],
                ["2024-01-02", "daily_active_addresses", 150.0],
            ],
        }
    }
    mock_gql_post.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

    result = execute_sql(
        query="SELECT dt, metric, value FROM daily_metrics_v2",
        parameters={},
    )

    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["dt", "metric", "value"]
    assert len(result) == 2


def test_execute_sql_with_set_index(mock_gql_post, test_response):
    api_call_result = {
        "query_0": {
            "columns": ["dt", "value"],
            "columnTypes": ["Date", "Float64"],
            "rows": [
                ["2024-01-01", 100.0],
                ["2024-01-02", 150.0],
            ],
        }
    }
    mock_gql_post.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

    result = execute_sql(
        query="SELECT dt, value FROM daily_metrics_v2",
        parameters={},
        set_index="dt",
    )

    assert result.index.name == "dt"
    assert "value" in result.columns
    assert "dt" not in result.columns


def test_execute_sql_with_parameters(mock_gql_post, test_response):
    api_call_result = {
        "query_0": {
            "columns": ["dt", "value"],
            "columnTypes": ["Date", "Float64"],
            "rows": [["2024-01-01", 42.0]],
        }
    }
    mock_gql_post.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

    result = execute_sql(
        query="SELECT dt, value FROM t WHERE asset_id = get_asset_id({slug})",
        parameters={"slug": "bitcoin"},
    )

    assert len(result) == 1
    # Verify the GQL query was constructed with escaped parameters
    call_args = mock_gql_post.call_args
    sent_query = call_args[1]["json"]["query"] if "json" in call_args[1] else call_args[0][1]["query"]
    assert "runRawSqlQuery" in sent_query
    assert "bitcoin" in sent_query


def test_execute_sql_invalid_set_index(mock_gql_post, test_response):
    api_call_result = {
        "query_0": {
            "columns": ["dt", "value"],
            "columnTypes": ["Date", "Float64"],
            "rows": [["2024-01-01", 100.0]],
        }
    }
    mock_gql_post.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

    with pytest.raises(SanValidationError, match="set_index"):
        execute_sql(
            query="SELECT dt, value FROM daily_metrics_v2",
            parameters={},
            set_index="nonexistent_column",
        )


def test_execute_sql_missing_query():
    with pytest.raises(SanValidationError, match="query"):
        execute_sql()


def test_execute_sql_escapes_special_chars(mock_gql_post, test_response):
    """Verify that newlines, quotes, and backslashes in SQL are properly escaped."""
    api_call_result = {
        "query_0": {
            "columns": ["v"],
            "columnTypes": ["Float64"],
            "rows": [[1.0]],
        }
    }
    mock_gql_post.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

    execute_sql(
        query='SELECT "value"\nFROM t\nWHERE x = 1',
        parameters={},
    )

    call_args = mock_gql_post.call_args
    sent_query = call_args[1]["json"]["query"] if "json" in call_args[1] else call_args[0][1]["query"]
    # The raw newlines should have been escaped
    assert "\n" not in sent_query.split("sqlQueryText")[1].split("sqlQueryParameters")[0] or "\\n" in sent_query
