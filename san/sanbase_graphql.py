import iso8601
import datetime
from san.pandas_utils import merge
from san.batch import Batch
from san.error import SanError


DEFAULT_INTERVAL = '1d'
DEFAULT_SOCIAL_VOLUME_TYPE = 'PROFESSIONAL_TRADERS_CHAT_OVERVIEW'
DEFAULT_SOURCE = 'TELEGRAM'
DEFAULT_SEARCH_TEXT = ''

QUERY_MAPPING = {
    'daily_active_addresses': {
        'query': 'dailyActiveAddresses',
        'return_fields': ['datetime', 'activeAddresses']
    },
    'burn_rate': {
        'query': 'burnRate',
        'return_fields': ['datetime', 'burnRate']
    },
    'transaction_volume': {
        'query': 'transactionVolume',
        'return_fields': ['datetime', 'transactionVolume']
    },
    'github_activity': {
        'query': 'githubActivity',
        'return_fields': ['datetime', 'activity']
    },
    'prices': {
        'query': 'historyPrice',
        'return_fields': ['datetime', 'priceUsd', 'priceBtc', 'marketcap', 'volume']
    },
    'ohlc': {
        'query': 'ohlc',
        'return_fields': ['datetime', 'openPriceUsd', 'closePriceUsd', 'highPriceUsd', 'lowPriceUsd']
    },
    'exchange_funds_flow': {
        'query': 'exchangeFundsFlow',
        'return_fields': ['datetime', 'inOutDifference']
    }
}


def daily_active_addresses(idx, slug, **kwargs):
    query_str = _create_query_str(
        'daily_active_addresses', idx, slug, **kwargs)

    return query_str


def burn_rate(idx, slug, **kwargs):
    query_str = _create_query_str('burn_rate', idx, slug, **kwargs)

    return query_str


def transaction_volume(idx, slug, **kwargs):
    query_str = _create_query_str('transaction_volume', idx, slug, **kwargs)

    return query_str


def github_activity(idx, slug, **kwargs):
    query_str = _create_query_str('github_activity', idx, slug, **kwargs)

    return query_str


def prices(idx, slug, **kwargs):
    query_str = _create_query_str('prices', idx, slug, **kwargs)

    return query_str


def ohlc(idx, slug, **kwargs):
    query_str = _create_query_str('ohlc', idx, slug, **kwargs)

    return query_str


def ohlcv(idx, slug, **kwargs):
    return_fields = ['openPriceUsd', 'closePriceUsd', 'highPriceUsd', 'lowPriceUsd', 'volume', 'marketcap']

    batch = Batch()
    batch.get(
        "prices/{slug}".format(slug=slug),
        **kwargs
    )
    batch.get(
        "ohlc/{slug}".format(slug=slug),
        **kwargs
    )
    [price_df, ohlc_df] = batch.execute()
    merged = merge(price_df, ohlc_df)
    return merged[return_fields]

def projects(idx, slug, **kwargs):
    if (slug == "erc20"):
        return erc20_projects(idx, **kwargs)
    elif (slug == "all"):
        return all_projects(idx, **kwargs)

    raise SanError("Unknown project group: {}".format(slug))

def all_projects(idx, **kwargs):
    query_str = """
    query_{idx}: allProjects
    {{
        name,
        slug,
        ticker,
        totalSupply
    }}
    """.format(idx=idx)

    return query_str

def erc20_projects(idx, **kwargs):
    query_str = """
    query_{idx}: allErc20Projects
    {{
        name,
        slug,
        ticker,
        totalSupply
    }}
    """.format(idx=idx)

    return query_str


def exchange_funds_flow(idx, slug, **kwargs):
    query_str = _create_query_str('exchange_funds_flow', idx, slug, **kwargs)

    return query_str


def erc20_exchange_funds_flow(idx, _slug, **kwargs):
    kwargs = _transform_query_args(**kwargs)

    query_str = """
    query_{idx}: erc20ExchangeFundsFlow (
        from: \"{from_date}\",
        to: \"{to_date}\"
    ){{
        ticker,
        contract,
        exchangeIn,
        exchangeOut,
        exchangeDiff,
        exchangeInUsd,
        exchangeOutUsd,
        exchangeDiffUsd,
        percentDiffExchangeDiffUsd,
        exchangeVolumeUsd,
        percentDiffExchangeVolumeUsd,
        exchangeInBtc,
        exchangeOutBtc,
        exchangeDiffBtc,
        percentDiffExchangeDiffBtc,
        exchangeVolumeBtc,
        percentDiffExchangeVolumeBtc
    }}
    """.format(
        idx=idx,
        **kwargs
    )

    return query_str


def social_volume_projects(idx, _slug, **kwargs):
    query_str = """
    query_{idx}: socialVolumeProjects
    """.format(idx=idx)

    return query_str


def social_volume(idx, slug, **kwargs):
    kwargs = _transform_query_args(**kwargs)

    query_str = """
    query_{idx}: socialVolume (
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\",
        socialVolumeType: {social_volume_type}
    ){{
        mentionsCount,
        datetime
    }}
    """.format(
        idx=idx,
        slug=slug,
        **kwargs
    )

    return query_str


def topic_search(idx, field, **kwargs):
    kwargs = _transform_query_args(**kwargs)
    return_fields = {
        'messages': """
        messages {
            datetime
            text
        }
        """,
        'chart_data': """
        chartData {
            mentionsCount
            datetime
        }
        """
    }

    query_str = """
    query_{idx}: topicSearch (
        source: {source},
        searchText: \"{search_text}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\"
    ){{
        {return_fields}
    }}
    """.format(
        idx=idx,
        return_fields=return_fields[field],
        **kwargs
    )

    return query_str


def _create_query_str(query, idx, slug, **kwargs):
    kwargs = _transform_query_args(**kwargs)

    query_str = """
    query_{idx}: {query}(
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\"
    ){{
        {return_fields}
    }}
    """.format(
        query=QUERY_MAPPING[query]['query'],
        idx=idx,
        slug=slug,
        return_fields=_format_return_fields(
            QUERY_MAPPING[query]['return_fields']),
        **kwargs
    )

    return query_str


def _transform_query_args(**kwargs):
    kwargs['from_date'] = kwargs['from_date'] if 'from_date' in kwargs else _default_from_date()
    kwargs['to_date'] = kwargs['to_date'] if 'to_date' in kwargs else _default_to_date()
    kwargs['interval'] = kwargs['interval'] if 'interval' in kwargs else DEFAULT_INTERVAL
    kwargs['social_volume_type'] = kwargs['social_volume_type'] if 'social_volume_type' in kwargs else DEFAULT_SOCIAL_VOLUME_TYPE
    kwargs['source'] = kwargs['source'] if 'source' in kwargs else DEFAULT_SOURCE
    kwargs['search_text'] = kwargs['search_text'] if 'search_text' in kwargs else DEFAULT_SEARCH_TEXT

    kwargs['from_date'] = _format_date(kwargs['from_date'])
    kwargs['to_date'] = _format_date(kwargs['to_date'])

    return kwargs


def _default_to_date():
    return datetime.datetime.now()


def _default_from_date():
    return datetime.datetime.now() - datetime.timedelta(days=365)


def _format_return_fields(return_fields):
    return ",\n".join(return_fields)


def _format_date(datetime_obj_or_str):
    if isinstance(datetime_obj_or_str, datetime.datetime):
        datetime_obj_or_str = datetime_obj_or_str.isoformat()

    return iso8601.parse_date(datetime_obj_or_str).isoformat()
