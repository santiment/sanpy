import san
from san.error import SanError
from nose.tools import assert_raises
from unittest.mock import Mock, patch
import pandas as pd
import pandas.testing as pdt


@patch('san.graphql.get_sanbase_gql_client')
def test_get(mock):
    expected = {
        'query_0':
            [{'datetime': '2018-06-01T00:00:00Z', 'activeAddresses': 2},
             {'datetime': '2018-06-02T00:00:00Z', 'activeAddresses': 4},
             {'datetime': '2018-06-03T00:00:00Z', 'activeAddresses': 6},
             {'datetime': '2018-06-04T00:00:00Z', 'activeAddresses': 6},
             {'datetime': '2018-06-05T00:00:00Z', 'activeAddresses': 14}]
    }
    mock.return_value = Mock()
    mock.return_value.execute.return_value = expected
    res = san.get(
        "daily_active_addresses/santiment",
        from_date="2018-06-01",
        to_date="2018-06-05",
        interval="1d"
    )
    df = pd.DataFrame(expected['query_0'])
    pdt.assert_frame_equal(res, df, check_dtype=False)


@patch('san.graphql.get_sanbase_gql_client')
def test_prices(mock):
    expected = {
        'query_0':
            [{'priceUsd': '1.234634930555555', 'datetime': '2018-06-01T00:00:00Z'},
             {'priceUsd': '1.2551352777777771', 'datetime': '2018-06-02T00:00:00Z'},
             {'priceUsd': '1.251881943462897', 'datetime': '2018-06-03T00:00:00Z'},
             {'priceUsd': '1.2135782638888888', 'datetime': '2018-06-04T00:00:00Z'}]
    }
    mock.return_value = Mock()
    mock.return_value.execute.return_value = expected
    res = san.get(
        "prices/san_usd",
        from_date="2018-06-01",
        to_date="2018-06-05",
        interval="1d"
    )

    df = pd.DataFrame(expected['query_0'])
    pdt.assert_frame_equal(res, df, check_dtype=False)


def test_invalid_request():
    with assert_raises(ValueError):
        san.get("invalid_request")


def test_invalid_method():
    with assert_raises(SanError):
        san.get("invalid_method/slug")
