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
    "interval": "1d"
}

@attr('integration')
def test_batched_queries_equal_format():
    queries = sanbase_graphql.QUERY_MAPPING.keys()

    batch = Batch()
    for query in queries:
        batch.get(
            "{}/{}".format(query, params["project_slug"]),
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
def test_ohlcv():
    ohlcv_df = san.get(
        "{}/{}".format('ohlcv', params["project_slug"]),
        from_date=params["from_date"],
        to_date=params["to_date"],
        interval=params["interval"]
    )

    assert len(ohlcv_df.index) >= 1

@attr('integration')
# FIXME: test to be added. Currently query timeouts
def test_erc20_exchange_funds_flow():
    pass
