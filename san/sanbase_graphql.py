import iso8601


def daily_active_addresses(idx, **kwargs):

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
    """.format(idx=idx, **kwargs)

    print(query_str)

    return query_str


def _format_date(date_str):
    return iso8601.parse_date(date_str).isoformat()
