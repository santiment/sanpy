import san
import pandas as pd
import pandas.testing as pdt
from san.error import SanError
from nose.tools import assert_raises
from unittest.mock import Mock, patch
from san.pandas_utils import convert_to_datetime_idx_df
from san.tests.utils import TestResponse
from copy import deepcopy
from san.batch import Batch


@patch('san.graphql.requests.post')
def test_get(mock):
    api_call_result = {'query_0': [{'balance': 212664.33000000002,
                                    'datetime': '2019-05-23T00:00:00Z'},
                                   {'balance': 212664.33000000002,
                                    'datetime': '2019-05-24T00:00:00Z'},
                                   {'balance': 212664.33000000002,
                                    'datetime': '2019-05-25T00:00:00Z'}]}
    mock.return_value = TestResponse(
        status_code=200, data=deepcopy(api_call_result))

    res = san.get(
        "historical_balance/santiment",
        address="0x1f3df0b8390bb8e9e322972c5e75583e87608ec2",
        from_date="2019-05-23",
        to_date="2019-05-26",
        interval="1d"
    )
    expected_df = convert_to_datetime_idx_df(api_call_result['query_0'])
    pdt.assert_frame_equal(res, expected_df, check_dtype=False)


@patch('san.graphql.requests.post')
def test_prices(mock):
    api_call_result = {
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
    mock.return_value = TestResponse(
        status_code=200, data=deepcopy(api_call_result))

    res = san.get(
        "prices/santiment_usd",
        from_date="2018-06-01",
        to_date="2018-06-05",
        interval="1d"
    )

    df = convert_to_datetime_idx_df(api_call_result['query_0'])
    pdt.assert_frame_equal(res, df, check_dtype=False)


@patch('san.graphql.requests.post')
def test_error_response(mock):
    mock.return_value = TestResponse(
        status_code=500, data={
            'errors': {
                'detail': 'Internal server error'}})
    with assert_raises(SanError):
        san.get(
            "prices/santiment_usd",
            from_date="2018-06-01",
            to_date="2018-06-05",
            interval="1d"
        )


@patch('san.graphql.requests.post')
def test_get_without_transform(mock):
    api_call_result = {'query_0': [{'balance': 212664.33000000002,
                                    'datetime': '2019-05-23T00:00:00Z'},
                                   {'balance': 212664.33000000002,
                                    'datetime': '2019-05-24T00:00:00Z'},
                                   {'balance': 212664.33000000002,
                                    'datetime': '2019-05-25T00:00:00Z'}]}

    # The value is passed by refference, that's why deepcopy is used for
    # expected
    mock.return_value = TestResponse(
        status_code=200, data=deepcopy(api_call_result))

    res = san.get(
        "historical_balance/santiment",
        address="0x1f3df0b8390bb8e9e322972c5e75583e87608ec2",
        from_date="2019-05-23",
        to_date="2019-05-26",
        interval="1d"
    )
    expected_df = convert_to_datetime_idx_df(api_call_result['query_0'])
    pdt.assert_frame_equal(res, expected_df, check_dtype=False)


@patch('san.graphql.requests.post')
def test_get_with_transform(mock):
    api_call_result = {
        'query_0': {
            'ethTopTransactions': [
                {
                    'datetime': '2019-04-19T14:14:52.000000Z',
                    'fromAddress': {
                        'address': '0x1f3df0b8390bb8e9e322972c5e75583e87608ec2',
                        'isExchange': False},
                    'toAddress': {
                        'address': '0xd69bc0585e05ea381ce3ae69626ce4e8a0629e16',
                        'isExchange': False},
                    'trxHash': '0x590512e1f1fbcfd48a13d1997842777269f7c1915b7baef3c11ba83ca62495be',
                    'trxValue': 19.48},
                {
                    'datetime': '2019-04-19T14:09:58.000000Z',
                    'fromAddress': {
                                'address': '0x1f3df0b8390bb8e9e322972c5e75583e87608ec2',
                                'isExchange': False},
                    'toAddress': {
                        'address': '0x723fb5c14eaff826b386052aace3b9b21999bf50',
                        'isExchange': False},
                    'trxHash': '0x78e0720b9e72d1d4d44efeff8393758d7b09c16f5156d63e021655e70be29db5',
                    'trxValue': 15.15}]}}

    # The value is passed by refference, that's why deepcopy is used for
    # expected
    mock.return_value = TestResponse(
        status_code=200, data=deepcopy(api_call_result))

    result = san.get(
        "eth_top_transactions/santiment",
        from_date="2019-04-18",
        to_date="2019-04-22",
        limit=5,
        transaction_type="ALL"
    )
    expected = [{'datetime': '2019-04-19T14:14:52.000000Z',
                 'fromAddress': '0x1f3df0b8390bb8e9e322972c5e75583e87608ec2',
                 'fromAddressIsExchange': False,
                 'toAddress': '0xd69bc0585e05ea381ce3ae69626ce4e8a0629e16',
                 'toAddressIsExchange': False,
                 'trxHash': '0x590512e1f1fbcfd48a13d1997842777269f7c1915b7baef3c11ba83ca62495be',
                 'trxValue': 19.48},
                {'datetime': '2019-04-19T14:09:58.000000Z',
                 'fromAddress': '0x1f3df0b8390bb8e9e322972c5e75583e87608ec2',
                 'fromAddressIsExchange': False,
                 'toAddress': '0x723fb5c14eaff826b386052aace3b9b21999bf50',
                 'toAddressIsExchange': False,
                 'trxHash': '0x78e0720b9e72d1d4d44efeff8393758d7b09c16f5156d63e021655e70be29db5',
                 'trxValue': 15.15}]

    expected_df = pd.DataFrame(expected, columns=expected[0].keys())
    if 'datetime' in expected_df.columns:
        expected_df['datetime'] = pd.to_datetime(
            expected_df['datetime'], utc=True)
        expected_df.set_index('datetime', inplace=True)
    pdt.assert_frame_equal(result, expected_df, check_dtype=False)


@patch('san.graphql.requests.post')
def test_batch_only_with_nontransform_queries(mock):
    api_call_result = {'query_0': [{'balance': 212664.33000000002,
                                    'datetime': '2019-05-18T00:00:00Z'},
                                   {'balance': 212664.33000000002,
                                    'datetime': '2019-05-19T00:00:00Z'},
                                   {'balance': 212664.33000000002,
                                    'datetime': '2019-05-20T00:00:00Z'},
                                   {'balance': 212664.33000000002,
                                    'datetime': '2019-05-21T00:00:00Z'},
                                   {'balance': 212664.33000000002,
                                    'datetime': '2019-05-22T00:00:00Z'}],
                       'query_1': [{'balance': 212664.33000000002,
                                    'datetime': '2019-05-23T00:00:00Z'},
                                   {'balance': 212664.33000000002,
                                    'datetime': '2019-05-24T00:00:00Z'},
                                   {'balance': 212664.33000000002,
                                    'datetime': '2019-05-25T00:00:00Z'}]}

    # The value is passed by refference, that's why deepcopy is used for
    # expected
    mock.return_value = TestResponse(
        status_code=200, data=deepcopy(api_call_result))

    expected = api_call_result

    batch = Batch()

    batch.get(
        "historical_balance/santiment",
        address="0x1f3df0b8390bb8e9e322972c5e75583e87608ec2",
        from_date="2019-05-18",
        to_date="2019-05-23",
        interval="1d"
    )

    batch.get(
        "historical_balance/santiment",
        address="0x1f3df0b8390bb8e9e322972c5e75583e87608ec2",
        from_date="2019-05-23",
        to_date="2019-05-26",
        interval="1d"
    )

    result = batch.execute()

    expected_result = []

    queries = ['historical_balance', 'historical_balance']
    for idx, query in enumerate(queries):
        df = pd.DataFrame(expected['query_' + str(idx)])
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
            df.set_index('datetime', inplace=True)
        expected_result.append(df)

    assert len(result) == len(expected_result)

    for i in range(0, len(result)):
        pdt.assert_frame_equal(
            result[i],
            expected_result[i],
            check_dtype=False)


@patch('san.graphql.requests.post')
def test_batch_only_with_transform_queries(mock):
    api_call_result = {
        'query_0': {
            'ethTopTransactions': [
                {
                    'datetime': '2019-04-19T14:14:52.000000Z',
                    'fromAddress': {
                        'address': '0x1f3df0b8390bb8e9e322972c5e75583e87608ec2',
                        'isExchange': False},
                    'toAddress': {
                        'address': '0xd69bc0585e05ea381ce3ae69626ce4e8a0629e16',
                        'isExchange': False},
                    'trxHash': '0x590512e1f1fbcfd48a13d1997842777269f7c1915b7baef3c11ba83ca62495be',
                    'trxValue': 19.48},
                {
                    'datetime': '2019-04-19T14:09:58.000000Z',
                    'fromAddress': {
                                'address': '0x1f3df0b8390bb8e9e322972c5e75583e87608ec2',
                                'isExchange': False},
                    'toAddress': {
                        'address': '0x723fb5c14eaff826b386052aace3b9b21999bf50',
                        'isExchange': False},
                    'trxHash': '0x78e0720b9e72d1d4d44efeff8393758d7b09c16f5156d63e021655e70be29db5',
                    'trxValue': 15.15}]},
        'query_1': {
            'ethTopTransactions': [
                {
                    'datetime': '2019-04-29T21:33:31.000000Z',
                    'fromAddress': {
                        'address': '0xe76fe52a251c8f3a5dcd657e47a6c8d16fdf4bfa',
                        'isExchange': False},
                    'toAddress': {
                        'address': '0x45d6275d9496bc61b5b072a75089be4c5ab54068',
                        'isExchange': False},
                    'trxHash': '0x776cd57382456adb2f9c22bc2e06b4ddc9937b073e7f2206737933b46806f658',
                    'trxValue': 100.0},
                {
                    'datetime': '2019-04-29T21:21:18.000000Z',
                    'fromAddress': {
                        'address': '0xe76fe52a251c8f3a5dcd657e47a6c8d16fdf4bfa',
                        'isExchange': False},
                    'toAddress': {
                        'address': '0x468bdccdc334f646f1acfb4f69e3e855d23440e2',
                        'isExchange': False},
                    'trxHash': '0x848414fb5c382f2a9fb1856425437b60a5471ae383b884100794f8adf12227a6',
                    'trxValue': 40.95}]}}

    # The value is passed by refference, that's why deepcopy is used for
    # expected
    mock.return_value = TestResponse(
        status_code=200, data=deepcopy(api_call_result))

    batch = Batch()

    batch.get(
        "eth_top_transactions/santiment",
        from_date="2019-04-18",
        to_date="2019-04-22",
        limit=5,
        transaction_type="ALL"
    )

    batch.get(
        "eth_top_transactions/santiment",
        from_date="2019-04-23",
        to_date="2019-04-29",
        limit=5,
        transaction_type="ALL"
    )

    result = batch.execute()

    expected = [[{'datetime': '2019-04-19T14:14:52.000000Z',
                  'fromAddress': '0x1f3df0b8390bb8e9e322972c5e75583e87608ec2',
                  'fromAddressIsExchange': False,
                  'toAddress': '0xd69bc0585e05ea381ce3ae69626ce4e8a0629e16',
                  'toAddressIsExchange': False,
                  'trxHash': '0x590512e1f1fbcfd48a13d1997842777269f7c1915b7baef3c11ba83ca62495be',
                  'trxValue': 19.48},
                 {'datetime': '2019-04-19T14:09:58.000000Z',
                  'fromAddress': '0x1f3df0b8390bb8e9e322972c5e75583e87608ec2',
                  'fromAddressIsExchange': False,
                  'toAddress': '0x723fb5c14eaff826b386052aace3b9b21999bf50',
                  'toAddressIsExchange': False,
                  'trxHash': '0x78e0720b9e72d1d4d44efeff8393758d7b09c16f5156d63e021655e70be29db5',
                  'trxValue': 15.15}],
                [{'datetime': '2019-04-29T21:33:31.000000Z',
                  'fromAddress': '0xe76fe52a251c8f3a5dcd657e47a6c8d16fdf4bfa',
                  'fromAddressIsExchange': False,
                  'toAddress': '0x45d6275d9496bc61b5b072a75089be4c5ab54068',
                  'toAddressIsExchange': False,
                  'trxHash': '0x776cd57382456adb2f9c22bc2e06b4ddc9937b073e7f2206737933b46806f658',
                  'trxValue': 100.0},
                 {'datetime': '2019-04-29T21:21:18.000000Z',
                    'fromAddress': '0xe76fe52a251c8f3a5dcd657e47a6c8d16fdf4bfa',
                    'fromAddressIsExchange': False,
                    'toAddress': '0x468bdccdc334f646f1acfb4f69e3e855d23440e2',
                    'toAddressIsExchange': False,
                    'trxHash': '0x848414fb5c382f2a9fb1856425437b60a5471ae383b884100794f8adf12227a6',
                    'trxValue': 40.95}]]

    expected_result = []

    queries = ['eth_top_transactions', 'eth_top_transactions']
    for idx, query in enumerate(queries):
        df = pd.DataFrame(expected[idx], columns=expected[idx][0].keys())

        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
            df.set_index('datetime', inplace=True)
        expected_result.append(df)

    assert len(result) == len(expected_result)

    for i in range(0, len(result)):
        pdt.assert_frame_equal(
            result[i],
            expected_result[i],
            check_dtype=False)


@patch('san.graphql.requests.post')
def test_batch_with_mixed_queries(mock):
    api_call_result = {'query_0': [{'balance': 212664.33000000002,
                                    'datetime': '2019-05-18T00:00:00Z'},
                                   {'balance': 212664.33000000002,
                                    'datetime': '2019-05-19T00:00:00Z'},
                                   {'balance': 212664.33000000002,
                                    'datetime': '2019-05-20T00:00:00Z'},
                                   {'balance': 212664.33000000002,
                                    'datetime': '2019-05-21T00:00:00Z'},
                                   {'balance': 212664.33000000002,
                                    'datetime': '2019-05-22T00:00:00Z'}],
                       'query_1': {'ethTopTransactions': [{'datetime': '2019-04-29T21:33:31.000000Z',
                                                           'fromAddress': {'address': '0xe76fe52a251c8f3a5dcd657e47a6c8d16fdf4bfa',
                                                                           'isExchange': False},
                                                           'toAddress': {'address': '0x45d6275d9496bc61b5b072a75089be4c5ab54068',
                                                                         'isExchange': False},
                                                           'trxHash': '0x776cd57382456adb2f9c22bc2e06b4ddc9937b073e7f2206737933b46806f658',
                                                           'trxValue': 100.0},
                                                          {'datetime': '2019-04-29T21:21:18.000000Z',
                                                           'fromAddress': {'address': '0xe76fe52a251c8f3a5dcd657e47a6c8d16fdf4bfa',
                                                                           'isExchange': False},
                                                           'toAddress': {'address': '0x468bdccdc334f646f1acfb4f69e3e855d23440e2',
                                                                         'isExchange': False},
                                                           'trxHash': '0x848414fb5c382f2a9fb1856425437b60a5471ae383b884100794f8adf12227a6',
                                                           'trxValue': 40.95}]}}

    # The value is passed by refference, that's why deepcopy is used for
    # expected
    mock.return_value = TestResponse(
        status_code=200, data=deepcopy(api_call_result))

    expected = [[{'balance': 212664.33000000002,
                  'datetime': '2019-05-18T00:00:00Z'},
                 {'balance': 212664.33000000002,
                  'datetime': '2019-05-19T00:00:00Z'},
                 {'balance': 212664.33000000002,
                  'datetime': '2019-05-20T00:00:00Z'},
                 {'balance': 212664.33000000002,
                  'datetime': '2019-05-21T00:00:00Z'},
                 {'balance': 212664.33000000002,
                  'datetime': '2019-05-22T00:00:00Z'}],
                [{'datetime': '2019-04-29T21:33:31.000000Z',
                  'fromAddress': '0xe76fe52a251c8f3a5dcd657e47a6c8d16fdf4bfa',
                  'fromAddressIsExchange': False,
                  'toAddress': '0x45d6275d9496bc61b5b072a75089be4c5ab54068',
                  'toAddressIsExchange': False,
                  'trxHash': '0x776cd57382456adb2f9c22bc2e06b4ddc9937b073e7f2206737933b46806f658',
                  'trxValue': 100.0},
                 {'datetime': '2019-04-29T21:21:18.000000Z',
                    'fromAddress': '0xe76fe52a251c8f3a5dcd657e47a6c8d16fdf4bfa',
                    'fromAddressIsExchange': False,
                    'toAddress': '0x468bdccdc334f646f1acfb4f69e3e855d23440e2',
                    'toAddressIsExchange': False,
                    'trxHash': '0x848414fb5c382f2a9fb1856425437b60a5471ae383b884100794f8adf12227a6',
                    'trxValue': 40.95}]]

    batch = Batch()

    batch.get(
        "historical_balance/santiment",
        address="0x1f3df0b8390bb8e9e322972c5e75583e87608ec2",
        from_date="2019-05-18",
        to_date="2019-05-23",
        interval="1d"
    )

    batch.get(
        "eth_top_transactions/santiment",
        from_date="2019-04-23",
        to_date="2019-04-29",
        limit=5,
        transaction_type="ALL"
    )

    result = batch.execute()

    expected_result = []

    queries = ['historical_balance', 'eth_top_transactions']
    for idx, query in enumerate(queries):
        df = pd.DataFrame(expected[idx], columns=expected[idx][0].keys())
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
            df.set_index('datetime', inplace=True)

        expected_result.append(df)

    assert len(result) == len(expected_result)

    for i in range(0, len(result)):
        pdt.assert_frame_equal(
            result[i],
            expected_result[i],
            check_dtype=False)


def test_invalid_request():
    with assert_raises(ValueError):
        san.get("invalid_request")


def test_invalid_method():
    with assert_raises(SanError):
        san.get("invalid_method/slug")
