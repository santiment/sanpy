import san.pandas_utils
import san.sanbase_graphql_helper as sgh
from san.batch import Batch
from san.error import SanError


def prices(idx, slug, **kwargs):
    query_str = sgh.create_query_str('prices', idx, slug, **kwargs)

    return query_str

def ohlc(idx, slug, **kwargs):
    query_str = sgh.create_query_str('ohlc', idx, slug, **kwargs)

    return query_str

def miners_balance(idx, slug, **kwargs):
    query_str = sgh.create_query_str('miners_balance', idx, slug, **kwargs)

    return query_str

def historical_balance(idx, slug, **kwargs):
    kwargs = sgh.transform_query_args('historical_balance', **kwargs)

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

def top_holders_percent_of_total_supply(idx, slug, **kwargs):
    kwargs = sgh.transform_query_args('top_holders_percent_of_total_supply', **kwargs)

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


def top_transfers(idx, slug, **kwargs):
    kwargs = sgh.transform_query_args('top_transfers', **kwargs)

    query_str = ("""
    query_{idx}: topTransfers(
        {address_selector}
        slug: \"{slug}\",
        from: \"{from_date}\",
        to: \"{to_date}\"
    ){{
    """ + ' '.join(kwargs['return_fields']) + '}}').format(idx=idx, slug=slug, **kwargs)

    return query_str


def eth_top_transactions(idx, slug, **kwargs):
    kwargs = sgh.transform_query_args('eth_top_transactions', **kwargs)

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


def eth_spent_over_time(idx, slug, **kwargs):
    kwargs = sgh.transform_query_args('eth_spent_over_time', **kwargs)

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
    kwargs = sgh.transform_query_args('token_top_transactions', **kwargs)

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
    kwargs = sgh.transform_query_args('emerging_trends', **kwargs)

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
    merged = san.pandas_utils.merge(price_df, ohlc_df)
    if merged.size != 0:
        return merged[return_fields]
    return merged


def __choose_selector_or_slugs(slugs, **kwargs):
    if slugs:
        # The interpolation strings will be surrounded by single quotes
        # but the GraphQL spec requires double quotes.
        selector_or_slugs = f'selector: {{slugs: {slugs}}}'.replace("'", '"')
    else:
        if 'slugs' in kwargs:
            selector_or_slugs = kwargs['slugs']
        elif 'selector' in kwargs:
            selector_or_slugs = kwargs['selector']
        else:
            raise SanError('"slugs" or "selector" must be provided as an argument!')
    
    return selector_or_slugs

def __choose_selector_or_slug(slug, **kwargs):
    if slug:
        selector_or_slug = f'slug:"{slug}"'
    else:
        if 'slug' in kwargs:
            selector_or_slug = kwargs['slug']
        elif 'selector' in kwargs:
            selector_or_slug = kwargs['selector']
        else:
            raise SanError('"slug" or "selector" must be provided as an argument!')

    return selector_or_slug

def get_metric_timeseries_data(idx, metric, slug=None, **kwargs):
    kwargs = sgh.transform_query_args('get_metric', **kwargs)
    selector_or_slug = __choose_selector_or_slug(slug, **kwargs)

    transform_arg = _transform_arg_helper(kwargs)
    query_str = ("""
    query_{idx}: getMetric(metric: \"{metric}\"){{
        timeseriesData(
            {selector_or_slug}
            {transform_arg}
            from: \"{from_date}\"
            to: \"{to_date}\"
            interval: \"{interval}\"
            aggregation: {aggregation}
            includeIncompleteData: {include_incomplete_data}
        ){{
        """ + ' '.join(kwargs['return_fields']) + """
        }}
    }}
    """).format(
        idx=idx,
        metric=metric,
        selector_or_slug=selector_or_slug,
        transform_arg=transform_arg,
        **kwargs
    )

    return query_str

def get_metric_timeseries_data_per_slug(idx, metric, slugs=None, **kwargs):
    kwargs = sgh.transform_query_args('get_metric', **kwargs)
    selector_or_slugs = __choose_selector_or_slugs(slugs, **kwargs)

    transform_arg = _transform_arg_helper(kwargs)
    query_str = ("""
    query_{idx}: getMetric(metric: \"{metric}\"){{
        timeseriesDataPerSlug(
            {selector_or_slugs}
            {transform_arg}
            from: \"{from_date}\"
            to: \"{to_date}\"
            interval: \"{interval}\"
            aggregation: {aggregation}
            includeIncompleteData: {include_incomplete_data}
        ){{
            datetime
            data {{
                slug
                value
            }}
        }}
    }}
    """).format(
        idx=idx,
        metric=metric,
        selector_or_slugs=selector_or_slugs,
        transform_arg=transform_arg,
        **kwargs
    )

    return query_str

def _transform_arg_helper(kwargs):
    transform_arg_str = ''
    if 'transform' in kwargs and isinstance(kwargs['transform'], dict):
        transform_arg_str += 'transform:{'
        for k,v in kwargs['transform'].items():
            if isinstance(v, int):  
                transform_arg_str += f'{k}: {v}\n'
            elif isinstance(v, str):
                transform_arg_str += f'{k}: \"{v}\"\n'
            else:
                raise SanError(f'\"transform\" argument incorrect: {kwargs["transform"]}')
        transform_arg_str += '}'

    return transform_arg_str


def projects(idx, slug, **kwargs):
    if (slug == "erc20"):
        return sgh.erc20_projects(idx, **kwargs)
    elif (slug == "all"):
        return sgh.all_projects(idx, **kwargs)

    raise SanError("Unknown project group: {}".format(slug))


def exchange_funds_flow(idx, slug, **kwargs):
    query_str = sgh.create_query_str('exchange_funds_flow', idx, slug, **kwargs)

    return query_str


def social_volume_projects(idx, **kwargs):
    query_str = """
    query_{idx}: socialVolumeProjects
    """.format(idx=idx)

    return query_str


def social_volume(idx, slug, **kwargs):
    kwargs = sgh.transform_query_args('social_volume', **kwargs)

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
    kwargs = sgh.transform_query_args('topic_search', **kwargs)
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


def get_api_calls_made():
    return """{
    currentUser {
        apiCallsHistory(from: "utc_now-30d", to: "utc_now", interval: "1d", authMethod: APIKEY) {
            apiCallsCount, datetime
        }
    }}"""
