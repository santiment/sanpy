import san
from san import Batch, sanbase_graphql, sanbase_graphql_helper, available_metrics
from san.tests.utils import two_days_ago, four_days_ago, month_ago
from nose.plugins.attrib import attr


params = {
    'project_slug': 'santiment',
    'from_date': month_ago(),
    'to_date': two_days_ago(),
    'interval': '1d',
    'address': '0x1f3df0b8390bb8e9e322972c5e75583e87608ec2'
}

# Metrics, which are made with _create_query_string, excluding the ones
# using ETHEREUM
METRICS_EQUAL_FORMAT = [
    'daily_active_addresses',
    'burn_rate',
    'transaction_volume',
    'token_age_consumed',
    'average_token_age_consumed_in_days',
    'github_activity',
    'dev_activity',
    'network_growth',
    'prices',
    'token_velocity',
    'token_circulation',
    'realized_value',
    'mvrv_ratio',
    'nvt_ratio',
    'daily_active_deposits',
    'share_of_deposits',
    'ohlc',
    'history_twitter_data',
    'exchange_funds_flow',
]
# Metrics, which are made with _create_query_string, using ETHEREUM
METRICS_USING_ETHEREUM = [
    'gas_used',
    'miners_balance',
    'mining_pools_distribution'
]


def _test_ordinary_function(
        query,
        graphiql_query,
        slug=params['project_slug']):
    result = san.get(query + '/' + slug,
                     from_date=params['from_date'],
                     to_date=params['to_date'],
                     interval=params['interval']
                     )
    assert result.empty == False
    assert len(result.index) >= 1
    assert 'DatetimeIndex' in str(type(result.index))


@attr('integration')
def test_batched_queries_equal_format():
    batch = Batch()
    for query in METRICS_EQUAL_FORMAT:
        batch.get(
            "{}/{}".format(query, params['project_slug']),
            from_date=params['from_date'],
            to_date=params['to_date'],
            interval=params['interval']
        )
    for query in METRICS_USING_ETHEREUM:
        batch.get(
            "{}/ethereum".format(query),
            from_date=params['from_date'],
            to_date=params['to_date'],
            interval=params['interval']
        )

    result = batch.execute()

    for df in result:
        assert len(df.index) >= 1


@attr('integration')
def test_batched_queries_different_format():
    batch = Batch()

    batch.get('projects/all')
    batch.get('social_volume_projects')
    batch.get(
        "{}/{}".format('social_volume', 'ethereum'),
        from_date=month_ago(),
        to_date=params['to_date'],
        interval=params['interval'],
        social_volume_type='PROFESSIONAL_TRADERS_CHAT_OVERVIEW'
    )
    batch.get(
        'topic_search',
        source='TELEGRAM',
        search_text='btc',
        from_date=month_ago(),
        to_date=params['to_date'],
        interval=params['interval']
    )

    result = batch.execute()
    for df in result:
        assert len(df.index) >= 1


@attr('integration')
def test_erc20_projects():
    result = san.get('projects/erc20')

    assert result.empty == False
    assert len(result[result.slug == 'bitcoin']) == 0


@attr('integration')
def test_daily_active_addresses():
    _test_ordinary_function('daily_active_addresses', 'dailyActiveAddresses')


@attr('integration')
def test_burn_rate():
    _test_ordinary_function('burn_rate', 'burnRate')


@attr('integration')
def test_gas_used():
    _test_ordinary_function('gas_used', 'gasUsed', 'ethereum')


@attr('integration')
def test_token_age_consumed():
    _test_ordinary_function('token_age_consumed', 'tokenAgeConsumed')


@attr('integration')
def test_average_token_age_consumed_in_days():
    _test_ordinary_function(
        'average_token_age_consumed_in_days',
        'averageTokenAgeConsumedInDays')


@attr('integration')
def test_transaction_volume():
    _test_ordinary_function('transaction_volume', 'transactionVolume')


@attr('integration')
def test_github_activity():
    _test_ordinary_function('github_activity', 'githubActivity')


@attr('integration')
def test_dev_activity():
    _test_ordinary_function('dev_activity', 'devActivity')


@attr('integration')
def test_network_growth():
    _test_ordinary_function('network_growth', 'networkGrowth')


@attr('integration')
def test_prices():
    _test_ordinary_function('prices', 'prices')


@attr('integration')
def test_ohlc():
    _test_ordinary_function('ohlc', 'ohlc')


@attr('integration')
def test_exchange_funds_flow():
    _test_ordinary_function('exchange_funds_flow', 'exchangeFundsFlow')


@attr('integration')
def test_token_velocity():
    _test_ordinary_function('token_velocity', 'tokenVelocity')


@attr('integration')
def test_token_circulation():
    _test_ordinary_function('token_circulation', 'tokenCirculation')


@attr('integration')
def test_realized_value():
    _test_ordinary_function('realized_value', 'realizedValue')


@attr('integration')
def test_mvrv_ratio():
    _test_ordinary_function('mvrv_ratio', 'mvrvRatio')


