from copy import deepcopy
from unittest.mock import patch

import pandas.testing as pdt
import pytest

import san
from san.error import SanAuthError, SanError
from san.pandas_utils import convert_to_datetime_idx_df


@patch("san.transport.requests.Session.post")
def test_san_client_get_uses_explicit_api_key(mock, test_response):
    api_call_result = {
        "query_0": {
            "timeseriesDataJson": [
                {"datetime": "2026-01-01T00:00:00Z", "value": 1.0},
                {"datetime": "2026-01-02T00:00:00Z", "value": 2.0},
            ]
        }
    }
    mock.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

    client = san.SanClient(api_key="client-key")
    result = client.get(
        "price_usd",
        slug="bitcoin",
        from_date="2026-01-01",
        to_date="2026-01-02",
        interval="1d",
    )

    expected = convert_to_datetime_idx_df(api_call_result["query_0"]["timeseriesDataJson"])
    pdt.assert_frame_equal(result, expected, check_dtype=False)
    assert mock.call_args.kwargs["headers"]["authorization"] == "Apikey client-key"


@patch("san.transport.requests.Session.post")
def test_san_client_preserves_transport_error_mapping(mock, test_response):
    mock.return_value = test_response(status_code=401, data={"errors": {"details": "Unauthorized"}})

    client = san.SanClient(api_key="bad-key")

    try:
        client.get(
            "price_usd",
            slug="bitcoin",
            from_date="2026-01-01",
            to_date="2026-01-02",
            interval="1d",
        )
    except SanAuthError:
        pass
    else:
        raise AssertionError("SanClient should preserve transport-backed auth error mapping")


@patch("san.transport.requests.Session.post")
def test_module_get_uses_compat_api_key(mock, test_response):
    api_call_result = {
        "query_0": {
            "timeseriesDataJson": [
                {"datetime": "2026-01-01T00:00:00Z", "value": 1.0},
                {"datetime": "2026-01-02T00:00:00Z", "value": 2.0},
            ]
        }
    }
    mock.return_value = test_response(status_code=200, data=deepcopy(api_call_result))

    previous_api_key = san.ApiConfig.api_key
    try:
        san.ApiConfig.api_key = "compat-key"
        result = san.get(
            "price_usd",
            slug="bitcoin",
            from_date="2026-01-01",
            to_date="2026-01-02",
            interval="1d",
        )
    finally:
        san.ApiConfig.api_key = previous_api_key

    expected = convert_to_datetime_idx_df(api_call_result["query_0"]["timeseriesDataJson"])
    pdt.assert_frame_equal(result, expected, check_dtype=False)
    assert mock.call_args.kwargs["headers"]["authorization"] == "Apikey compat-key"


def test_san_client_get_rejects_unsupported_parameters():
    client = san.SanClient()

    with pytest.raises(SanError, match="SanClient.get\\(\\) received unsupported parameter"):
        client.get("price_usd", slug="bitcoin", unsupported=True)


def test_module_get_keeps_strict_parameter_validation():
    with pytest.raises(SanError, match="san.get\\(\\) received unsupported parameter"):
        san.get("price_usd", slug="bitcoin", unsupported=True)
