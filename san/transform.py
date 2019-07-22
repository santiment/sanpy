"""
In order to have metrics, which require different order, we need to have transform
 functions, which reorder or make different dictionaries in general.
"""
import operator
import pandas as pd
from san.pandas_utils import convert_to_datetime_idx_df
from functools import reduce

QUERY_PATH_MAP = {
    'eth_top_transactions': ['ethTopTransactions'],
    'eth_spent_over_time': ['ethSpentOverTime'],
    'token_top_transactions':['tokenTopTransactions']
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
    result = list(map(lambda column: {
        'datetime': column['datetime'],
        'title': column['title'],
        'description': column['description'],
        'sourceName': column['sourceName'],
        'url': column['url']
    }, data))

    df = pd.DataFrame(result, columns = result[0].keys())

    return df


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
