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
    'burn_rate': {  # to be removed
        'query': 'burnRate',
        'return_fields': ['datetime', 'burnRate']
    },
    'token_age_consumed': {
        'query': 'tokenAgeConsumed',
        'return_fields': ['datetime', 'tokenAgeConsumed']
    },
    'average_token_age_consumed_in_days': {
        'query': 'averageTokenAgeConsumedInDays',
        'return_fields': ['datetime', 'tokenAge']
    },
    'transaction_volume': {
        'query': 'transactionVolume',
        'return_fields': ['datetime', 'transactionVolume']
    },
    'github_activity': {
        'query': 'githubActivity',
        'return_fields': ['datetime', 'activity']
    },
    'dev_activity': {
        'query': 'devActivity',
        'return_fields': ['datetime', 'activity']
    },
    'network_growth': {
        'query': 'networkGrowth',
        'return_fields': ['datetime', 'newAddresses']
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
    },
    'token_velocity': {
        'query': 'tokenVelocity',
        'return_fields': ['datetime', 'tokenVelocity']
    },
    'token_circulation': {
        'query': 'tokenCirculation',
        'return_fields': ['datetime', 'tokenCirculation']
    },
    'realized_value': {
        'query': 'realizedValue',
        'return_fields': ['datetime', 'nonExchangeRealizedValue', 'realizedValue']
    },
    'mvrv_ratio': {
        'query': 'mvrvRatio',
        'return_fields': ['datetime', 'ratio']
    },
    'nvt_ratio': {
        'query': 'nvtRatio',
        'return_fields': ['datetime', 'nvtRatioCirculation', 'nvtRatioTxVolume']
    },
    'daily_active_deposits': {
        'query': 'dailyActiveDeposits',
        'return_fields': ['datetime', 'activeDeposits']
    },
    'share_of_deposits': {
        'query': 'shareOfDeposits',
        'return_fields': ['activeAddresses', 'activeDeposits', 'datetime', 'shareOfDeposits']
    },
    'gas_used': {
        'query': 'gasUsed',
        'return_fields': ['datetime', 'gasUsed']
    },
    'miners_balance': {
        'query': 'minersBalance',
        'return_fields': ['balance', 'datetime']
    },
    'mining_pools_distribution': {
        'query': 'miningPoolsDistribution',
        'return_fields': ['datetime', 'other', 'top10', 'top3']
    },
    'historical_balance': {
        'query': 'historicalBalance',
        'return_fields': ['balance', 'datetime']
    },
    'social_dominance': {
        'query': 'socialDominance',
        'return_fields': ['datetime', 'dominance']
    },
    'top_holders_percent_of_total_supply': {
        'query': 'topHoldersPercentOfTotalSupply',
        'return_fields': ['datetime', 'inExchanges', 'inTopHoldersTotal', 'outsideExchanges']
    }
}


def daily_active_addresses(idx, slug, **kwargs):
    query_str = _create_query_str(
        'daily_active_addresses', idx, slug, **kwargs)

    return query_str

# to be removed


def burn_rate(idx, slug, **kwargs):
    query_str = _create_query_str('burn_rate', idx, slug, **kwargs)

    return query_str


def transaction_volume(idx, slug, **kwargs):
    query_str = _create_query_str('transaction_volume', idx, slug, **kwargs)

    return query_str


def token_age_consumed(idx, slug, **kwargs):
    query_str = _create_query_str('token_age_consumed', idx, slug, **kwargs)

    return query_str


def average_token_age_consumed_in_days(idx, slug, **kwargs):
    query_str = _create_query_str(
        'average_token_age_consumed_in_days', idx, slug, **kwargs)

    return query_str


def github_activity(idx, slug, **kwargs):
    query_str = _create_query_str('github_activity', idx, slug, **kwargs)

    return query_str


def dev_activity(idx, slug, **kwargs):
    query_str = _create_query_str('dev_activity', idx, slug, **kwargs)

    return query_str


def network_growth(idx, slug, **kwargs):
    query_str = _create_query_str('network_growth', idx, slug, **kwargs)

    return query_str


def prices(idx, slug, **kwargs):
    query_str = _create_query_str('prices', idx, slug, **kwargs)

    return query_str


def token_velocity(idx, slug, **kwargs):
    query_str = _create_query_str('token_velocity', idx, slug, **kwargs)

    return query_str


def token_circulation(idx, slug, **kwargs):
    query_str = _create_query_str('token_circulation', idx, slug, **kwargs)

    return query_str


def realized_value(idx, slug, **kwargs):
    query_str = _create_query_str('realized_value', idx, slug, **kwargs)

    return query_str


