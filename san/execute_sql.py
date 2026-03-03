import json
from typing import Any

import pandas as pd

from san.error import SanValidationError
from san.graphql import execute_gql


def execute_sql(**kwargs: Any) -> pd.DataFrame:
    """
    Execute an arbitrary SQL against Santiment's Clickhouse Database

    Example:
        san.execute_sql(query=\"""
        SELECT
            get_metric_name(metric_id) AS metric,
            get_asset_name(asset_id) AS asset,
            dt,
            value
        FROM daily_metrics_v2
        WHERE
            asset_id = get_asset_id({{slug}}) AND
            metric_id = get_metric_id({{metric}}) AND
            dt >= now() - INTERVAL {{last_n_days}} DAY
        ORDER BY dt ASC
        \""",
        parameters={'slug': 'bitcoin', 'metric': 'daily_active_addresses', 'last_n_days': 7},
        set_index="dt")
    """
    if "query" in kwargs:
        query = kwargs.pop("query")
    else:
        raise SanValidationError("The 'query' argument is required when calling 'execute_sql'")

    parameters = kwargs.pop("parameters", {})

    result = __execute_sql(query, parameters, **kwargs)
    transformed_result = result

    return transformed_result


def __execute_sql(query, parameters, **kwargs):
    idx = kwargs.pop("idx", 0)
    # Export the python dictionary parameters to a JSON string
    # where each of the quotes " is replaced with \", so when interpolated
    # in the GraphQL parameters field it is properly escaped
    parameters = json.dumps(parameters).replace('"', '\\"')

    # Sanitize the SQL query for embedding in a GraphQL double-quoted string:
    # escape backslashes first, then double quotes, then newlines/carriage returns
    query = query.replace("\\", "\\\\")
    query = query.replace('"', '\\"')
    query = query.replace("\n", "\\n")
    query = query.replace("\r", "\\r")

    gql_query = f"""{{
        query_{idx}:  runRawSqlQuery(
            sqlQueryText: "{query}"
            sqlQueryParameters: "{parameters}"
        ){{
            columns
            columnTypes
            rows
        }}
    }}"""

    res = execute_gql(gql_query)
    res = __transform_sql_result(res, idx, **kwargs)

    return res


def __transform_sql_result(response, idx, **kwargs):
    result = response[f"query_{idx}"]
    result = pd.DataFrame(result["rows"], columns=result["columns"])

    set_index = kwargs.get("set_index")

    if set_index is None:
        pass
    elif set_index not in result.columns:
        raise SanValidationError(f"""
        Index provided via \'set_index\' to \'execute_sql\' is not a column in the result.
        Got {set_index} but expected one of {result.columns}
        """)
    else:
        result = result.set_index(set_index)

    return result
