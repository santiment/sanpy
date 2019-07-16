import san
from san.batch import Batch
from copy import deepcopy
from san.error import SanError
from nose.tools import assert_raises
from unittest.mock import Mock, patch
from san.pandas_utils import convert_to_datetime_idx_df
import pandas.testing as pdt
from san.graphql import execute_gql
from san.tests.utils import TestResponse
from san.query import transform_query


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

    # The value is passed by refference, that's why deepcopy is used for
    # expected
    mock.return_value = TestResponse(status_code=200, data=deepcopy(expected))

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
    # The value is passed by refference, that's why deepcopy is used for
    # expected
    mock.return_value = TestResponse(status_code=200, data=deepcopy(expected))

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
    expected = {
        'query_0':
            [{'datetime': '2018-06-01T00:00:00Z', 'activeAddresses': 2},
             {'datetime': '2018-06-02T00:00:00Z', 'activeAddresses': 4},
             {'datetime': '2018-06-03T00:00:00Z', 'activeAddresses': 6},
             {'datetime': '2018-06-04T00:00:00Z', 'activeAddresses': 6},
             {'datetime': '2018-06-05T00:00:00Z', 'activeAddresses': 14}]
    }
    # The value is passed by refference, that's why deepcopy is used for
    # expected
    mock.return_value = TestResponse(status_code=200, data=deepcopy(expected))

    res = san.get(
        "daily_active_addresses/santiment",
        from_date="2018-06-01",
        to_date="2018-06-05",
        interval="1d"
    )
    df = transform_query(0, 'daily_active_addresses', expected)
    pdt.assert_frame_equal(res, df, check_dtype=False)


@patch('san.graphql.requests.post')
def test_get_with_transform(mock):
    expected = {
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
    mock.return_value = TestResponse(status_code=200, data=deepcopy(expected))
    res = san.get(
        "eth_top_transactions/santiment",
        from_date="2019-04-18",
        to_date="2019-04-22",
        limit=5,
        transaction_type="ALL"
    )

    df = transform_query(0, 'eth_top_transactions', expected)
    pdt.assert_frame_equal(res, df, check_dtype=False)


@patch('san.graphql.requests.post')
def test_batch_only_with_nontransform_queries(mock):
    expected = {
        'query_0': {
            'datetime': '2019-04-19T14:14:52.000000Z',
            'fromAddress': {
                'address': '0x1f3df0b8390bb8e9e322972c5e75583e87608ec2',
                'isExchange': False},
            'toAddress': {
                'address': '0xd69bc0585e05ea381ce3ae69626ce4e8a0629e16',
                'isExchange': False},
            'trxHash': '0x590512e1f1fbcfd48a13d1997842777269f7c1915b7baef3c11ba83ca62495be',
            'trxValue': 19.48},
        'query_1': {
            'datetime': '2019-04-19T14:09:58.000000Z',
            'fromAddress': {
                        'address': '0x1f3df0b8390bb8e9e322972c5e75583e87608ec2',
                        'isExchange': False},
            'toAddress': {
                'address': '0x723fb5c14eaff826b386052aace3b9b21999bf50',
                'isExchange': False},
            'trxHash': '0x78e0720b9e72d1d4d44efeff8393758d7b09c16f5156d63e021655e70be29db5',
            'trxValue': 15.15}}
    # The value is passed by refference, that's why deepcopy is used for
    # expected
    mock.return_value = TestResponse(status_code=200, data=deepcopy(expected))

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

    result = batch.execute()

    expected_result = []

    queries = ['daily_active_addresses', 'daily_active_addresses']
    for idx, query in enumerate(queries):
        df = transform_query(idx, query, expected)
        expected_result.append(df)

    assert len(result) == len(expected_result)

    for i in range(0, len(result)):
        pdt.assert_frame_equal(
            result[i],
            expected_result[i],
            check_dtype=False)


@patch('san.graphql.requests.post')
def test_batch_only_with_transform_queries(mock):
    expected = {
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
    mock.return_value = TestResponse(status_code=200, data=deepcopy(expected))

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
        to_date="2019-04-24",
        limit=5,
        transaction_type="ALL"
    )

    result = batch.execute()

    expected_result = []

    queries = ['eth_top_transactions', 'eth_top_transactions']

    for idx, query in enumerate(queries):
        df = transform_query(idx, query, expected)
        expected_result.append(df)

    assert len(result) == len(expected_result)

    for i in range(0, len(result)):
        pdt.assert_frame_equal(
            result[i],
            expected_result[i],
            check_dtype=False)


@patch('san.graphql.requests.post')
def test_batch_with_mixed_queries(mock):
    expected = {'query_0': [{'activeAddresses': 2,
                             'datetime': '2018-06-01T00:00:00Z'},
                            {'activeAddresses': 4,
                             'datetime': '2018-06-02T00:00:00Z'},
                            {'activeAddresses': 6,
                             'datetime': '2018-06-03T00:00:00Z'},
                            {'activeAddresses': 6,
                             'datetime': '2018-06-04T00:00:00Z'},
                            {'activeAddresses': 14,
                             'datetime': '2018-06-05T00:00:00Z'}],
                'query_1': {'ethTopTransactions': [{'datetime': '2019-04-19T14:14:52.000000Z',
                                                    'fromAddress': {'address': '0x1f3df0b8390bb8e9e322972c5e75583e87608ec2',
                                                                    'isExchange': False},
                                                    'toAddress': {'address': '0xd69bc0585e05ea381ce3ae69626ce4e8a0629e16',
                                                                  'isExchange': False},
                                                    'trxHash': '0x590512e1f1fbcfd48a13d1997842777269f7c1915b7baef3c11ba83ca62495be',
                                                    'trxValue': 19.48},
                                                   {'datetime': '2019-04-19T14:09:58.000000Z',
                                                    'fromAddress': {'address': '0x1f3df0b8390bb8e9e322972c5e75583e87608ec2',
                                                                    'isExchange': False},
                                                    'toAddress': {'address': '0x723fb5c14eaff826b386052aace3b9b21999bf50',
                                                                  'isExchange': False},
                                                    'trxHash': '0x78e0720b9e72d1d4d44efeff8393758d7b09c16f5156d63e021655e70be29db5',
                                                    'trxValue': 15.15}]}}

    # The value is passed by refference, that's why deepcopy is used for
    # expected
    mock.return_value = TestResponse(status_code=200, data=deepcopy(expected))

    batch = Batch()

    batch.get(
        "daily_active_addresses/santiment",
        from_date="2018-06-01",
        to_date="2018-06-05",
        interval="1d"
    )

    batch.get(
        "eth_top_transactions/santiment",
        from_date="2019-04-18",
        to_date="2019-04-22",
        limit=5,
        transaction_type="ALL"
    )

    result = batch.execute()

    expected_result = []

    queries = ['daily_active_addresses', 'eth_top_transactions']

    for idx, query in enumerate(queries):
        df = transform_query(idx, query, expected)
        print(df)
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