def mvrv_ratio(idx, slug, **kwargs):
    query_str = _create_query_str('mvrv_ratio', idx, slug, **kwargs)

    return query_str


def nvt_ratio(idx, slug, **kwargs):
    query_str = _create_query_str('nvt_ratio', idx, slug, **kwargs)

    return query_str


def daily_active_deposits(idx, slug, **kwargs):
    query_str = _create_query_str('daily_active_deposits', idx, slug, **kwargs)

    return query_str


def share_of_deposits(idx, slug, **kwargs):
    query_str = _create_query_str('share_of_deposits', idx, slug, **kwargs)

    return query_str


def ohlc(idx, slug, **kwargs):
    query_str = _create_query_str('ohlc', idx, slug, **kwargs)

    return query_str


def gas_used(idx, slug, **kwargs):
    query_str = _create_query_str('gas_used', idx, slug, **kwargs)

    return query_str


def miners_balance(idx, slug, **kwargs):
    query_str = _create_query_str('miners_balance', idx, slug, **kwargs)

    return query_str


def mining_pools_distribution(idx, slug, **kwargs):
    query_str = _create_query_str(
        'mining_pools_distribution', idx, slug, **kwargs)

    return query_str


def historical_balance(idx, slug, **kwargs):
    kwargs = _transform_query_args(**kwargs)

    query_str = """
    query_{idx}: historicalBalance (
        address: \"{address}\",
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\"
    ){{
        balance,
        datetime
    }}
    """.format(
        idx=idx,
        slug=slug,
        **kwargs
    )

    return query_str


def social_dominance(idx, slug, **kwargs):
    kwargs = _transform_query_args(**kwargs)

    query_str = """
    query_{idx}: socialDominance (
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\",
        source: {source}
    ){{
        datetime,
        dominance
    }}
    """.format(
        idx=idx,
        slug=slug,
        **kwargs
    )

    return query_str


def top_holders_percent_of_total_supply(idx, slug, **kwargs):
    kwargs = _transform_query_args(**kwargs)

    query_str = """
    query_{idx}: topHoldersPercentOfTotalSupply(
        slug: \"{slug}\",
        numberOfHolders: {number_of_holders},
        from: \"{from_date}\",
        to: \"{to_date}\"
    ){{
        datetime,
        inExchanges,
        inTopHoldersTotal,
        outsideExchanges
    }}
    """.format(
        idx=idx,
        slug=slug,
        **kwargs
    )

    return query_str


def eth_top_transactions(idx, slug, **kwargs):
    kwargs = _transform_query_args(**kwargs)

    query_str = """
    query_{idx}: projectBySlug (slug: \"{slug}\"){{
            ethTopTransactions (
                from: \"{from_date}\",
                to: \"{to_date}\",
                limit: {limit},
                transactionType: {transaction_type}
            ){{
        datetime,
        fromAddress{{
            address,
            isExchange
        }},
        toAddress{{
            address,
            isExchange
        }},
        trxHash,
        trxValue
        }}
    }}
    """.format(
        idx=idx,
        slug=slug,
        **kwargs
    )

    return query_str


def ohlcv(idx, slug, **kwargs):
    return_fields = [
        'openPriceUsd',
        'closePriceUsd',
        'highPriceUsd',
        'lowPriceUsd',
        'volume',
        'marketcap']

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
        totalSupply,
        marketSegment
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
        totalSupply,
        marketSegment
    }}
    """.format(idx=idx)

    return query_str


def exchange_funds_flow(idx, slug, **kwargs):
    query_str = _create_query_str('exchange_funds_flow', idx, slug, **kwargs)

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

    kwargs['from_date'] = _format_from_date(kwargs['from_date'])
    kwargs['to_date'] = _format_to_date(kwargs['to_date'])

    return kwargs


def _default_to_date():
    return datetime.datetime.now()


def _default_from_date():
    return datetime.datetime.now() - datetime.timedelta(days=365)


def _format_return_fields(return_fields):
    return ",\n".join(return_fields)


def _format_from_date(datetime_obj_or_str):
    if isinstance(datetime_obj_or_str, datetime.datetime):
        datetime_obj_or_str = datetime_obj_or_str.isoformat()

    return iso8601.parse_date(datetime_obj_or_str).isoformat()


def _format_to_date(datetime_obj_or_str):
    if isinstance(datetime_obj_or_str, datetime.datetime):
        datetime_obj_or_str = datetime_obj_or_str.isoformat()

    dt = iso8601.parse_date(datetime_obj_or_str) + \
        datetime.timedelta(hours=23, minutes=59, seconds=59)
    return dt.isoformat()
