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
    'history_twitter_data': {
        'query': 'historyTwitterData',
        'return_fields': ['datetime', 'followers_count']
    },
    'historical_balance': {
        'query': 'historicalBalance',
        'return_fields': ['datetime', 'balance']
    },
    'social_dominance': {
        'query': 'socialDominance',
        'return_fields': ['datetime', 'dominance']
    },
    'top_holders_percent_of_total_supply': {
        'query': 'topHoldersPercentOfTotalSupply',
        'return_fields': ['datetime', 'inExchanges', 'outsideExchanges', 'inTopHoldersTotal']
    },
    'projects': {
        'query': 'allProjects',
        'return_fields': ['name', 'slug', 'ticker', 'totalSupply', 'marketSegment']
    },
    'get_metric': {
        'query': 'getMetric',
        'return_fields': [
            'datetime',
            'value'
        ]
    },
    'topic_search': {
        'query': 'topicSearch',
        'return_fields': [
            ('chartData', ['datetime, ''mentionsCount'])
        ]
    },
    'eth_top_transactions': {
        'query': 'ethTopTransactions',
        'return_fields': [
            'datetime',
            ('fromAddress', ['address', 'isExchange']),
            ('toAddress', ['address', 'isExchange']),
            'trxHash',
            'trxValue'
        ]
    },
    'token_top_transactions': {
        'query': 'tokenTopTransactions',
        'return_fields': [
            'datetime',
            ('fromAddress', ['address', 'isExchange']),
            ('toAddress', ['address', 'isExchange']),
            'trxHash',
            'trxValue'
        ]
    },
    'eth_spent_over_time': {
        'query': 'ethSpentOverTime',
        'return_fields': [
            'datetime',
            'ethSpent'
        ]
    },
    'news': {
        'query': 'news',
        'return_fields': [
            'datetime',
            'title',
            'sourceName',
            'url',
            'description'
        ]
    },
    'price_volume_difference': {
        'query': 'priceVolumeDiff',
        'return_fields': [
            'datetime',
            'priceChange',
            'priceVolumeDiff',
            'volumeChange'
        ]
    },
    'social_volume': {
        'query': 'socialVolume',
        'return_fields': [
            'datetime',
            'mentionsCount'
        ]
    },
    'top_social_gainers_losers': {
        'query': 'topSocialGainersLosers',
        'return_fields': [
            'datetime',
            ('projects', ['change', 'slug', 'status'])
        ]
    },
    'emerging_trends': {
        'query': 'getTrendingWords',
        'return_fields': [
            'datetime',
            ('topWords', ['score', 'word'])
        ]
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
    kwargs = _transform_query_args('historical_balance', **kwargs)

    query_str = ("""
    query_{idx}: historicalBalance (
        address: \"{address}\",
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\"
    ){{
    """ + ' '.join(kwargs['return_fields']) + '}}').format(
        idx=idx,
        slug=slug,
        **kwargs
    )

    return query_str


def social_dominance(idx, slug, **kwargs):
    kwargs = _transform_query_args('social_dominance', **kwargs)

    query_str = ("""
    query_{idx}: socialDominance (
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\",
        source: {source}
    ){{
    """ + ' '.join(kwargs['return_fields']) + '}}').format(
        idx=idx,
        slug=slug,
        **kwargs
    )

    return query_str


def top_holders_percent_of_total_supply(idx, slug, **kwargs):
    kwargs = _transform_query_args('top_holders_percent_of_total_supply', **kwargs)

    query_str = ("""
    query_{idx}: topHoldersPercentOfTotalSupply(
        slug: \"{slug}\",
        numberOfHolders: {number_of_holders},
        from: \"{from_date}\",
        to: \"{to_date}\"
    ){{
    """ + ' '.join(kwargs['return_fields']) + '}}').format(
        idx=idx,
        slug=slug,
        **kwargs
    )

    return query_str


def history_twitter_data(idx, slug, **kwargs):
    query_str = _create_query_str('history_twitter_data', idx, slug, **kwargs)

    return query_str


def price_volume_difference(idx, slug, **kwargs):
    kwargs = _transform_query_args('price_volume_difference', **kwargs)

    query_str = ("""
    query_{idx}: priceVolumeDiff (
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\",
        currency: \"{currency}\"
    ){{
    """ + ' '.join(kwargs['return_fields']) + '}}').format(
        idx=idx,
        slug=slug,
        **kwargs
    )

    return query_str


def eth_top_transactions(idx, slug, **kwargs):
    kwargs = _transform_query_args('eth_top_transactions', **kwargs)

    query_str = ("""
    query_{idx}: projectBySlug (slug: \"{slug}\"){{
            ethTopTransactions (
                from: \"{from_date}\",
                to: \"{to_date}\",
                limit: {limit},
                transactionType: {transaction_type}
            ){{
            """ + ' '.join(kwargs['return_fields']) + '}}}}').format(
        idx=idx,
        slug=slug,
        **kwargs
    )

    return query_str


def news(idx, tag, **kwargs):
    kwargs = _transform_query_args('news', **kwargs)

    query_str = ("""
    query_{idx}: news(
        tag: \"{tag}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        size: {size}
    ){{
    """ + ' '.join(kwargs['return_fields']) + '}}').format(
        idx=idx,
        tag=tag,
        **kwargs
    )

    return query_str


def eth_spent_over_time(idx, slug, **kwargs):
    kwargs = _transform_query_args('eth_spent_over_time', **kwargs)

    query_str = """
    query_{idx}: projectBySlug (slug: \"{slug}\"){{
            ethSpentOverTime(
                from: \"{from_date}\",
                to: \"{to_date}\",
                interval: \"{interval}\"
            ){{
        datetime,
        ethSpent
        }}
    }}
    """.format(
        idx=idx,
        slug=slug,
        **kwargs
    )

    return query_str


def token_top_transactions(idx, slug, **kwargs):
    kwargs = _transform_query_args('token_top_transactions', **kwargs)

    query_str = """
    query_{idx}: projectBySlug (slug: \"{slug}\"){{
            tokenTopTransactions (
                from: \"{from_date}\",
                to: \"{to_date}\",
                limit: {limit}
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


def emerging_trends(idx, **kwargs):
    kwargs = _transform_query_args('emerging_trends', **kwargs)

    query_str = ("""
    query_{idx}: getTrendingWords (
        from: \"{from_date}\",
        to: \"{to_date}\",
        size: {size},
        interval: \"{interval}\"
    ){{""" + ' '.join(kwargs['return_fields']) + """
    }}
    """).format(
        idx=idx,
        **kwargs
    )

    return query_str


def top_social_gainers_losers(idx, **kwargs):
    kwargs = _transform_query_args('top_social_gainers_losers', **kwargs)

    query_str = ("""
    query_{idx}: topSocialGainersLosers(
                    from: \"{from_date}\",
                    to: \"{to_date}\",
                    status: {status},
                    size: {size},
                    timeWindow: \"{time_window}\"
                ){{
    """ + ' '.join(kwargs['return_fields']) + """
    }}
    """).format(
        idx=idx,
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


def get_metric(idx, metric, slug, **kwargs):
    kwargs = _transform_query_args('get_metric', **kwargs)

    query_str = ("""
    query_{idx}: getMetric(metric: \"{metric}\"){{
        timeseriesData(
            slug: \"{slug}\"
            from: \"{from_date}\"
            to: \"{to_date}\"
            interval: \"{interval}\",
            aggregation: {aggregation}
        ){{
        """ + ' '.join(kwargs['return_fields']) + """
        }}
    }}
    """).format(
        idx=idx,
        metric=metric,
        slug=slug,
        **kwargs
    )

    return query_str


def projects(idx, slug, **kwargs):
    if (slug == "erc20"):
        return erc20_projects(idx, **kwargs)
    elif (slug == "all"):
        return all_projects(idx, **kwargs)

    raise SanError("Unknown project group: {}".format(slug))


def all_projects(idx, **kwargs):
    kwargs = _transform_query_args('projects', **kwargs)
    query_str = ("""
    query_{idx}: allProjects
    {{
    """ + ' '.join(kwargs['return_fields']) + '}}').format(idx=idx)

    return query_str


def erc20_projects(idx, **kwargs):
    kwargs = _transform_query_args('projects', **kwargs)
    query_str = ("""
    query_{idx}: allErc20Projects
    {{
    """ + ' '.join(kwargs['return_fields']) + '}}').format(idx=idx)

    return query_str


def exchange_funds_flow(idx, slug, **kwargs):
    query_str = _create_query_str('exchange_funds_flow', idx, slug, **kwargs)

    return query_str


def social_volume_projects(idx, **kwargs):
    query_str = """
    query_{idx}: socialVolumeProjects
    """.format(idx=idx)

    return query_str


def social_volume(idx, slug, **kwargs):
    kwargs = _transform_query_args('social_volume', **kwargs)

    query_str = ("""
    query_{idx}: socialVolume (
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\",
        socialVolumeType: {social_volume_type}
    ){{
    """ + ' '.join(kwargs['return_fields']) + '}}').format(
        idx=idx,
        slug=slug,
        **kwargs
    )

    return query_str


def topic_search(idx, **kwargs):
    kwargs = _transform_query_args('topic_search', **kwargs)
    query_str = ("""
    query_{idx}: topicSearch (
        source: {source},
        searchText: \"{search_text}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\"
    ){{
    """ + ' '.join(kwargs['return_fields']) + """
    }}
    """).format(
        idx=idx,
        **kwargs
    )

    return query_str


def _create_query_str(query, idx, slug, **kwargs):
    kwargs = _transform_query_args(query, **kwargs)

    query_str = ("""
    query_{idx}: {query}(
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\",
        interval: \"{interval}\"
    ){{
    """ +  ' '.join(kwargs['return_fields']) + '}}'
    ).format(
        query=QUERY_MAPPING[query]['query'],
        idx=idx,
        slug=slug,
        **kwargs
    )

    return query_str


def _transform_query_args(query, **kwargs):
    kwargs['from_date'] = kwargs['from_date'] if 'from_date' in kwargs else _default_from_date()
    kwargs['to_date'] = kwargs['to_date'] if 'to_date' in kwargs else _default_to_date()
    kwargs['interval'] = kwargs['interval'] if 'interval' in kwargs else DEFAULT_INTERVAL
    kwargs['social_volume_type'] = kwargs['social_volume_type'] if 'social_volume_type' in kwargs else DEFAULT_SOCIAL_VOLUME_TYPE
    kwargs['source'] = kwargs['source'] if 'source' in kwargs else DEFAULT_SOURCE
    kwargs['search_text'] = kwargs['search_text'] if 'search_text' in kwargs else DEFAULT_SEARCH_TEXT
    kwargs['aggregation'] = kwargs['aggregation'] if 'aggregation' in kwargs else "null"

    kwargs['from_date'] = _format_from_date(kwargs['from_date'])
    kwargs['to_date'] = _format_to_date(kwargs['to_date'])

    if 'return_fields' in kwargs:
        kwargs['return_fields'] = _format_all_return_fields(kwargs['return_fields'])
    else:
        kwargs['return_fields'] = _format_all_return_fields(QUERY_MAPPING[query]['return_fields'])

    return kwargs


def _default_to_date():
    return datetime.datetime.now()


def _default_from_date():
    return datetime.datetime.now() - datetime.timedelta(days=365)


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

def _format_all_return_fields(fields):
    while any(isinstance(x, tuple) for x in fields):
        fields = _format_return_fields(fields)
    return fields

def _format_return_fields(fields):
    return list(map(
        lambda el: el[0] + '{{' + ' '.join(el[1]) + '}}' if isinstance(el, tuple) else el
    , fields))
