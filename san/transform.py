import operator
from san.pandas_utils import convert_to_datetime_idx_df
from functools import reduce

QUERY_PATH_MAP = {
    'eth_top_transactions': ['ethTopTransactions']
}


def path_to_data(idx, query, data):
    """
    With this function we jump straight onto the key from the dataframe, that we want and start from there
    """
    return reduce(
        operator.getitem, [
            'query_' + str(idx), ] + QUERY_PATH_MAP[query], data)


def transform_query_result(idx, query, data):
    """
    If there is a transforming function for this query, then the result is
    passed for it for another transformation
    """
    if query + '_transform' in globals():
        result = path_to_data(idx, query, data)
        globals()[query + '_transform'](result)
    else:
        result = data['query_' + str(idx)]
    return convert_to_datetime_idx_df(result)


def eth_top_transactions_transform(data):
    for column in data:
        column['fromAddressIsExchange'] = column['fromAddress']['isExchange']
        column['toAddressIsExchange'] = column['toAddress']['isExchange']
        column['fromAddress'] = column['fromAddress']['address']
        column['toAddress'] = column['toAddress']['address']
    return data
