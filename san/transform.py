"""
In order to have metrics, which require different order, we need to have transform
 functions, which reorder or make different dictionaries in general.
"""
import operator
import pandas as pd
from san.pandas_utils import convert_to_datetime_idx_df
from functools import reduce
from collections import OrderedDict
from san.graphql import execute_gql
from san.v2_metrics_list import V2_METRIC_QUERIES

QUERY_PATH_MAP = {
    'eth_top_transactions': ['ethTopTransactions'],
    'eth_spent_over_time': ['ethSpentOverTime'],
    'token_top_transactions': ['tokenTopTransactions'],
    'get_metric': ['timeseriesData'],
    'topic_search': ['chartData']
}

def path_to_data(idx, query, data):
    """
    With this function we jump straight onto the key from the dataframe, that we want and start from there. We use our future starting points from the QUERY_PATH_MAP.
    """
    return reduce(
        operator.getitem, [
            'query_' + str(idx), ] + QUERY_PATH_MAP[query], data)


def transform_query_result(idx, query, data):
    """
    If there is a transforming function for this query, then the result is
    passed for it for another transformation
    """
    if query in QUERY_PATH_MAP:
        result = path_to_data(idx, query, data)
    elif query in V2_METRIC_QUERIES:
        result = path_to_data(idx, 'get_metric', data)
    else:
        result = data['query_' + str(idx)]

    if query + '_transform' in globals():
        result = globals()[query + '_transform'](result)

    return convert_to_datetime_idx_df(result)


def eth_top_transactions_transform(data):
    return list(map(lambda column: {
        'datetime': column['datetime'],
        'fromAddress': column['fromAddress']['address'],
        'fromAddressIsExchange': column['fromAddress']['isExchange'],
        'toAddress': column['toAddress']['address'],
        'toAddressIsExchange': column['toAddress']['isExchange'],
        'trxHash': column['trxHash'],
        'trxValue': column['trxValue']
    }, data))


def news_transform(data):
    result = list(map(lambda column: OrderedDict({
        'datetime': column['datetime'],
        'title': column['title'],
        'description': column['description'],
        'sourceName': column['sourceName'],
        'url': column['url']
    }), data))

    return result


def token_top_transactions_transform(data):
    return list(map(lambda column: {
        'datetime': column['datetime'],
        'fromAddress': column['fromAddress']['address'],
        'fromAddressIsExchange': column['fromAddress']['isExchange'],
        'toAddress': column['toAddress']['address'],
        'toAddressIsExchange': column['toAddress']['isExchange'],
        'trxHash': column['trxHash'],
        'trxValue': column['trxValue']
    }, data))


def emerging_trends_transform(data):
    result = []
    for column in data:
        for i in range(0, len(column['topWords'])):
            result.append({
                'datetime': column['datetime'],
                'score': column['topWords'][i]['score'],
                'word': column['topWords'][i]['word']
            })
    result.sort(key=lambda elem: elem['datetime'])

    return result


def top_social_gainers_losers_transform(data):
    result = []
    for column in data:
        for i in range(0, len(column['projects'])):
            result.append({
                'datetime': column['datetime'],
                'slug': column['projects'][i]['slug'],
                'change': column['projects'][i]['change'],
                'status': column['projects'][i]['status'],
            })
    
    result = list(map(lambda column: OrderedDict({
        'datetime': column['datetime'],
        'slug': column['slug'],
        'change': column['change'],
        'status': column['status']
    }), result))

    return result
