import san.sanbase_graphql
from san.graphql import execute_gql, get_response_headers
from san.error import SanError

def is_rate_limit_exception(exception):
    return 'API Rate Limit Reached' in str(exception)


def rate_limit_time_left(exception):
    words = str(exception).split()
    return int(list(filter(lambda x: x.isnumeric(), words))[0]) # Message is: API Rate Limit Reached. Try again in X seconds (<human readable time>)  


def api_calls_remaining():
    gql_query_str = san.sanbase_graphql.get_api_calls_made()
    res = get_response_headers(gql_query_str)
    return __get_headers_remaining(res)


def api_calls_made():
    gql_query_str = san.sanbase_graphql.get_api_calls_made()
    res = __request_api_call_data(gql_query_str)
    api_calls = __parse_out_calls_data(res)

    return api_calls


def __request_api_call_data(query):
    try:
        res = execute_gql(query)['currentUser']['apiCallsHistory']
    except Exception as exc:
        if 'the results are empty' in str(exc):
            raise SanError('No API Key detected...')
        else:
            raise SanError(exc)

    return res


def __parse_out_calls_data(response):
    try:
        api_calls = list(map(
            lambda x: (x['datetime'], x['apiCallsCount']), response
        ))
    except:
        raise SanError('An error has occured, please contact our support...')

    return api_calls


def __get_headers_remaining(data):
    try:
        return {
            'month_remaining': data['x-ratelimit-remaining-month'],
            'hour_remaining': data['x-ratelimit-remaining-hour'],
            'minute_remaining': data['x-ratelimit-remaining-minute']
        }
    except KeyError as exc:
        raise SanError('There are no limits for this API Key.')
