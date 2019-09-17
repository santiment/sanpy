import san.sanbase_graphql
from san.error import SanError


def get_gql_query(idx, identifier, **kwargs):
  query, separator, slug = identifier.partition("/")

  if slug == '' and separator != '':
    raise SanError('Invalid metric!')
  elif slug == '':
    return getattr(
        san.sanbase_graphql,
        query,
        lambda *args, **kwargs: not_found(query)
    )(idx, **kwargs)
  else:
    return getattr(
        san.sanbase_graphql,
        query,
        lambda *args, **kwargs: not_found(query)
    )(idx, slug, **kwargs)


def parse_dataset(dataset):
    left, _separator, right = dataset.partition("/")
    return [left, right]


def not_found(query):
    raise SanError(query + ' not found')
