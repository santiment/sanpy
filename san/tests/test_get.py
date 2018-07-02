import san
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
        "santiment/daily_active_addresses",
        slug="santiment",
        from_date="2018-06-01",
        to_date="2018-06-05",
        interval="1d"
    )
    df = pd.DataFrame(expected['query_0'])
    pdt.assert_frame_equal(res, df, check_dtype=False)
