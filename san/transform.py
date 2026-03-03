"""
In order to have metrics, which require different order, we need to have transform
 functions, which reorder or make different dictionaries in general.
"""

import operator
from functools import reduce
from typing import Any

import pandas as pd

from san.error import SanValidationError
from san.pandas_utils import convert_to_datetime_idx_df
from san.sanbase_graphql_helper import QUERY_MAPPING

QUERY_PATH_MAP = {
    "eth_top_transactions": ["ethTopTransactions"],
    "eth_spent_over_time": ["ethSpentOverTime"],
    "token_top_transactions": ["tokenTopTransactions"],
    "get_metric": ["timeseriesDataJson"],
    "get_metric_many": ["timeseriesDataPerSlugJson"],
    "topic_search": ["chartData"],
}


def path_to_data(idx: int, query: str, data: dict[str, Any]) -> Any:
    """
    With this function we jump straight onto the key from the dataframe,
    that we want and start from there. We use our future starting points from the QUERY_PATH_MAP.
    """
    return reduce(
        operator.getitem,
        [
            "query_" + str(idx),
        ]
        + QUERY_PATH_MAP[query],
        data,
    )


def transform_timeseries_data_query_result(idx: int, query: str, data: dict[str, Any]) -> pd.DataFrame:
    """
    If there is a transforming function for this query, then the result is
    passed for it for another transformation
    """
    if query in QUERY_PATH_MAP:
        result = path_to_data(idx, query, data)
    elif query in QUERY_MAPPING:
        result = data["query_" + str(idx)]
    else:
        result = path_to_data(idx, "get_metric", data)

    if query + "_transform" in globals():
        result = globals()[query + "_transform"](result)

    return convert_to_datetime_idx_df(result)


def transform_timeseries_data_per_slug_query_result(idx: int, query: str, data: dict[str, Any]) -> pd.DataFrame:
    if query in QUERY_MAPPING:
        raise SanValidationError(f"The get_many call is available only for get_metric. Called with {query}")

    result = path_to_data(idx, "get_metric_many", data)
    rows = []

    for datetime_point in result:
        row = {"datetime": datetime_point["datetime"]}
        for slug_data in datetime_point["data"]:
            row[slug_data["slug"]] = slug_data["value"]

        rows.append(row)

    return convert_to_datetime_idx_df(rows)


def eth_top_transactions_transform(data: list[dict]) -> list[dict]:
    return [
        {
            "datetime": column["datetime"],
            "fromAddress": column["fromAddress"]["address"],
            "fromAddressIsExchange": column["fromAddress"]["isExchange"],
            "toAddress": column["toAddress"]["address"],
            "toAddressIsExchange": column["toAddress"]["isExchange"],
            "trxHash": column["trxHash"],
            "trxValue": column["trxValue"],
        }
        for column in data
    ]


def top_transfers_transform(data: list[dict]) -> list[dict]:
    return [
        {
            "datetime": column["datetime"],
            "fromAddress": column["fromAddress"]["address"],
            "toAddress": column["toAddress"]["address"],
            "trxHash": column["trxHash"],
            "trxValue": column["trxValue"],
        }
        for column in data
    ]


def news_transform(data: list[dict]) -> list[dict]:
    return [
        {
            "datetime": column["datetime"],
            "title": column["title"],
            "description": column["description"],
            "sourceName": column["sourceName"],
            "url": column["url"],
        }
        for column in data
    ]


def token_top_transactions_transform(data: list[dict]) -> list[dict]:
    return [
        {
            "datetime": column["datetime"],
            "fromAddress": column["fromAddress"]["address"],
            "fromAddressIsExchange": column["fromAddress"]["isExchange"],
            "toAddress": column["toAddress"]["address"],
            "toAddressIsExchange": column["toAddress"]["isExchange"],
            "trxHash": column["trxHash"],
            "trxValue": column["trxValue"],
        }
        for column in data
    ]


def emerging_trends_transform(data: list[dict]) -> list[dict]:
    result = []
    for column in data:
        for i in range(0, len(column["topWords"])):
            result.append(
                {"datetime": column["datetime"], "score": column["topWords"][i]["score"], "word": column["topWords"][i]["word"]}
            )
    result.sort(key=lambda elem: elem["datetime"])

    return result


def top_social_gainers_losers_transform(data: list[dict]) -> list[dict]:
    result = []
    for column in data:
        for project in column["projects"]:
            result.append(
                {
                    "datetime": column["datetime"],
                    "slug": project["slug"],
                    "change": project["change"],
                    "status": project["status"],
                }
            )

    return result
