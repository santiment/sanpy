import inspect
import san.sanbase_graphql
from san.graphql import get_all_available_metrics

def available_metrics():
    sanbase_graphql_functions = inspect.getmembers(san.sanbase_graphql, inspect.isfunction)
    all_functions =  list(map(lambda x: x[0], sanbase_graphql_functions)) + get_all_available_metrics()
    all_functions.remove('get_metric')
    return all_functions
