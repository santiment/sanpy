import operator
from functools import reduce
from san.pandas_utils import convert_to_datetime_idx_df

QUERY_PATH_MAP = {
    'eth_top_transactions': ['ethTopTransactions']
}

def underscore_to_camelcase(query):
    new_query = ''
    query = query.split('_')
    first_passed = False
    for word in query:
        if first_passed:
            new_query += word.capitalize()
        else:
            new_query += word
            first_passed = True
    new_query = ''.join(new_query)
    return new_query

def path_to_data(idx, query, data):
    return reduce(operator.getitem, ['query_'+str(idx),]+QUERY_PATH_MAP[query], data)
    """
    With this function we jump straight onto the key from the dataframe, that we want and start from there
    """

def add_transform(function):
    def decorator(idx, query, data):
        if query in QUERY_PATH_MAP:
            print(underscore_to_camelcase(query))
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
