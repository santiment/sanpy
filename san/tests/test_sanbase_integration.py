import san
from san import Batch
from san import sanbase_graphql
from san.tests.utils import two_days_ago, four_days_ago, month_ago

import datetime
from nose.plugins.attrib import attr

params = {
    "project_slug":  "santiment",
    "from_date": month_ago(),
    "to_date": two_days_ago(),
    "interval": "1d",
    "address": "0x1f3df0b8390bb8e9e322972c5e75583e87608ec2"
}

METRICS_USING_ETHEREUM = ["gas_used", "miners_balance", "mining_pools_distribution"]

def ordinary_function_maker(query, slug=params['project_slug']):
    result = san.get(query+'/'+slug,
        from_date=params['from_date'],
        to_date=params['to_date'],
        interval=params['interval']
        )
    return result

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

    assert len(result) > 0
    assert len(result[result.slug == "bitcoin"]) == 0

@attr('integration')
def test_ordinary_ethereum_queries():
    for query in METRICS_USING_ETHEREUM:
        result = ordinary_function_maker(query, "ethereum")

        assert len(result.index) >= 1

@attr('integration')
def test_token_age_consumed():
    result = ordinary_function_maker('token_age_consumed')

    for row in result['tokenAgeConsumed']:
        assert row >= 0
    assert len(result.index) >= 1

@attr('integration')
def test_average_token_age_consumed_in_days():
    result = ordinary_function_maker('average_token_age_consumed_in_days')

    for row in result['tokenAge']:
        assert row >= 0
    assert len(result.index) >= 1

@attr('integration')
def test_transaction_volume():
    result = ordinary_function_maker('transaction_volume')

    for row in result['transactionVolume']:
        assert row >= 0
    assert len(result.index) >= 1

@attr('integration')
def test_github_activity():
    result = ordinary_function_maker('github_activity')

    for row in result['activity']:
        assert row >= 0
    assert len(result.index) >= 1

@attr('integration')
def test_dev_activity():
    result = ordinary_function_maker('dev_activity')

    for row in result['activity']:
        assert row >= 0
    assert len(result.index) >= 1

@attr('integration')
def test_network_growth():
    result = ordinary_function_maker('network_growth')

    for row in result['newAddresses']:
        assert row >= 0
    assert len(result.index) >= 1

@attr('integration')
def test_prices():
    result = ordinary_function_maker('prices')

    assert len(result.index) >= 1

@attr('integration')
def test_historical_balance():
    result = san.get('historical_balance/'+params['project_slug'],
        address=params['address'],
        from_date=params['from_date'],
        to_date=params['to_date'],
        interval=params['interval']
        )
    assert len(result.index) >= 1

@attr('integration')
def test_ohlcv():
    ohlcv_df = san.get(
        "{}/{}".format('ohlcv', params["project_slug"]),
        from_date=params["from_date"],
        to_date=params["to_date"],
        interval=params["interval"]
    )

    assert len(ohlcv_df.index) >= 1
