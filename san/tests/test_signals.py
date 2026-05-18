from copy import deepcopy
from unittest.mock import patch

import pandas.testing as pdt
import pytest

import san
from san.error import SanError
from san.pandas_utils import convert_to_datetime_idx_df


@patch("san.transport.requests.Session.post")
def test_available_signals(mock, test_response):
    api_call_result = {
        "query_0": [
            "anomaly_total_liquidations",
            "anomaly_project_in_trending_words",
        ]
    }
    mock.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

    res = san.available_signals()

    assert res == api_call_result["query_0"]

    query = mock.call_args.kwargs["json"]["query"]
    assert "getAvailableSignals" in query


@patch("san.transport.requests.Session.post")
def test_get_signal(mock, test_response):
    api_call_result = {
        "query_0": {
            "timeseriesData": [
                {
                    "datetime": "2026-01-01T00:00:00Z",
                    "value": 1.0,
                    "metadata": [{"type": "spike"}],
                }
            ]
        }
    }
    mock.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

    res = san.get_signal(
        "anomaly_total_liquidations",
        slug="ethereum",
        from_date="2026-01-01",
        to_date="2026-01-02",
        interval="1d",
    )

    expected_df = convert_to_datetime_idx_df(api_call_result["query_0"]["timeseriesData"])
    pdt.assert_frame_equal(res, expected_df, check_dtype=False)

    query = mock.call_args.kwargs["json"]["query"]
    assert 'getSignal(signal: "anomaly_total_liquidations")' in query
    assert "timeseriesData(" in query
    assert 'slug:"ethereum"' in query


def test_get_signal_requires_signal():
    with pytest.raises(SanError, match='"signal" must be provided'):
        san.get_signal(
            "",
            slug="ethereum",
            from_date="2026-01-01",
            to_date="2026-01-02",
        )


@patch("san.transport.requests.Session.post")
def test_get_raw_signals(mock, test_response):
    api_call_result = {
        "query_0": [
            {
                "datetime": "2026-01-01T00:00:00Z",
                "signal": "anomaly_total_liquidations",
                "slug": "ethereum",
                "value": 12.0,
                "metadata": {"type": "spike"},
                "isHidden": False,
            }
        ]
    }
    mock.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

    res = san.get_raw_signals(
        signals=["anomaly_total_liquidations"],
        selector={"slug": "ethereum"},
        from_date="2026-01-01",
        to_date="2026-01-02",
    )

    expected_df = convert_to_datetime_idx_df(api_call_result["query_0"])
    pdt.assert_frame_equal(res, expected_df, check_dtype=False)

    query = mock.call_args.kwargs["json"]["query"]
    assert "getRawSignals(" in query
    assert 'signals: ["anomaly_total_liquidations"]' in query
    assert 'selector:{slug: "ethereum"' in query


@patch("san.transport.requests.Session.post")
def test_get_raw_signals_without_slug(mock, test_response):
    api_call_result = {
        "query_0": [
            {
                "datetime": "2026-01-01T00:00:00Z",
                "signal": "anomaly_total_liquidations",
                "slug": "ethereum",
                "value": 12.0,
                "metadata": {"type": "spike"},
                "isHidden": False,
            }
        ]
    }
    mock.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

    res = san.get_raw_signals(
        signals=["anomaly_total_liquidations"],
        from_date="2026-01-01",
        to_date="2026-01-02",
    )

    expected_df = convert_to_datetime_idx_df(api_call_result["query_0"])
    pdt.assert_frame_equal(res, expected_df, check_dtype=False)

    query = mock.call_args.kwargs["json"]["query"]
    assert "getRawSignals(" in query
    assert "selector:" not in query
