import iso8601
import datetime

from san.error import SanError
from san.query_constants import QUERY_MAPPING

_DEFAULT_INTERVAL = "1d"
_DEFAULT_SOCIAL_VOLUME_TYPE = "TELEGRAM_CHATS_OVERVIEW"
_DEFAULT_SOURCE = "TELEGRAM"
_DEFAULT_SEARCH_TEXT = ""


def all_projects(idx: int, **kwargs: dict) -> str:
    """
    Returns a GraphQL query string for allProjects
    :param idx: Index of the query
    :param kwargs: Keyword arguments
    :return: GraphQL query string
    """
    kwargs = transform_query_args("projects", **kwargs)
    query_str = (
        f"""
    query_{idx}: allProjects
    {{
    """
        + " ".join(kwargs["return_fields"])
        + "}"
    )

    return query_str


def erc20_projects(idx: int, **kwargs: dict) -> str:
    kwargs = transform_query_args("projects", **kwargs)
    query_str = (
        f"""
    query_{idx}: allErc20Projects
    {{
    """
        + " ".join(kwargs["return_fields"])
        + "}"
    )

    return query_str


def create_query_str(query: str, idx: int, slug: str, **kwargs: dict) -> str:
    """
    Returns a GraphQL query string for a given query
    :param query: Query name
    :param idx: Index of the query
    :param slug: Slug of the project
    :param kwargs: Keyword arguments
    :return: GraphQL query string
    """
    kwargs = transform_query_args(query, **kwargs)
    query = QUERY_MAPPING[query]["query"]
    from_date = kwargs["from_date"]
    to_date = kwargs["to_date"]
    interval = kwargs["interval"]

    query_str = (
        f"""
    query_{idx}: {query}(
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\"
    ){{
    """
        + " ".join(kwargs["return_fields"])
        + "}"
    )

    return query_str


def transform_selector(selector: dict) -> str:
    """
    Transforms a selector dictionary to a GraphQL selector string
    :param selector: Selector dictionary
    :return: GraphQL selector string
    """
    temp_selector = ""
    for key, value in selector.items():
        if (isinstance(value, str) and value.isdigit()) or isinstance(value, int):
            temp_selector += f"{key}: {value}\n"
        elif isinstance(value, str):
            temp_selector += f'{key}: "{value}"\n'
        elif isinstance(value, dict):
            temp_selector += f"{key}:{{{transform_selector(value)}}}\n"
        elif isinstance(value, bool):
            temp_selector += f"{key}: true\n" if value else f"{key}: false\n"
        elif isinstance(value, list):
            temp_value = map(lambda x: f'"{x}"', value)
            temp_selector += f'{key}: [{",".join(temp_value)}]\n'

    return temp_selector


def transform_query_args(query: str, **kwargs: dict) -> dict:
    """
    Transforms keyword arguments to a dictionary of GraphQL arguments
    :param query: Query name
    :param kwargs: Keyword arguments
    :return: Dictionary of GraphQL arguments
    """
    kwargs["from_date"] = kwargs.get("from_date", _default_from_date())
    kwargs["to_date"] = kwargs.get("to_date", _default_to_date())
    kwargs["interval"] = kwargs.get("interval", _DEFAULT_INTERVAL)
    kwargs["social_volume_type"] = kwargs.get(
        "social_volume_type", _DEFAULT_SOCIAL_VOLUME_TYPE
    )
    kwargs["source"] = kwargs.get("source", _DEFAULT_SOURCE)
    kwargs["search_text"] = kwargs.get("search_text", _DEFAULT_SEARCH_TEXT)
    kwargs["aggregation"] = kwargs.get("aggregation", "null")
    # transform python booleans to strings so it's properly interpolated in the query string
    kwargs["include_incomplete_data"] = str(
        kwargs.get("include_incomplete_data", "false")
    ).lower()

    if "selector" in kwargs:
        kwargs["selector"] = f'selector:{{{transform_selector(kwargs["selector"])}}}'

    kwargs["address"] = kwargs.get("address", "")
    kwargs["transaction_type"] = kwargs.get("transaction_type", "ALL")

    if kwargs["address"] != "":
        if kwargs["transaction_type"] != "":
            kwargs[
                "address_selector"
            ] = f'addressSelector:{{address:"{kwargs["address"]}", transactionType: {kwargs["transaction_type"]}}},'
        else:
            kwargs[
                "address_selector"
            ] = f'addressSelector:{{address:"{kwargs["address"]}"}},'
    else:
        kwargs["address_selector"] = ""

    kwargs["from_date"] = _format_from_date(kwargs["from_date"])
    kwargs["to_date"] = _format_to_date(kwargs["to_date"])

    if "return_fields" in kwargs:
        kwargs["return_fields"] = _format_all_return_fields(kwargs["return_fields"])
    else:
        kwargs["return_fields"] = _format_all_return_fields(
            QUERY_MAPPING[query]["return_fields"]
        )

    return kwargs


def _default_to_date() -> datetime.datetime:
    """
    Returns the current UTC datetime
    """
    return datetime.datetime.utcnow()


def _default_from_date() -> datetime.datetime:
    """
    Returns the current UTC datetime minus 365 days
    """
    return datetime.datetime.utcnow() - datetime.timedelta(days=365)


def _format_from_date(datetime_obj_or_str) -> str:
    """
    Formats a datetime object or string to a GraphQL compatible string
    :param datetime_obj_or_str: Datetime object or string
    :return: Formatted string
    """
    if isinstance(datetime_obj_or_str, str) and "utc_now" in datetime_obj_or_str:
        return datetime_obj_or_str

    if isinstance(datetime_obj_or_str, datetime.datetime):
        datetime_obj_or_str = datetime_obj_or_str.isoformat()

    return iso8601.parse_date(datetime_obj_or_str).isoformat()


def _format_to_date(datetime_obj_or_str) -> str:
    """
    Formats a datetime object or string to a GraphQL compatible string
    :param datetime_obj_or_str: Datetime object or string
    :return: Formatted string
    """
    if isinstance(datetime_obj_or_str, str) and "utc_now" in datetime_obj_or_str:
        return datetime_obj_or_str

    if isinstance(datetime_obj_or_str, datetime.datetime):
        return iso8601.parse_date(datetime_obj_or_str.isoformat()).isoformat()

    try:
        # Throw if the string is not date-formated, parse as date otherwise
        datetime.datetime.strptime(datetime_obj_or_str, "%Y-%m-%d")
        dt = iso8601.parse_date(datetime_obj_or_str) + datetime.timedelta(
            hours=23, minutes=59, seconds=59
        )
        return dt.isoformat()
    except Exception as e:
        raise SanError("Invalid date format: " + str(e) + " - " + datetime_obj_or_str)


def _format_all_return_fields(fields: list) -> list:
    """
    Formats all return fields to a GraphQL compatible string
    :param fields: List of return fields
    :return: Formatted list of return fields
    """
    while any(isinstance(x, tuple) for x in fields):
        fields = _format_return_fields(fields)
    return fields


def _format_return_fields(fields: list) -> list:
    """
    Formats a list of return fields to a GraphQL compatible string
    :param fields: List of return fields
    :return: Formatted list of return fields
    """
    return list(
        map(
            lambda el: el[0] + "{{" + " ".join(el[1]) + "}}"
            if isinstance(el, tuple)
            else el,
            fields,
        )
    )
