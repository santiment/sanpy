from san import Batch
# from unittest.mock import Mock, patch
import pandas as pd
import pandas.testing as pdt


# @patch('san.graphql.get_sanbase_gql_client')
def test_batch():
    expected = {
        'query_0':
            [{'datetime': '2018-06-01T00:00:00Z', 'activeAddresses': 2},
             {'datetime': '2018-06-02T00:00:00Z', 'activeAddresses': 4},
             {'datetime': '2018-06-03T00:00:00Z', 'activeAddresses': 6},
             {'datetime': '2018-06-04T00:00:00Z', 'activeAddresses': 6},
             {'datetime': '2018-06-05T00:00:00Z', 'activeAddresses': 14}],
        'query_1':
            [{'datetime': '2018-06-06T00:00:00Z', 'activeAddresses': 2},
             {'datetime': '2018-06-07T00:00:00Z', 'activeAddresses': 10},
             {'datetime': '2018-06-08T00:00:00Z', 'activeAddresses': 21},
             {'datetime': '2018-06-09T00:00:00Z', 'activeAddresses': 6},
             {'datetime': '2018-06-10T00:00:00Z', 'activeAddresses': 5}]
    }
    # mock.return_value = Mock()
    # mock.return_value.execute.return_value = expected

    batch = Batch()
    batch.get(
        "daily_active_addresses/santiment",
        from_date="2018-06-01",
        to_date="2018-06-05",
        interval="1d"
    )
    batch.get(
        "daily_active_addresses/santiment",
        from_date="2018-06-06",
        to_date="2018-06-10",
        interval="1d"
    )
    [res1, res2] = batch.execute()

    df1 = pd.DataFrame(expected['query_0'])
    df2 = pd.DataFrame(expected['query_1'])

    pdt.assert_frame_equal(res1, df1, check_dtype=False)
    pdt.assert_frame_equal(res2, df2, check_dtype=False)
