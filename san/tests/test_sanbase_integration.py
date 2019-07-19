import san
from san import Batch
from san import sanbase_graphql
from san.tests.utils import two_days_ago, four_days_ago, month_ago
from nose.plugins.attrib import attr


params = {
    "project_slug": "santiment",
    "from_date": month_ago(),
    "to_date": two_days_ago(),
    "interval": "1d",
    "address": "0x1f3df0b8390bb8e9e322972c5e75583e87608ec2"
}

METRICS_USING_ETHEREUM = [
    "gas_used",
    "miners_balance",
    "mining_pools_distribution"]


def _test_ordinary_function(query, graphiql_query, slug=params['project_slug']):
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
    queries = sanbase_graphql.QUERY_MAPPING.keys() - METRICS_USING_ETHEREUM

    batch = Batch()
    for query in queries:
        batch.get(
            "{}/{}".format(query, params["project_slug"]),
            from_date=params["from_date"],
            to_date=params["to_date"],
            interval=params["interval"]
        )
    for query in METRICS_USING_ETHEREUM:
        batch.get(
            "{}/ethereum".format(query),
            from_date=params["from_date"],
            to_date=params["to_date"],
            interval=params["interval"]
        )

    result = batch.execute()

    for df in result:
        assert len(df.index) >= 1


@attr('integration')
def test_batched_queries_different_format():
    batch = Batch()

    batch.get("projects/all")
    batch.get("social_volume_projects")
    batch.get(
        "{}/{}".format('social_volume', 'ethereum'),
        from_date=month_ago(),
        to_date=params["to_date"],
        interval=params["interval"],
        social_volume_type="PROFESSIONAL_TRADERS_CHAT_OVERVIEW"
    )
    batch.get(
        "topic_search/messages",
        source="TELEGRAM",
        search_text="btc",
        from_date=month_ago(),
        to_date=params["to_date"],
        interval=params["interval"]
    )

    batch.get(
        "topic_search/chart_data",
        source="TELEGRAM",
        search_text="btc",
        from_date=month_ago(),
        to_date=params["to_date"],
        interval=params["interval"]
    )

    result = batch.execute()
    for df in result:
        assert len(df.index) >= 1


@attr('integration')
def test_erc20_projects():
    result = san.get("projects/erc20")

    assert result.empty == False
    assert len(result[result.slug == "bitcoin"]) == 0


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
    result = _test_ordinary_function('github_activity', 'githubActivity')


@attr('integration')
def test_dev_activity():
    result = _test_ordinary_function('dev_activity', 'devActivity')


@attr('integration')
def test_network_growth():
    result = _test_ordinary_function('network_growth', 'networkGrowth')


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
    _test_ordinary_function('mining_pools_distribution', 'miningPoolsDistribution', 'ethereum')


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
def test_ohlcv():
    ohlcv_df = san.get(
        "{}/{}".format('ohlcv', params["project_slug"]),
        from_date=params["from_date"],
        to_date=params["to_date"],
        interval=params["interval"]
    )

    assert len(ohlcv_df.index) >= 1
    assert 'DatetimeIndex' in str(type(ohlcv_df.index))
    assert ohlcv_df.empty == False
