import iso8601


def daily_active_addresses(idx, slug, **kwargs):

    kwargs['from_date'] = _format_date(kwargs['from_date'])
    kwargs['to_date'] = _format_date(kwargs['to_date'])

    query_str = """
    query_{idx}: dailyActiveAddresses(
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\"
    ){{
        activeAddresses,
        datetime
    }}
    """.format(idx=idx, slug=slug, **kwargs)

    print(query_str)

    return query_str


def prices(idx, currencies_from_to_string, **kwargs):
    curr_from, curr_to = currencies_from_to_string.split("_")

    kwargs['from_date'] = _format_date(kwargs['from_date'])
    kwargs['to_date'] = _format_date(kwargs['to_date'])

    query_str = """
    query_{idx}: historyPrice(
        ticker: \"{ticker}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\"
    ){{
        {result_curr},
        datetime
    }}
    """.format(idx=idx, ticker=curr_from.upper(), result_curr=_result_curr(curr_to), **kwargs)

    print(query_str)

    return query_str


def _format_date(date_str):
    return iso8601.parse_date(date_str).isoformat()


def _result_curr(curr_to):
    return "price" + curr_to.title()