@attr('integration')
def test_nvt_ratio():
    _test_ordinary_function('nvt_ratio', 'nvtRatio')


@attr('integration')
def test_daily_active_deposits():
    _test_ordinary_function('daily_active_deposits', 'dailyActiveDeposits')


@attr('integration')
def test_share_of_deposits():
    _test_ordinary_function('share_of_deposits', 'shareOfDeposits')


@attr('integration')
def test_miners_balance():
    _test_ordinary_function('miners_balance', 'minersBalance', 'ethereum')


@attr('integration')
def test_mining_pools_distribution():
    _test_ordinary_function(
        'mining_pools_distribution',
        'miningPoolsDistribution',
        'ethereum')


@attr('integration')
def test_history_twitter_data():
    _test_ordinary_function('history_twitter_data', 'historyTwitterData')


@attr('integration')
def test_historical_balance():
    result = san.get('historical_balance/' + params['project_slug'],
                     address=params['address'],
                     from_date=params['from_date'],
                     to_date=params['to_date'],
                     interval=params['interval']
                     )
    assert len(result.index) >= 1
    assert 'DatetimeIndex' in str(type(result.index))
    assert result.empty == False


@attr('integration')
def test_social_dominance():
    sources = [
        'ALL',
        'REDDIT',
        'TELEGRAM',
        'DISCORD',
        'PROFESSIONAL_TRADERS_CHAT']
    for item in sources:
        result = san.get('social_dominance/' + params['project_slug'],
                         from_date=params['from_date'],
                         to_date=params['to_date'],
                         interval=params['interval'],
                         source=item
                         )
        assert len(result.index) >= 1
        assert 'DatetimeIndex' in str(type(result.index))
        assert result.empty == False


@attr('integration')
def test_top_holders_percent_of_total_supply():
    result = san.get(
        'top_holders_percent_of_total_supply/' +
        params['project_slug'],
        number_of_holders=10,
        from_date=params['from_date'],
        to_date=params['to_date'])
    assert len(result.index) >= 1
    assert 'DatetimeIndex' in str(type(result.index))
    assert result.empty == False


@attr('integration')
def test_price_volume_difference():
    currencies = ['USD', 'BTC']
    for item in currencies:
        result = san.get('price_volume_difference/' + params['project_slug'],
                         from_date=params['from_date'],
                         to_date=params['to_date'],
                         interval=params['interval'],
                         currency=item
                         )
        assert len(result.index) >= 1
        assert 'DatetimeIndex' in str(type(result.index))
        assert result.empty == False


@attr('integration')
def test_eth_top_transactions():
    transaction_types = ['ALL', 'IN', 'OUT']
    for item in transaction_types:
        result = san.get('eth_top_transactions/' + params['project_slug'],
                         from_date='2019-06-11',
                         to_date='2019-07-11',
                         limit=5,
                         transaction_type=item
                         )
        assert len(result.index) >= 1
        assert 'DatetimeIndex' in str(type(result.index))
        assert result.empty == False


@attr('integration')
def test_news():
    result = san.get('news/' + params['project_slug'],
                     from_date='2019-04-18',
                     to_date='2019-07-11',
                     size=5
                     )
    assert len(result.index) >= 1
    assert 'DatetimeIndex' in str(type(result.index))
    assert result.empty == False


@attr('integration')
def test_eth_spent_over_time():
    result = san.get('eth_spent_over_time/' + params['project_slug'],
                     from_date=params['from_date'],
                     to_date=params['to_date'],
                     interval=params['interval']
                     )
    assert len(result.index) >= 1
    assert 'DatetimeIndex' in str(type(result.index))
    assert result.empty == False


@attr('integration')
def test_token_top_transactions():
    result = san.get('token_top_transactions/' + params['project_slug'],
                     from_date='2019-06-18',
                     to_date='2019-07-11',
                     limit=5
                     )
    assert len(result.index) >= 1
    assert 'DatetimeIndex' in str(type(result.index))
    assert result.empty == False


@attr('integration')
def test_all_projects():
    result = san.get('projects/all')

    assert len(result.index) >= 1
    assert result.empty == False


@attr('integration')
def test_social_volume_projects():
    result = san.get('social_volume_projects')

    assert len(result.index) >= 1
    assert result.empty == False


@attr('integration')
def test_social_volume():
    social_volume_types = [
        'PROFESSIONAL_TRADERS_CHAT_OVERVIEW',
        'TELEGRAM_CHATS_OVERVIEW',
        'TELEGRAM_DISCUSSION_OVERVIEW',
        'DISCORD_DISCUSSION_OVERVIEW']
    for item in social_volume_types:
        result = san.get('social_volume/' + params['project_slug'],
                         from_date=params['from_date'],
                         to_date=params['to_date'],
                         interval=params['interval'],
                         social_volume_type=item
                         )
        assert len(result.index) >= 1
        assert 'DatetimeIndex' in str(type(result.index))
        assert result.empty == False


