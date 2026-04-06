import inspect
import json

import pandas as pd
import requests

import san.sanbase_graphql
from san.api_config import ApiConfig
from san.env_vars import SANBASE_GQL_HOST
from san.error import SanError
from san.query import get_gql_query, parse_dataset
from san.query_constants import CUSTOM_QUERIES, DEPRECATED_QUERIES, NO_SLUG_QUERIES
from san.sanbase_graphql_helper import QUERY_MAPPING, _format_from_date, _format_to_date
from san.transform import transform_timeseries_data_per_slug_query_result, transform_timeseries_data_query_result


class ClientConfig:
    def __init__(self, api_key=None):
        self.api_key = api_key


class SanClient:
    def __init__(self, api_key=None, config=None):
        self.config = config or ClientConfig()
        if api_key is not None:
            self.config.api_key = api_key

    def execute_gql(self, gql_query_str):
        headers = self._headers()

        try:
            response = requests.post(SANBASE_GQL_HOST, json={"query": gql_query_str}, headers=headers)
        except requests.exceptions.RequestException as e:
            raise SanError("Error running query: ({})".format(e))

        if response.status_code == 200:
            return self._handle_success_response(response, gql_query_str)

        if self._result_has_gql_errors(response):
            error_response = response.json()["errors"]["details"]
        else:
            error_response = ""
        raise SanError(
            "Error running query. Status code: {}.\n {}\n {}".format(response.status_code, error_response, gql_query_str)
        )

    def get_response_headers(self, gql_query_str):
        headers = self._headers()

        try:
            response = requests.post(SANBASE_GQL_HOST, json={"query": gql_query_str}, headers=headers)
        except requests.exceptions.RequestException as e:
            raise SanError("Error running query: ({})".format(e))

        if response.status_code == 200:
            return response.headers

        if self._result_has_gql_errors(response):
            error_response = response.json()["errors"]["details"]
        else:
            error_response = ""
        raise SanError(
            "Error running query. Status code: {}.\n {}\n {}".format(response.status_code, error_response, gql_query_str)
        )

    def get(self, dataset, **kwargs):
        query, slug = parse_dataset(dataset)
        if slug or query in NO_SLUG_QUERIES:
            return self._get_metric_slug_string_selector(query, slug, dataset, **kwargs)
        if query and not slug:
            return self._get(query, **kwargs)

    def get_many(self, dataset, **kwargs):
        query, _ = parse_dataset(dataset)
        if not ("selector" in kwargs or "slugs" in kwargs):
            raise SanError(
                """
            Invalid call of the get function,you need to either
            give <metric>/<slug> as a first argument or give a slug
            or selector as a key-word argument!"""
            )

        idx = kwargs.pop("idx", 0)
        gql_query = "{" + san.sanbase_graphql.get_metric_timeseries_data_per_slug(idx, query, **kwargs) + "}"
        res = self.execute_gql(gql_query)

        return transform_timeseries_data_per_slug_query_result(idx, query, res)

    def execute_sql(self, **kwargs):
        if "query" in kwargs:
            query = kwargs.pop("query")
        else:
            raise SanError("The 'query' argument is required when calling 'execute_sql'")

        parameters = kwargs.pop("parameters", {})
        idx = kwargs.pop("idx", 0)
        parameters = json.dumps(parameters).replace('"', '\\"')
        query = query.replace("\n", "\\n")

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

        response = self.execute_gql(gql_query)
        result = pd.DataFrame(response[f"query_{idx}"]["rows"], columns=response[f"query_{idx}"]["columns"])

        set_index = kwargs.get("set_index")
        if set_index is None:
            return result
        if set_index not in result.columns:
            raise SanError(
                f"""
        Index provided via \'set_index\' to \'execute_sql\' is not a column in the result.
        Got {set_index} but expected one of {result.columns}
        """
            )
        return result.set_index(set_index)

    def available_metrics(self):
        sanbase_graphql_functions = inspect.getmembers(san.sanbase_graphql, inspect.isfunction)
        all_functions = list(map(lambda x: x[0], sanbase_graphql_functions)) + self.execute_gql("{query: getAvailableMetrics}")[
            "query"
        ]
        return list(filter(lambda x: not (str.startswith(x, "get_metric") or str.startswith(x, "_")), all_functions))

    def available_metrics_for_slug(self, slug):
        query_str = (
            """{{
        projectBySlug(slug: \"{slug}\"){{
            availableMetrics
        }}
    }}
    """
        ).format(slug=slug)

        return self.execute_gql(query_str)["projectBySlug"]["availableMetrics"]

    def available_metric_for_slug_since(self, metric, slug):
        query_str = (
            """{{
        getMetric(metric: \"{metric}\"){{
            availableSince(slug: \"{slug}\")
        }}
    }}
    """
        ).format(metric=metric, slug=slug)

        return self.execute_gql(query_str)["getMetric"]["availableSince"]

    def metadata(self, metric, arr):
        query_str = (
            """{{
    getMetric (metric: \"{metric}\") {{
        metadata {{
            """
            + " ".join(arr)
            + """
        }}
    }}
    }}
    """
        ).format(metric=metric)

        return self.execute_gql(query_str)["getMetric"]["metadata"]

    def metric_complexity(self, metric, from_date, to_date, interval):
        query_str = (
            """{{
    getMetric (metric: \"{metric}\") {{
        timeseriesDataComplexity(
            from: \"{from_date}\",
            to: \"{to_date}\",
            interval: \"{interval}\"
        )
        }}
    }}
    """
        ).format(metric=metric, from_date=_format_from_date(from_date), to_date=_format_to_date(to_date), interval=interval)

        return self.execute_gql(query_str)["getMetric"]["timeseriesDataComplexity"]

    def api_calls_remaining(self):
        gql_query_str = san.sanbase_graphql.get_api_calls_made()
        response_headers = self.get_response_headers(gql_query_str)
        try:
            return {
                "month_remaining": response_headers["x-ratelimit-remaining-month"],
                "hour_remaining": response_headers["x-ratelimit-remaining-hour"],
                "minute_remaining": response_headers["x-ratelimit-remaining-minute"],
            }
        except KeyError:
            raise SanError("There are no limits for this API Key.")

    def api_calls_made(self):
        gql_query_str = san.sanbase_graphql.get_api_calls_made()
        try:
            response = self.execute_gql(gql_query_str)["currentUser"]["apiCallsHistory"]
        except Exception as exc:
            if "the results are empty" in str(exc):
                raise SanError("No API Key detected...") from exc
            raise SanError(str(exc)) from exc

        try:
            return list(map(lambda x: (x["datetime"], x["apiCallsCount"]), response))
        except (KeyError, TypeError) as exc:
            raise SanError(f"Error parsing API response: {exc}") from exc

    def _headers(self):
        if self.config.api_key:
            return {"authorization": "Apikey {}".format(self.config.api_key)}
        return {}

    def _get_metric_slug_string_selector(self, query, slug, dataset, **kwargs):
        idx = kwargs.pop("idx", 0)

        if query in DEPRECATED_QUERIES:
            print(
                "**NOTICE**\n{} will be deprecated in a future version, please use {} instead".format(
                    query, DEPRECATED_QUERIES[query]
                )
            )

        if query in CUSTOM_QUERIES:
            return getattr(san.sanbase_graphql, query)(idx, slug, **kwargs)
        if query in QUERY_MAPPING.keys():
            gql_query = "{" + get_gql_query(idx, dataset, **kwargs) + "}"
        else:
            if slug != "":
                gql_query = "{" + san.sanbase_graphql.get_metric_timeseries_data(idx, query, slug, **kwargs) + "}"
            else:
                raise SanError("Invalid metric!")
        res = self.execute_gql(gql_query)

        return transform_timeseries_data_query_result(idx, query, res)

    def _get(self, query, **kwargs):
        if not ("selector" in kwargs or "slug" in kwargs):
            raise SanError(
                """
            Invalid call of the get function,you need to either
            give <metric>/<slug> as a first argument or give a slug
            or selector as a key-word argument!"""
            )
        idx = kwargs.pop("idx", 0)

        if query in QUERY_MAPPING.keys():
            gql_query = "{" + get_gql_query(idx, query, **kwargs) + "}"
        else:
            gql_query = "{" + san.sanbase_graphql.get_metric_timeseries_data(idx, query, **kwargs) + "}"

        res = self.execute_gql(gql_query)

        return transform_timeseries_data_query_result(idx, query, res)

    def _handle_success_response(self, response, gql_query_str):
        if self._result_has_gql_errors(response):
            raise SanError("GraphQL error occured running query {} \n errors: {}".format(gql_query_str, response.json()["errors"]))
        if self._exist_not_empty_result(response):
            return response.json()["data"]
        raise SanError("Error running query, the results are empty. Status code: {}.\n {}".format(response.status_code, gql_query_str))

    def _result_has_gql_errors(self, response):
        return "errors" in response.json().keys()

    def _exist_not_empty_result(self, response):
        return "data" in response.json().keys() and len(list(filter(lambda x: x is not None, response.json()["data"].values()))) > 0


_default_client = None


def get_default_client():
    global _default_client
    if _default_client is None:
        _default_client = SanClient(config=ClientConfig())

    _default_client.config.api_key = ApiConfig.api_key
    return _default_client
