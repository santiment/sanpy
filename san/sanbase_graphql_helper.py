import datetime

from san.sanitize import sanitize_gql_string, validate_address, validate_positive_int

_DEFAULT_INTERVAL = "1d"
_DEFAULT_SOCIAL_VOLUME_TYPE = "TELEGRAM_CHATS_OVERVIEW"
_DEFAULT_SOURCE = "TELEGRAM"
_DEFAULT_SEARCH_TEXT = ""

QUERY_MAPPING = {
    "prices": {"query": "historyPrice", "return_fields": ["datetime", "priceUsd", "priceBtc", "marketcap", "volume"]},
    "ohlc": {"query": "ohlc", "return_fields": ["datetime", "openPriceUsd", "closePriceUsd", "highPriceUsd", "lowPriceUsd"]},
    "miners_balance": {"query": "minersBalance", "return_fields": ["balance", "datetime"]},
    "historical_balance": {"query": "historicalBalance", "return_fields": ["datetime", "balance"]},
    "top_holders_percent_of_total_supply": {
        "query": "topHoldersPercentOfTotalSupply",
        "return_fields": ["datetime", "inExchanges", "outsideExchanges", "inTopHoldersTotal"],
    },
    "projects": {"query": "allProjects", "return_fields": ["name", "slug", "ticker", "totalSupply", "marketSegment"]},
    "get_metric": {"query": "getMetric", "return_fields": ["datetime", "value"]},
    "top_transfers": {
        "query": "topTransfers",
        "return_fields": ["datetime", ("fromAddress", ["address"]), ("toAddress", ["address"]), "trxValue", "trxHash"],
    },
    "eth_top_transactions": {
        "query": "ethTopTransactions",
        "return_fields": [
            "datetime",
            ("fromAddress", ["address", "isExchange"]),
            ("toAddress", ["address", "isExchange"]),
            "trxHash",
            "trxValue",
        ],
    },
    "token_top_transactions": {
        "query": "tokenTopTransactions",
        "return_fields": [
            "datetime",
            ("fromAddress", ["address", "isExchange"]),
            ("toAddress", ["address", "isExchange"]),
            "trxHash",
            "trxValue",
        ],
    },
    "eth_spent_over_time": {"query": "ethSpentOverTime", "return_fields": ["datetime", "ethSpent"]},
    "emerging_trends": {"query": "getTrendingWords", "return_fields": ["datetime", ("topWords", ["score", "word"])]},
    "social_volume_projects": {},
}


def _parse_iso_date(date_string: str) -> datetime.datetime:
    """Parse an ISO 8601 date string, always returning a timezone-aware datetime.

    Handles the ``Z`` timezone suffix for Python 3.10 compatibility, where
    ``datetime.fromisoformat()`` does not yet support it.  Naive results
    (e.g. from date-only strings like ``"2024-01-01"``) are assumed UTC.
    """
    if date_string.endswith("Z"):
        date_string = date_string[:-1] + "+00:00"
    dt = datetime.datetime.fromisoformat(date_string)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def all_projects(idx, **kwargs):
    kwargs = transform_query_args("projects", **kwargs)
    query_str = (
        """
    query_{idx}: allProjects
    {{
    """
        + " ".join(kwargs["return_fields"])
        + "}}"
    ).format(idx=idx)

    return query_str


def erc20_projects(idx, **kwargs):
    kwargs = transform_query_args("projects", **kwargs)
    query_str = (
        """
    query_{idx}: allErc20Projects
    {{
    """
        + " ".join(kwargs["return_fields"])
        + "}}"
    ).format(idx=idx)

    return query_str


def create_query_str(query, idx, slug, **kwargs):
    kwargs = transform_query_args(query, **kwargs)
    slug = sanitize_gql_string(slug)

    query_str = (
        """
    query_{idx}: {query}(
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\"
    ){{
    """
        + " ".join(kwargs["return_fields"])
        + "}}"
    ).format(query=QUERY_MAPPING[query]["query"], idx=idx, slug=slug, **kwargs)

    return query_str


def transform_selector(selector):
    temp_selector = ""
    for key, value in selector.items():
        sanitized_key = sanitize_gql_string(str(key))
        if (isinstance(value, str) and value.isdigit()) or isinstance(value, int):
            temp_selector += f"{sanitized_key}: {int(value)}\n"
        elif isinstance(value, str):
            temp_selector += f'{sanitized_key}: "{sanitize_gql_string(value)}"\n'
        elif isinstance(value, dict):
            temp_selector += f"{sanitized_key}:{{{transform_selector(value)}}}\n"
        elif isinstance(value, bool):
            temp_selector += f"{sanitized_key}: true\n" if value else f"{sanitized_key}: false\n"
        elif isinstance(value, list):
            temp_value = (f'"{sanitize_gql_string(str(x))}"' for x in value)
            temp_selector += f"{sanitized_key}: [{','.join(temp_value)}]\n"

    return temp_selector


