from san import Batch
from unittest.mock import patch
from san.pandas_utils import convert_to_datetime_idx_df
import pandas.testing as pdt


@patch("san.graphql.requests.post")
def test_batch(mock, test_response):
    expected = {
        "query_0": [
            {"balance": 212664.33000000002, "datetime": "2019-05-18T00:00:00Z"},
            {"balance": 212664.33000000002, "datetime": "2019-05-19T00:00:00Z"},
            {"balance": 212664.33000000002, "datetime": "2019-05-20T00:00:00Z"},
            {"balance": 212664.33000000002, "datetime": "2019-05-21T00:00:00Z"},
            {"balance": 212664.33000000002, "datetime": "2019-05-22T00:00:00Z"},
        ],
        "query_1": [
            {"balance": 212664.33000000002, "datetime": "2019-05-23T00:00:00Z"},
            {"balance": 212664.33000000002, "datetime": "2019-05-24T00:00:00Z"},
            {"balance": 212664.33000000002, "datetime": "2019-05-25T00:00:00Z"},
        ],
    }
    mock.return_value = test_response(status_code=200, data=expected)

    batch = Batch()
    batch.get(
        "historical_balance/santiment",
        address="0x1f3df0b8390bb8e9e322972c5e75583e87608ec2",
        from_date="2019-05-18",
        to_date="2019-05-23",
        interval="1d",
    )
    batch.get(
        "historical_balance/santiment",
        address="0x1f3df0b8390bb8e9e322972c5e75583e87608ec2",
        from_date="2019-05-23",
        to_date="2019-05-26",
        interval="1d",
    )
    [res1, res2] = batch.execute()

    df1 = convert_to_datetime_idx_df(expected["query_0"])
    df2 = convert_to_datetime_idx_df(expected["query_1"])

    pdt.assert_frame_equal(res1, df1, check_dtype=False)
    pdt.assert_frame_equal(res2, df2, check_dtype=False)
