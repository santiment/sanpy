import iso8601
import datetime

_DEFAULT_INTERVAL = '1d'
_DEFAULT_SOCIAL_VOLUME_TYPE = 'TELEGRAM_CHATS_OVERVIEW'
_DEFAULT_SOURCE = 'TELEGRAM'
_DEFAULT_SEARCH_TEXT = ''

QUERY_MAPPING = {
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
    # OLD
    'token_velocity': {
        'query': 'tokenVelocity',
        'return_fields': ['datetime', 'tokenVelocity']
    },
    # OLD
    'token_circulation': {
        'query': 'tokenCirculation',
        'return_fields': ['datetime', 'tokenCirculation']
    },
    # OLD
    'realized_value': {
        'query': 'realizedValue',
        'return_fields': ['datetime', 'realizedValue']
    },
    # OLD
    'mvrv_ratio': {
        'query': 'mvrvRatio',
        'return_fields': ['datetime', 'ratio']
    },
    # OLD
    'nvt_ratio': {
        'query': 'nvtRatio',
        'return_fields': ['datetime', 'nvtRatioCirculation', 'nvtRatioTxVolume']
    },
    # OLD
    'daily_active_deposits': {
        'query': 'dailyActiveDeposits',
        'return_fields': ['datetime', 'activeDeposits']
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
    # OLD
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
    'top_transfers': {
        'query': 'topTransfers',
        'return_fields': [
            'datetime',
            ('fromAddress', ['address']),
            ('toAddress', ['address']),
            'trxValue',
            'trxHash'
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
    # OLD
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
    },
    'social_volume_projects': {}
}


def all_projects(idx, **kwargs):
    kwargs = transform_query_args('projects', **kwargs)
    query_str = ("""
    query_{idx}: allProjects
    {{
    """ + ' '.join(kwargs['return_fields']) + '}}').format(idx=idx)

    return query_str


def erc20_projects(idx, **kwargs):
    kwargs = transform_query_args('projects', **kwargs)
    query_str = ("""
    query_{idx}: allErc20Projects
    {{
    """ + ' '.join(kwargs['return_fields']) + '}}').format(idx=idx)

    return query_str


def create_query_str(query, idx, slug, **kwargs):
    kwargs = transform_query_args(query, **kwargs)

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


def transform_selector(selector):
    temp_selector = ''
    for key, value in selector.items():
        if (isinstance(value, str) and value.isdigit()) or isinstance(value, int):
            temp_selector += f'{key}: {value}\n'
        elif isinstance(value, str):
            temp_selector += f'{key}: \"{value}\"\n'
        elif isinstance(value, dict):
            temp_selector += f'{key}:{{{transform_selector(value)}}}\n'
        elif isinstance(value, bool):
            temp_selector += (f'{key}: true\n' if value else f'{key}: false\n')
        elif isinstance(value, list):
            temp_value = map(lambda x: f'"{x}"', value)
            temp_selector += f'{key}: [{",".join(temp_value)}]\n'

    return temp_selector


def transform_query_args(query, **kwargs):
    kwargs['from_date'] = kwargs['from_date'] if 'from_date' in kwargs else _default_from_date()
    kwargs['to_date'] = kwargs['to_date'] if 'to_date' in kwargs else _default_to_date()
    kwargs['interval'] = kwargs['interval'] if 'interval' in kwargs else _DEFAULT_INTERVAL
    kwargs['social_volume_type'] = kwargs['social_volume_type'] if 'social_volume_type' in kwargs else _DEFAULT_SOCIAL_VOLUME_TYPE
    kwargs['source'] = kwargs['source'] if 'source' in kwargs else _DEFAULT_SOURCE
    kwargs['search_text'] = kwargs['search_text'] if 'search_text' in kwargs else _DEFAULT_SEARCH_TEXT
    kwargs['aggregation'] = kwargs['aggregation'] if 'aggregation' in kwargs else 'null'
    kwargs['include_incomplete_data'] = kwargs['include_incomplete_data'] if 'include_incomplete_data' in kwargs else False
    # transform python booleans to strings so it's properly interpolated in the query string
    kwargs['include_incomplete_data'] = 'true' if kwargs['include_incomplete_data'] else 'false'
    if 'selector' in kwargs:
        kwargs['selector'] = f'selector:{{{transform_selector(kwargs["selector"])}}}'

    kwargs['address'] = kwargs['address'] if 'address' in kwargs else ''
    kwargs['transaction_type'] = kwargs['transaction_type'] if 'transaction_type' in kwargs else 'ALL'

    if kwargs['address'] != '':
        if kwargs['transaction_type'] != '':
            kwargs['address_selector'] = f'addressSelector:{{address:\"{kwargs["address"]}\", transactionType: {kwargs["transaction_type"]}}},'
        else:
            kwargs['address_selector'] = f'addressSelector:{{address:\"{kwargs["address"]}\"}},'
    else:
        kwargs['address_selector'] = ''

    kwargs['from_date'] = _format_from_date(kwargs['from_date'])
    kwargs['to_date'] = _format_to_date(kwargs['to_date'])

    if 'return_fields' in kwargs:
        kwargs['return_fields'] = _format_all_return_fields(kwargs['return_fields'])
    else:
        kwargs['return_fields'] = _format_all_return_fields(QUERY_MAPPING[query]['return_fields'])

    return kwargs


def _default_to_date():
    return datetime.datetime.utcnow()


def _default_from_date():
    return datetime.datetime.utcnow() - datetime.timedelta(days=365)


def _format_from_date(datetime_obj_or_str):
    if isinstance(datetime_obj_or_str, str) and 'utc_now' in datetime_obj_or_str:
        return datetime_obj_or_str

    if isinstance(datetime_obj_or_str, datetime.datetime):
        datetime_obj_or_str = datetime_obj_or_str.isoformat()

    return iso8601.parse_date(datetime_obj_or_str).isoformat()


def _format_to_date(datetime_obj_or_str):
    if isinstance(datetime_obj_or_str, str) and 'utc_now' in datetime_obj_or_str:
        return datetime_obj_or_str

    if isinstance(datetime_obj_or_str, datetime.datetime):
      return iso8601.parse_date(datetime_obj_or_str.isoformat())
    
    try:
        # Throw if the string is not date-formated, parse as date otherwise
        datetime.datetime.strptime(datetime_obj_or_str, '%Y-%m-%d')
        dt = iso8601.parse_date(datetime_obj_or_str) + \
            datetime.timedelta(hours=23, minutes=59, seconds=59)
    except:
        dt = iso8601.parse_date(datetime_obj_or_str)
    
    return dt.isoformat()

def _format_all_return_fields(fields):
    while any(isinstance(x, tuple) for x in fields):
        fields = _format_return_fields(fields)
    return fields

def _format_return_fields(fields):
    return list(map(
        lambda el: el[0] + '{{' + ' '.join(el[1]) + '}}' if isinstance(el, tuple) else el
    , fields))
