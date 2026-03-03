from typing import Any, NoReturn

import san.sanbase_graphql
from san.error import SanValidationError


def get_gql_query(idx: int, identifier: str, **kwargs: Any) -> str:
    query, separator, slug = identifier.partition("/")

    if slug == "" and separator != "":
        raise SanValidationError("Invalid metric!")
    elif slug == "":
        return getattr(san.sanbase_graphql, query, lambda *args, **kwargs: not_found(query))(idx, **kwargs)
    else:
        return getattr(san.sanbase_graphql, query, lambda *args, **kwargs: not_found(query))(idx, slug, **kwargs)


def parse_dataset(dataset: str) -> list[str]:
    left, _separator, right = dataset.partition("/")
    return [left, right]


def not_found(query: str) -> NoReturn:
    raise SanValidationError(query + " not found")
