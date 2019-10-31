import inspect
import san.sanbase_graphql
from san.v2_metrics_list import V2_METRIC_QUERIES

def available_metrics():
    sanbase_graphql_functions = inspect.getmembers(san.sanbase_graphql, inspect.isfunction)
    all_functions =  list(map(lambda x: x[0], sanbase_graphql_functions)) + V2_METRIC_QUERIES
    all_functions.remove('get_metric')
    return all_functions
