from san.available_metrics import (
    _available_metric_for_slug_since,
    _available_metric_versions,
    _available_metrics,
    _available_metrics_for_slug,
)
from san.execute_sql import _execute_sql_with_executor
from san.get import _get_with_executor
from san.get_many import _get_many_with_executor
from san.graphql import DEFAULT_TRANSPORT, _execute_gql, _get_response_headers
from san.metadata import _metadata
from san.metric_complexity import _metric_complexity
from san.utility import _api_calls_made, _api_calls_remaining


class SanClient:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def execute_gql(self, gql_query_str):
        return _execute_gql(gql_query_str, transport=DEFAULT_TRANSPORT, api_key=self.api_key)

    def get_response_headers(self, gql_query_str):
        return _get_response_headers(gql_query_str, transport=DEFAULT_TRANSPORT, api_key=self.api_key)

    def get(self, dataset, **kwargs):
        return _get_with_executor(dataset, self.execute_gql, "SanClient.get", **kwargs)

    def get_many(self, dataset, **kwargs):
        return _get_many_with_executor(dataset, self.execute_gql, "SanClient.get_many", **kwargs)

    def execute_sql(self, **kwargs):
        return _execute_sql_with_executor(self.execute_gql, **kwargs)

    def available_metrics(self):
        return _available_metrics(self.execute_gql)

    def available_metrics_for_slug(self, slug):
        return _available_metrics_for_slug(self.execute_gql, slug)

    def available_metric_versions(self, metric):
        return _available_metric_versions(self.execute_gql, metric)

    def available_metric_for_slug_since(self, metric, slug):
        return _available_metric_for_slug_since(self.execute_gql, metric, slug)

    def metadata(self, metric, arr):
        return _metadata(self.execute_gql, metric, arr)

    def metric_complexity(self, metric, from_date, to_date, interval):
        return _metric_complexity(self.execute_gql, metric, from_date, to_date, interval)

    def api_calls_remaining(self):
        return _api_calls_remaining(self.get_response_headers)

    def api_calls_made(self):
        return _api_calls_made(self.execute_gql)
