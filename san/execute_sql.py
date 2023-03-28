import san.sanbase_graphql
import pandas as pd
from san.graphql import execute_gql, get_response_headers
from san.query import get_gql_query, parse_dataset
from san.transform import transform_timeseries_data_query_result
from san.error import SanError
import json

def execute_sql(**kwargs):
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
    if 'query' in kwargs:
        query = kwargs.pop('query')
    else:
        raise SanError("The 'query' argument is required when calling 'execute_sql'")

    parameters = kwargs.pop('parameters', {})

    result = __execute_sql(query, parameters, **kwargs)
    transformed_result = result

    return transformed_result

def __execute_sql(query, parameters, **kwargs):
    idx = kwargs.pop('idx', 0)
    # Export the python dictionary parameters to a JSON string
    # where each of the quotes " is replaced with \", so when interpolated
    # in the GraphQL parameters field it is properly escaped
    parameters = json.dumps(parameters).replace('"', '\\"')

    # Replace the new lines with explicit new lines \\n. Othewise the
    # GraphQL query is malformed as it does not support multiline strings
    query = query.replace('\n', '\\n')

    gql_query = f"""{{
        query_{idx}:  computeRawClickhouseQuery(
            query: "{query}"
            parameters: "{parameters}"
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
    result = response[f'query_{idx}']
    result = pd.DataFrame(result['rows'], columns=result['columns'])

    set_index = kwargs.get('set_index')

    if set_index == None:
        pass
    elif set_index not in result.columns:
        raise SanError(f"""
        Index provided via \'set_index\' to \'execute_sql\' is not a column in the result.
        Got {set_index} but expected one of {result.columns}
        """)
    else:
        result = result.set_index(set_index)

    return result