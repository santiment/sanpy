import san
from san.error import SanError
from nose.tools import assert_raises
from unittest.mock import Mock, patch
from san.pandas_utils import convert_to_datetime_idx_df
import pandas.testing as pdt
from san.graphql import execute_gql
from san.tests.utils import TestResponse

@patch('san.graphql.requests.post')
def test_get(mock):
    expected = {
        'query_0':
            [{'datetime': '2018-06-01T00:00:00Z', 'activeAddresses': 2},
             {'datetime': '2018-06-02T00:00:00Z', 'activeAddresses': 4},
             {'datetime': '2018-06-03T00:00:00Z', 'activeAddresses': 6},
             {'datetime': '2018-06-04T00:00:00Z', 'activeAddresses': 6},
             {'datetime': '2018-06-05T00:00:00Z', 'activeAddresses': 14}]
    }
    mock.return_value = TestResponse(status_code=200, data=expected)

    res = san.get(
        "daily_active_addresses/santiment",
        from_date="2018-06-01",
        to_date="2018-06-05",
        interval="1d"
    )
    df = convert_to_datetime_idx_df(expected['query_0'])
    pdt.assert_frame_equal(res, df, check_dtype=False)


@patch('san.graphql.requests.post')
def test_prices(mock):
    expected = {
        'query_0':
            [
                {
                    'priceUsd': '1.234634930555555',
                    'priceBtc': '0.0001649780416666666',
                    'datetime': '2018-06-01T00:00:00Z'
                },
                {
                    'priceUsd': '1.2551352777777771',
                    'priceBtc': '0.00016521851041666669',
                    'datetime': '2018-06-02T00:00:00Z'
                },
                {
                    'priceUsd': '1.251881943462897',
                    'priceBtc': '0.000162902558303887',
                    'datetime': '2018-06-03T00:00:00Z'
                },
                {
                    'priceUsd': '1.2135782638888888',
                    'priceBtc': '0.0001600935277777778',
                    'datetime': '2018-06-04T00:00:00Z'
                }
            ]
    }
    mock.return_value = TestResponse(status_code=200, data=expected)

    res = san.get(
        "prices/santiment_usd",
        from_date="2018-06-01",
        to_date="2018-06-05",
        interval="1d"
    )

    df = convert_to_datetime_idx_df(expected['query_0'])
    pdt.assert_frame_equal(res, df, check_dtype=False)

@patch('san.graphql.requests.post')
def test_error_response(mock):
    mock.return_value = TestResponse(status_code=500, data={'errors': {'detail': 'Internal server error'}})
    with assert_raises(SanError):
        san.get(
            "prices/santiment_usd",
            from_date="2018-06-01",
            to_date="2018-06-05",
            interval="1d"
        )

def test_invalid_request():
    with assert_raises(ValueError):
        san.get("invalid_request")


def test_invalid_method():
    with assert_raises(SanError):
        san.get("invalid_method/slug")
