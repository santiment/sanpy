import san
from san import Batch, available_metric_for_slug_since
from san.tests.utils import two_days_ago, month_ago
import pytest


params = {
    "project_slug": "santiment",
    "from_date": month_ago(),
    "to_date": two_days_ago(),
    "interval": "1d",
    "address": "0x1f3df0b8390bb8e9e322972c5e75583e87608ec2",
}

# Metrics, which are made with _create_query_string, excluding the ones
# using ETHEREUM
METRICS_EQUAL_FORMAT = [
    "prices",
    "ohlc",
]

# Metrics, which are made with _create_query_string, using ETHEREUM
METRICS_USING_ETHEREUM = ["mvrv_usd"]


def _test_ordinary_function(query, slug=params["project_slug"]):
    result = san.get(query + "/" + slug, from_date=params["from_date"], to_date=params["to_date"], interval=params["interval"])
    assert not result.empty
    assert len(result.index) >= 1
    assert "DatetimeIndex" in str(type(result.index))


@pytest.mark.integration
def test_batched_queries_equal_format():
    batch = Batch()
    for query in METRICS_EQUAL_FORMAT:
        batch.get(
            "{}/{}".format(query, params["project_slug"]),
            from_date=params["from_date"],
            to_date=params["to_date"],
            interval=params["interval"],
        )
    for query in METRICS_USING_ETHEREUM:
        batch.get(
            "{}/ethereum".format(query), from_date=params["from_date"], to_date=params["to_date"], interval=params["interval"]
        )

    result = batch.execute()

    for df in result:
        assert len(df.index) >= 1


@pytest.mark.integration
def test_batched_queries_different_format():
    batch = Batch()

    batch.get("projects/all")
    batch.get("social_volume_projects")
    batch.get(
        "{}/{}".format("social_volume_total", "ethereum"),
        from_date=month_ago(),
        to_date=params["to_date"],
        interval=params["interval"],
        social_volume_type="TELEGRAM_CHATS_OVERVIEW",
    )

    result = batch.execute()
    for df in result:
        assert len(df.index) >= 1


@pytest.mark.integration
def test_erc20_projects():
    result = san.get("projects/erc20")

    assert not result.empty
    assert len(result[result.slug == "bitcoin"]) == 0


@pytest.mark.integration
def test_prices():
    _test_ordinary_function("prices")


@pytest.mark.integration
def test_ohlc():
    _test_ordinary_function("ohlc")


@pytest.mark.integration
def test_historical_balance():
    result = san.get(
        "historical_balance/" + params["project_slug"],
        address=params["address"],
        from_date=params["from_date"],
        to_date=params["to_date"],
        interval=params["interval"],
    )
    assert len(result.index) >= 1
    assert "DatetimeIndex" in str(type(result.index))
    assert not result.empty


@pytest.mark.integration
def test_social_dominance():
    sources = ["ALL", "REDDIT", "TELEGRAM"]
    for item in sources:
        result = san.get(
            "social_dominance_total/" + params["project_slug"],
            from_date=params["from_date"],
            to_date=params["to_date"],
            interval=params["interval"],
            source=item,
        )
        assert len(result.index) >= 1
        assert "DatetimeIndex" in str(type(result.index))
        assert not result.empty


@pytest.mark.integration
def test_top_holders_percent_of_total_supply():
    result = san.get(
        "top_holders_percent_of_total_supply/" + params["project_slug"],
        number_of_holders=10,
        from_date=params["from_date"],
        to_date=params["to_date"],
    )
    assert len(result.index) >= 1
    assert "DatetimeIndex" in str(type(result.index))
    assert not result.empty


@pytest.mark.integration
def test_eth_top_transactions():
    transaction_types = ["ALL", "IN", "OUT"]
    for item in transaction_types:
        result = san.get(
            "eth_top_transactions/" + params["project_slug"],
            from_date="2019-06-11",
            to_date="2019-07-11",
            limit=5,
            transaction_type=item,
        )
        assert len(result.index) >= 1
        assert "DatetimeIndex" in str(type(result.index))
        assert not result.empty


@pytest.mark.integration
def test_eth_spent_over_time():
    result = san.get(
        "eth_spent_over_time/" + params["project_slug"],
        from_date=params["from_date"],
        to_date=params["to_date"],
        interval=params["interval"],
    )
    assert len(result.index) >= 1
    assert "DatetimeIndex" in str(type(result.index))
    assert not result.empty


@pytest.mark.integration
def test_token_top_transactions():
    result = san.get("token_top_transactions/" + params["project_slug"], from_date="2019-06-18", to_date="2019-07-11", limit=5)
    assert len(result.index) >= 1
    assert "DatetimeIndex" in str(type(result.index))
    assert not result.empty


@pytest.mark.integration
def test_all_projects():
    result = san.get("projects/all")

    assert len(result.index) >= 1
    assert not result.empty


@pytest.mark.integration
def test_social_volume_projects():
    result = san.get("social_volume_projects")

    assert len(result.index) >= 1
    assert not result.empty


@pytest.mark.integration
def test_ohlcv():
    ohlcv_df = san.get(
        "{}/{}".format("ohlcv", params["project_slug"]),
        from_date=params["from_date"],
        to_date=params["to_date"],
        interval=params["interval"],
    )

    assert len(ohlcv_df.index) >= 1
    assert "DatetimeIndex" in str(type(ohlcv_df.index))
    assert not ohlcv_df.empty


@pytest.mark.integration
def test_get_metric_timeseries_data():
    get_metric_df = san.get(
        "daily_active_addresses/" + params["project_slug"],
        from_date=params["from_date"],
        to_date=params["to_date"],
        interval="2d",
        aggregation="AVG",
    )

    assert len(get_metric_df) >= 1
    assert "DatetimeIndex" in str(type(get_metric_df.index))
    assert not get_metric_df.empty


@pytest.mark.integration
def test_emerging_trends():
    get_metric_df = san.get("emerging_trends", from_date=params["from_date"], to_date=params["to_date"], interval="1d", size=5)

    assert len(get_metric_df) >= 1
    assert "DatetimeIndex" in str(type(get_metric_df.index))
    assert not get_metric_df.empty


@pytest.mark.integration
def test_available_metrics():
    assert len(san.available_metrics()) >= 1


@pytest.mark.integration
def test_available_metric_for_slug_since():
    assert available_metric_for_slug_since("daily_active_addresses", "santiment") == "2017-07-12T00:00:00Z"


@pytest.mark.integration
def test_metadata():
    result = san.metadata("nvt", arr=["defaultAggregation", "metric"])

    expecter_result = {"defaultAggregation": "AVG", "metric": "nvt"}

    assert result == expecter_result


@pytest.mark.integration
def test_slug_metrics():
    result = san.available_metrics_for_slug("santiment")

    assert len(result) != 0


@pytest.mark.integration
def test_metric_complexity():
    result = san.metric_complexity("price_usd", from_date=params["from_date"], to_date=params["to_date"], interval="1d")

    assert result != 0


@pytest.mark.integration
def test_top_transfers():
    result = san.get("top_transfers/santiment", from_date=params["from_date"], to_date=params["to_date"], interval="1d")

    assert len(result) != 0


@pytest.mark.integration
def test_get_selector():
    result = san.get(
        "price_usd", selector={"slug": "santiment"}, from_date=params["from_date"], to_date=params["to_date"], interval="1d"
    )

    assert len(result) != 0


@pytest.mark.integration
def test_get_slug_kw_arg():
    result = san.get("price_usd", slug="santiment", from_date=params["from_date"], to_date=params["to_date"], interval="1d")

    assert len(result) != 0
