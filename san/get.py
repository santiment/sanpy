import san.sanbase_graphql
import operator
from san.graphql import execute_gql
from san.pandas_utils import convert_to_datetime_idx_df
from san.query import get_gql_query, parse_dataset
from functools import reduce

def shorten_path(root, items):
    return reduce(operator.getitem, items, root)
    """
    The first parameter (root) is the result from the execution of the query, the second is the list of keys,
    the first is the first key in the result of the query, the last - the key that we need the data from.

    The returned value is a shortened dictionary, from which the query can easily return the needed data.
    """
CUSTOM_QUERIES = {
    'ohlcv': 'get_ohlcv',
}

QUERY_PATH_MAP = {
    'eth_top_transactions': ['query_0', 'ethTopTransactions']
}

def get(dataset, **kwargs):
    query, slug = parse_dataset(dataset)
    if query in CUSTOM_QUERIES:
        return getattr(san.sanbase_graphql, query)(0, slug, **kwargs)

    gql_query = get_gql_query(0, dataset, **kwargs)
    gql_query = "{\n" + gql_query + "\n}"
    res = execute_gql(gql_query)

    if query in QUERY_PATH_MAP:
        res = shorten_path(res, QUERY_PATH_MAP[query])
        if query == 'eth_top_transactions':
            for column in res:
                column['fromAddressIsExchange'] = column['fromAddress']['isExchange']
                column['toAddressIsExchange'] = column['toAddress']['isExchange']
                column['fromAddress'] = column['fromAddress']['address']
                column['toAddress'] = column['toAddress']['address']
        return convert_to_datetime_idx_df(res)

    return convert_to_datetime_idx_df(res["query_0"])