def transform_query_args(query, **kwargs):
    kwargs["from_date"] = kwargs["from_date"] if "from_date" in kwargs else _default_from_date()
    kwargs["to_date"] = kwargs["to_date"] if "to_date" in kwargs else _default_to_date()
    kwargs["interval"] = kwargs["interval"] if "interval" in kwargs else _DEFAULT_INTERVAL
    kwargs["social_volume_type"] = kwargs["social_volume_type"] if "social_volume_type" in kwargs else _DEFAULT_SOCIAL_VOLUME_TYPE
    kwargs["source"] = kwargs["source"] if "source" in kwargs else _DEFAULT_SOURCE
    kwargs["search_text"] = kwargs["search_text"] if "search_text" in kwargs else _DEFAULT_SEARCH_TEXT
    kwargs["aggregation"] = kwargs["aggregation"] if "aggregation" in kwargs else "null"
    kwargs["include_incomplete_data"] = kwargs["include_incomplete_data"] if "include_incomplete_data" in kwargs else False
    # transform python booleans to strings so it's properly interpolated in the query string
    kwargs["include_incomplete_data"] = "true" if kwargs["include_incomplete_data"] else "false"

    # Sanitize interval
    if isinstance(kwargs["interval"], str):
        kwargs["interval"] = sanitize_gql_string(kwargs["interval"])

    # Sanitize search_text
    if isinstance(kwargs["search_text"], str):
        kwargs["search_text"] = sanitize_gql_string(kwargs["search_text"])

    if "selector" in kwargs:
        kwargs["selector"] = f"selector:{{{transform_selector(kwargs['selector'])}}}"

    kwargs["address"] = kwargs["address"] if "address" in kwargs else ""
    kwargs["transaction_type"] = kwargs["transaction_type"] if "transaction_type" in kwargs else "ALL"

    # Validate address if provided
    if kwargs["address"] != "":
        validate_address(kwargs["address"])

    # Validate limit if provided
    if "limit" in kwargs:
        kwargs["limit"] = validate_positive_int(kwargs["limit"], "limit")

    # Validate number_of_holders if provided
    if "number_of_holders" in kwargs:
        kwargs["number_of_holders"] = validate_positive_int(kwargs["number_of_holders"], "number_of_holders")

    # Validate size if provided
    if "size" in kwargs:
        kwargs["size"] = validate_positive_int(kwargs["size"], "size")

    if kwargs["address"] != "":
        address = sanitize_gql_string(kwargs["address"])
        if kwargs["transaction_type"] != "":
            kwargs["address_selector"] = (
                f'addressSelector:{{address:"{address}", transactionType: {kwargs["transaction_type"]}}},'
            )
        else:
            kwargs["address_selector"] = f'addressSelector:{{address:"{address}"}},'
    else:
        kwargs["address_selector"] = ""

    kwargs["from_date"] = _format_from_date(kwargs["from_date"])
    kwargs["to_date"] = _format_to_date(kwargs["to_date"])

    if "return_fields" in kwargs:
        kwargs["return_fields"] = _format_all_return_fields(kwargs["return_fields"])
    else:
        kwargs["return_fields"] = _format_all_return_fields(QUERY_MAPPING[query]["return_fields"])

    return kwargs


def _default_to_date():
    return datetime.datetime.now(datetime.timezone.utc)


def _default_from_date():
    return datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=365)


def _format_from_date(datetime_obj_or_str):
    if isinstance(datetime_obj_or_str, str) and "utc_now" in datetime_obj_or_str:
        return datetime_obj_or_str

    if isinstance(datetime_obj_or_str, datetime.datetime):
        datetime_obj_or_str = datetime_obj_or_str.isoformat()

    return _parse_iso_date(datetime_obj_or_str).isoformat()


def _format_to_date(datetime_obj_or_str):
    if isinstance(datetime_obj_or_str, str) and "utc_now" in datetime_obj_or_str:
        return datetime_obj_or_str

    if isinstance(datetime_obj_or_str, datetime.datetime):
        return _parse_iso_date(datetime_obj_or_str.isoformat()).isoformat()

    try:
        # Throw if the string is not date-formatted, parse as date otherwise
        datetime.datetime.strptime(datetime_obj_or_str, "%Y-%m-%d")
        dt = _parse_iso_date(datetime_obj_or_str) + datetime.timedelta(hours=23, minutes=59, seconds=59)
    except ValueError:
        dt = _parse_iso_date(datetime_obj_or_str)

    return dt.isoformat()


def _format_all_return_fields(fields):
    while any(isinstance(x, tuple) for x in fields):
        fields = _format_return_fields(fields)
    return fields


def _format_return_fields(fields):
    return list(map(lambda el: el[0] + "{{" + " ".join(el[1]) + "}}" if isinstance(el, tuple) else el, fields))