@attr('integration')
def test_ohlcv():
    ohlcv_df = san.get(
        "{}/{}".format('ohlcv', params['project_slug']),
        from_date=params['from_date'],
        to_date=params['to_date'],
        interval=params['interval']
    )

    assert len(ohlcv_df.index) >= 1
    assert 'DatetimeIndex' in str(type(ohlcv_df.index))
    assert ohlcv_df.empty == False


@attr('integration')
def test_top_social_gainers_losers():
    tsgl_df = san.get(
        'top_social_gainers_losers',
        from_date=params['from_date'],
        to_date=params['to_date'],
        size=5,
        time_window='2d',
        status='ALL'
    )

    assert len(tsgl_df) >= 1
    assert 'DatetimeIndex' in str(type(tsgl_df.index))
    assert tsgl_df.empty == False


@attr('integration')
def test_get_metric():
    get_metric_df = san.get(
        'daily_active_addresses/' + params['project_slug'],
        from_date=params['from_date'],
        to_date=params['to_date'],
        interval='2d',
        aggregation='AVG'
    )

    assert len(get_metric_df) >= 1
    assert 'DatetimeIndex' in str(type(get_metric_df.index))
    assert get_metric_df.empty == False


@attr('integration')
def test_emerging_trends():
    get_metric_df = san.get(
        'emerging_trends',
        from_date=params['from_date'],
        to_date=params['to_date'],
        interval='1d',
        size=5
    )

    assert len(get_metric_df) >= 1
    assert 'DatetimeIndex' in str(type(get_metric_df.index))
    assert get_metric_df.empty == False


@attr('integration')
def test_available_metrics():
    functions_list = [
        'average_token_age_consumed_in_days',
        'burn_rate',
        'daily_active_deposits',
        'dev_activity',
        'emerging_trends',
        'eth_spent_over_time',
        'eth_top_transactions',
        'exchange_funds_flow',
        'gas_used',
        'github_activity',
        'historical_balance',
        'history_twitter_data',
        'miners_balance',
        'mining_pools_distribution',
        'mvrv_ratio',
        'network_growth',
        'news',
        'nvt_ratio',
        'ohlc',
        'ohlcv',
        'price_volume_difference',
        'prices',
        'projects',
        'realized_value',
        'share_of_deposits',
        'social_dominance',
        'social_volume',
        'social_volume_projects',
        'token_age_consumed',
        'token_circulation',
        'token_top_transactions',
        'token_velocity',
        'top_holders_percent_of_total_supply',
        'top_social_gainers_losers',
        'topic_search',
        'daily_avg_marketcap_usd',
        'daily_avg_price_usd',
        'daily_closing_marketcap_usd',
        'daily_closing_price_usd',
        'daily_high_price_usd',
        'daily_low_price_usd',
        'daily_opening_price_usd',
        'daily_trading_volume_usd',
        'daily_active_addresses',
        'mean_realized_price_usd',
        'mean_realized_price_usd_10y',
        'mean_realized_price_usd_5y',
        'mean_realized_price_usd_3y',
        'mean_realized_price_usd_2y',
        'mean_realized_price_usd_365d',
        'mean_realized_price_usd_180d',
        'mean_realized_price_usd_90d',
        'mean_realized_price_usd_60d',
        'mean_realized_price_usd_30d',
        'mean_realized_price_usd_7d',
        'mean_realized_price_usd_1d',
        'mvrv_usd_long_short_diff',
        'mvrv_usd',
        'mvrv_usd_10y',
        'mvrv_usd_5y',
        'mvrv_usd_3y',
        'mvrv_usd_2y',
        'mvrv_usd_365d',
        'mvrv_usd_180d',
        'mvrv_usd_90d',
        'mvrv_usd_60d',
        'mvrv_usd_30d',
        'mvrv_usd_7d',
        'mvrv_usd_1d',
        'circulation',
        'circulation_10y',
        'circulation_5y',
        'circulation_3y',
        'circulation_2y',
        'circulation_365d',
        'circulation_180d',
        'circulation_90d',
        'circulation_60d',
        'circulation_30d',
        'circulation_7d',
        'circulation_1d',
        'mean_age',
        'realized_value_usd',
        'realized_value_usd_10y',
        'realized_value_usd_5y',
        'realized_value_usd_3y',
        'realized_value_usd_2y',
        'realized_value_usd_365d',
        'realized_value_usd_180d',
        'realized_value_usd_90d',
        'realized_value_usd_60d',
        'realized_value_usd_30d',
        'realized_value_usd_7d',
        'realized_value_usd_1d',
        'velocity',
        'transaction_volume',
        'exchange_inflow',
        'exchange_outflow',
        'exchange_balance',
        'age_destroyed',
        'nvt'
        ]

    assert functions_list == san.available_metrics()
    assert len(san.available_metrics()) >= 1


@attr('integration')
def test_metadata():
    result = san.metadata(
        'nvt',
        arr=['defaultAggregation', 'metric']
    )

    expecter_result = {'defaultAggregation': 'AVG', 'metric': 'nvt'}

    assert result == expecter_result
