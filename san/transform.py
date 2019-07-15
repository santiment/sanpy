import operator
from functools import reduce

QUERY_PATH_MAP = {
    'eth_top_transactions': ['ethTopTransactions']
}

def path_to_data(idx, query, data):
    return reduce(operator.getitem, ['query_'+str(idx),]+QUERY_PATH_MAP[query], data)
    """
    With this function we jump straight onto the key from the dataframe, that we want and start from there
    """

def add_transform(function):
    def decorator(idx, query, data):
        if query+'_transform' in globals():
            result = path_to_data(idx, query, data)
            globals()[query+'_transform'](result)
        else:
            result = data['query_'+str(idx)]
        return function(idx, query, result)
    return decorator

def eth_top_transactions_transform(data):
    for column in data:
        column['fromAddressIsExchange'] = column['fromAddress']['isExchange']
        column['toAddressIsExchange'] = column['toAddress']['isExchange']
        column['fromAddress'] = column['fromAddress']['address']
        column['toAddress'] = column['toAddress']['address']
    return data
