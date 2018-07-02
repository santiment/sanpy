import pandas as pd
import san.sanbase_graphql
from san.graphql import execute_gql

import warnings


def get(dataset, **kwargs):
    gql_query = get_gql_query(0, dataset, **kwargs)
    gql_query = "{\n" + gql_query + "\n}"
    res = execute_gql(gql_query)
    df = pd.DataFrame(res["query_0"])
    return df


def get_gql_query(idx, dataset, **kwargs):
    data = _parse_dataset(dataset)
    return getattr(san.sanbase_graphql, data)(idx, **kwargs)


def _parse_dataset(dataset):
    root, data = dataset.split("/")
    return data
