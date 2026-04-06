from san.client import get_default_client


def is_rate_limit_exception(exception):
    return "API Rate Limit Reached" in str(exception)


def rate_limit_time_left(exception):
    words = str(exception).split()
    return int(
        list(filter(lambda x: x.isnumeric(), words))[0]
    )  # Message is: API Rate Limit Reached. Try again in X seconds (<human readable time>)


def api_calls_remaining():
    return get_default_client().api_calls_remaining()


def api_calls_made():
    return get_default_client().api_calls_made()
