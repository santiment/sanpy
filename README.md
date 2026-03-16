# sanpy

[![PyPI version](https://badge.fury.io/py/sanpy.svg)](https://badge.fury.io/py/sanpy)

Python client library for the [Santiment API](https://api.santiment.net/) — access on-chain, social, development, and price metrics for 3000+ crypto assets. Results are returned as pandas DataFrames with datetime indexing.

For full API documentation and metric definitions, see [Santiment Academy](https://academy.santiment.net/sanapi/).

## Table of contents

- [Installation](#installation)
- [Configuration](#configuration)
  - [Environment variable](#environment-variable)
  - [Programmatic](#programmatic)
  - [Obtaining an API key](#obtaining-an-api-key)
- [Fetching data](#fetching-data)
  - [Single asset](#single-asset)
  - [Multiple assets](#multiple-assets)
  - [Using selectors](#using-selectors)
  - [Raw GraphQL queries](#raw-graphql-queries)
- [SQL queries (Santiment Queries)](#sql-queries-santiment-queries)
- [Metric discovery](#metric-discovery)
  - [Available metrics](#available-metrics)
  - [Available metrics for a slug](#available-metrics-for-a-slug)
  - [Metric/asset availability since](#metricasset-availability-since)
  - [Versioned metrics](#versioned-metrics)
  - [Metric metadata](#metric-metadata)
  - [Metric complexity](#metric-complexity)
- [Batching queries](#batching-queries)
- [Transforms and aggregation](#transforms-and-aggregation)
- [Include incomplete data](#include-incomplete-data)
- [Rate limit tools](#rate-limit-tools)
- [Available projects](#available-projects)
- [Non-standard metrics](#non-standard-metrics)
- [Extras](#extras)
- [Development](#development)

## Installation

Install from [PyPI](https://pypi.org/project/sanpy/):

```bash
pip install sanpy
```

Upgrade to the latest version:

```bash
pip install --upgrade sanpy
```

### Extra packages

There are a few utilities in the `san/extras/` directory for backtesting and event studies. To install their dependencies:

```bash
pip install sanpy[extras]
```

## Configuration

Some metrics require a paid [SanAPI plan](https://academy.santiment.net/products-and-plans/sanapi-plans/) to access real-time or full historical data. You can provide an API key in two ways:

### Environment variable

If the `SANPY_APIKEY` environment variable is set when you import `san`, it is loaded automatically:

```shell
export SANPY_APIKEY="my_api_key"
```

```python
import san
san.ApiConfig.api_key  # 'my_api_key'
```

### Programmatic

```python
import san
san.ApiConfig.api_key = "my_api_key"
```

### Obtaining an API key

1. [Log in to Sanbase](https://app.santiment.net/login).
2. Go to the [Account page](https://app.santiment.net/account).
3. Under **API Keys**, click **Generate new api key**.

## Fetching data

The library provides two main functions for fetching timeseries data:

- **`san.get(metric, slug=..., ...)`** — fetch data for a single metric/asset pair.
- **`san.get_many(metric, slugs=[...], ...)`** — fetch data for a single metric across multiple assets. This counts as 1 API call.

**Common parameters:**

| Parameter | Description | Default |
|---|---|---|
| `slug` / `slugs` | Project identifier(s), as listed in [Available projects](#available-projects) | — |
| `selector` | Dict for flexible targeting (address, label, holdersCount, etc.) | — |
| `from_date` | Start of the period (ISO 8601 string) | 365 days ago |
| `to_date` | End of the period (ISO 8601 string) | now |
| `interval` | Data point spacing — fixed (`1d`, `1h`, `5m`, `1w`) or semantic (`toStartOfMonth`, `toStartOfWeek`) | `'1d'` |

The returned result is a `pandas.DataFrame` indexed by `datetime`.
For `get`, the value column is named `value`.
For `get_many`, each column is named after the asset slug.

### Single asset

```python
import san

san.get(
    "price_usd",
    slug="bitcoin",
    from_date="2022-01-01",
    to_date="2022-01-05",
    interval="1d"
)
```

```
datetime                   value
2022-01-01 00:00:00+00:00  47686.811509
2022-01-02 00:00:00+00:00  47345.220564
2022-01-03 00:00:00+00:00  46458.116959
2022-01-04 00:00:00+00:00  45928.661063
2022-01-05 00:00:00+00:00  43569.003348
```

Using default parameters (last 1 year of data with 1 day interval):

```python
san.get("daily_active_addresses", slug="santiment")
san.get("price_usd", slug="santiment")
```

### Multiple assets

```python
import san

san.get_many(
    "price_usd",
    slugs=["bitcoin", "ethereum", "tether"],
    from_date="2022-01-01",
    to_date="2022-01-05",
    interval="1d"
)
```

```
datetime                   bitcoin       ethereum     tether
2022-01-01 00:00:00+00:00  47686.811509  3769.696916  1.000500
2022-01-02 00:00:00+00:00  47345.220564  3829.565045  1.000460
2022-01-03 00:00:00+00:00  46458.116959  3761.380274  1.000165
2022-01-04 00:00:00+00:00  45928.661063  3795.890130  1.000208
2022-01-05 00:00:00+00:00  43569.003348  3550.386882  1.000122
```

### Using selectors

The `selector` parameter enables querying by organization, contract address, label, and more:

```python
import san

# Development activity by GitHub organization
san.get(
    "dev_activity",
    selector={"organization": "google"},
    from_date="2022-01-01",
    to_date="2022-01-05",
    interval="1d"
)
```

```
datetime                    value
2022-01-01 00:00:00+00:00   176.0
2022-01-02 00:00:00+00:00   129.0
2022-01-03 00:00:00+00:00   562.0
2022-01-04 00:00:00+00:00  1381.0
2022-01-05 00:00:00+00:00  1334.0
```

```python
# Transactions for a specific contract address
san.get(
    "contract_transactions_count",
    selector={"contractAddress": "0x00000000219ab540356cBB839Cbe05303d7705Fa"},
    from_date="2022-01-01",
    to_date="2022-01-05",
    interval="1d"
)
```

```
datetime                   value
2022-01-01 00:00:00+00:00   90.0
2022-01-02 00:00:00+00:00  339.0
2022-01-03 00:00:00+00:00  486.0
2022-01-04 00:00:00+00:00  314.0
2022-01-05 00:00:00+00:00  328.0
```

```python
# Amount held by top N holders
san.get(
    "amount_in_top_holders",
    selector={"slug": "santiment", "holdersCount": 10},
    from_date="2022-01-01",
    to_date="2022-01-05",
    interval="1d"
)
```

```
datetime                   value
2022-01-01 00:00:00+00:00  7.391186e+07
2022-01-02 00:00:00+00:00  7.391438e+07
2022-01-03 00:00:00+00:00  7.391984e+07
2022-01-04 00:00:00+00:00  7.391984e+07
2022-01-05 00:00:00+00:00  7.391984e+07
```

```python
# DEX trade volume (requires PRO API key)
san.get(
    "total_trade_volume_by_dex",
    selector={"slug": "ethereum", "label": "decentralized_exchange", "owner": "UniswapV2"},
    from_date="2022-01-01",
    to_date="2022-01-05",
    interval="1d"
)
```

```
datetime                    value
2022-01-01 00:00:00+00:00   96882.176846
2022-01-02 00:00:00+00:00   85184.970249
2022-01-03 00:00:00+00:00  107489.846163
2022-01-04 00:00:00+00:00  105204.677503
2022-01-05 00:00:00+00:00  174178.848916
```

> **Note:** The legacy format `san.get("metric/slug", ...)` still works for backwards compatibility, but using the separate `slug` parameter is recommended.

### Raw GraphQL queries

For queries not covered by built-in functions, you can execute arbitrary GraphQL against the
[Santiment API](https://api.santiment.net/graphiql):

```python
import san
import pandas as pd

result = san.graphql.execute_gql("""
{
  getMetric(metric: "price_usd") {
    timeseriesDataPerSlug(
      selector: {slugs: ["ethereum", "bitcoin"]}
      from: "2022-05-05T00:00:00Z"
      to: "2022-05-08T00:00:00Z"
      interval: "1d") {
        datetime
        data{
          value
          slug
        }
    }
  }
}
""")

data = result['getMetric']['timeseriesDataPerSlug']
rows = []
for datetime_point in data:
    row = {'datetime': datetime_point['datetime']}
    for slug_data in datetime_point['data']:
        row[slug_data['slug']] = slug_data['value']
    rows.append(row)

df = pd.DataFrame(rows)
df.set_index('datetime', inplace=True)
```

```
datetime              bitcoin       ethereum
2022-05-05T00:00:00Z  36575.142133  2749.213042
2022-05-06T00:00:00Z  36040.922350  2694.979684
2022-05-07T00:00:00Z  35501.954144  2636.092958
```

Fetching a specific set of fields for a project:

```python
import san
import pandas as pd

result = san.graphql.execute_gql("""{
  projectBySlug(slug: "santiment") {
    slug
    name
    ticker
    infrastructure
    mainContractAddress
    twitterLink
  }
}""")

pd.DataFrame(result["projectBySlug"], index=[0])
```

```
  infrastructure                         mainContractAddress       name       slug ticker                        twitterLink
0            ETH  0x7c5a0ce9267ed19b22f8cae653f198e3e8daf098  Santiment  santiment    SAN  https://twitter.com/santimentfeed
```

## SQL queries (Santiment Queries)

[Santiment Queries](https://academy.santiment.net/santiment-queries/) lets you execute SQL queries against a ClickHouse database hosted by Santiment. See the [documentation](https://academy.santiment.net/santiment-queries/) for available tables and query syntax. Requires an API key.

Basic query returning a pandas DataFrame:

```python
import san

san.execute_sql(query="SELECT * FROM daily_metrics_v2 LIMIT 5")
```

```
   metric_id  asset_id                    dt  value           computed_at
0         10      1369  2015-07-17T00:00:00Z    0.0  2020-10-21T08:48:42Z
1         10      1369  2015-07-18T00:00:00Z    0.0  2020-10-21T08:48:42Z
2         10      1369  2015-07-19T00:00:00Z    0.0  2020-10-21T08:48:42Z
3         10      1369  2015-07-20T00:00:00Z    0.0  2020-10-21T08:48:42Z
4         10      1369  2015-07-21T00:00:00Z    0.0  2020-10-21T08:48:42Z
```

Use `set_index` to set a column as the DataFrame index:

```python
san.execute_sql(query="SELECT * FROM daily_metrics_v2 LIMIT 5", set_index="dt")
```

```
dt                    metric_id  asset_id  value           computed_at
2015-07-17T00:00:00Z         10      1369    0.0  2020-10-21T08:48:42Z
2015-07-18T00:00:00Z         10      1369    0.0  2020-10-21T08:48:42Z
2015-07-19T00:00:00Z         10      1369    0.0  2020-10-21T08:48:42Z
2015-07-20T00:00:00Z         10      1369    0.0  2020-10-21T08:48:42Z
2015-07-21T00:00:00Z         10      1369    0.0  2020-10-21T08:48:42Z
```

### Parameterized queries

Use `{{key}}` placeholders in the query and pass a `parameters` dict:

```python
san.execute_sql(query="""
    SELECT
        get_metric_name(metric_id) AS metric,
        get_asset_name(asset_id) AS asset,
        dt,
        argMax(value, computed_at)
    FROM daily_metrics_v2
    WHERE
        asset_id = get_asset_id({{slug}}) AND
        metric_id = get_metric_id({{metric}}) AND
        dt >= now() - INTERVAL {{last_n_days}} DAY
    GROUP BY dt, metric_id, asset_id
    ORDER BY dt ASC
""",
parameters={'slug': 'bitcoin', 'metric': 'daily_active_addresses', 'last_n_days': 7},
set_index="dt")
```

```
dt                                    metric    asset        value
2023-03-22T00:00:00Z  daily_active_addresses  bitcoin     941446.0
2023-03-23T00:00:00Z  daily_active_addresses  bitcoin     913215.0
2023-03-24T00:00:00Z  daily_active_addresses  bitcoin     884271.0
2023-03-25T00:00:00Z  daily_active_addresses  bitcoin     906851.0
2023-03-26T00:00:00Z  daily_active_addresses  bitcoin     835596.0
2023-03-27T00:00:00Z  daily_active_addresses  bitcoin    1052637.0
2023-03-28T00:00:00Z  daily_active_addresses  bitcoin     311566.0
```

## Metric discovery

### Available metrics

```python
san.available_metrics()
```

### Available metrics for a slug

```python
san.available_metrics_for_slug("santiment")
```

### Metric/asset availability since

Fetch the earliest datetime for which a metric is available for a given slug:

```python
san.available_metric_for_slug_since(metric="daily_active_addresses", slug="santiment")
```

### Versioned metrics

Some metrics support multiple versions (e.g., `"1.0"` and `"2.0"`).

Check which versions are available:

```python
import san

san.available_metric_versions("social_dominance_total")
# ['1.0', '2.0']
```

Pass `version` to `san.get` or `san.get_many` to select a specific version:

```python
san.get(
    "social_dominance_total",
    slug="bitcoin",
    from_date="2026-01-01",
    to_date="2026-01-10",
    interval="1d",
    version="2.0"
)

san.get_many(
    "social_dominance_total",
    slugs=["bitcoin", "ethereum"],
    from_date="2026-01-01",
    to_date="2026-01-10",
    interval="1d",
    version="2.0"
)
```

### Metric metadata

Fetch metadata for a metric, including access restrictions and available slugs:

```python
san.metadata(
    "nvt",
    arr=[
        "availableSlugs",
        "defaultAggregation",
        "humanReadableName",
        "isAccessible",
        "isRestricted",
        "restrictedFrom",
        "restrictedTo",
    ]
)
```

Example result:

```python
{
    "availableSlugs": ["0chain", "0x", "0xbtc", ...],
    "defaultAggregation": "AVG",
    "humanReadableName": "NVT (Using Circulation)",
    "isAccessible": True,
    "isRestricted": True,
    "restrictedFrom": "2020-03-21T08:44:14Z",
    "restrictedTo": "2020-06-17T08:44:14Z"
}
```

- `availableSlugs` — All slugs that have data for this metric.
- `defaultAggregation` — Aggregation function used when querying large intervals.
- `humanReadableName` — Human-readable metric name.
- `isAccessible` — Whether the metric is accessible with your current API plan. For example, `circulation_1d` requires a `PRO` plan.
- `isRestricted` — Whether time restrictions apply to your current plan (`Free` if no API key is configured).
- `restrictedFrom` / `restrictedTo` — The available date range for your current plan.

### Metric complexity

Each API request has a [complexity](https://academy.santiment.net/sanapi/complexity/) that depends on the date range, interval, metric, and subscription plan. The maximum complexity per request is 50,000.

```python
san.metric_complexity(
    metric="price_usd",
    from_date="2020-01-01",
    to_date="2020-02-20",
    interval="1d"
)
```

If a request exceeds the limit, break it into smaller date ranges or upgrade your plan.

## Batching queries

Two batch classes let you execute multiple queries efficiently:

> **Note:** Each query in a batch still counts as a separate API call.
> To fetch a metric for multiple assets in a single API call, use `san.get_many` instead.

`AsyncBatch` executes queries concurrently in separate HTTP requests.
Concurrency is controlled by the `max_workers` parameter (default: 10). Because each query
runs in its own request, you avoid [complexity](https://academy.santiment.net/sanapi/complexity/)
accumulation. Supports both `get` and `get_many`.

```python
from san import AsyncBatch

batch = AsyncBatch()

batch.get(
    "daily_active_addresses",
    slug="santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

batch.get(
    "transaction_volume",
    slug="santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

batch.get_many(
    "daily_active_addresses",
    slugs=["bitcoin", "ethereum"],
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

[daa, trx_volume, daa_many] = batch.execute(max_workers=10)
```

> **Note:** The older `Batch` class is deprecated. It combines all queries into a single GraphQL
> document, which causes [complexity](https://academy.santiment.net/sanapi/complexity/) to accumulate
> and requests to be rejected for larger batches. Use `AsyncBatch` instead — the `get`, `get_many`,
> and `execute` methods share the same interface, so switching only requires changing the import.

## Transforms and aggregation

Apply server-side transformations to the data:

```python
san.get(
    "price_usd",
    slug="santiment",
    from_date="2020-06-01",
    to_date="2021-06-05",
    interval="1d",
    transform={"type": "moving_average", "moving_average_base": 100},
    aggregation="LAST"
)
```

**Supported transforms:**

| Type | Description |
|---|---|
| `moving_average` | Replace each value with the average of the last `moving_average_base` values |
| `consecutive_differences` | Replace each value with the difference from the previous value (V_i - V_{i-1}) |
| `percent_change` | Replace each value with the percent change from the previous value ((V_i / V_{i-1} - 1) * 100) |

`aggregation` controls how values within each interval are combined (e.g., `LAST`, `AVG`, `SUM`).

## Include incomplete data

Daily metrics exclude the current (incomplete) day by default. For example, `daily_active_addresses` queried at 08:00 would only reflect one-third of the day's activity. To include the partial current-day value:

```python
san.get(
    "daily_active_addresses",
    slug="bitcoin",
    from_date="utc_now-3d",
    to_date="utc_now",
    interval="1d",
    include_incomplete_data=True
)
```

## Rate limit tools

Four utility functions help you handle [API rate limits](https://academy.santiment.net/sanapi/rate-limits/):

- `san.is_rate_limit_exception(exception)` — check if an exception was caused by rate limiting.
- `san.rate_limit_time_left(exception)` — seconds until the rate limit resets.
- `san.api_calls_made()` — API calls made per day.
- `san.api_calls_remaining()` — remaining calls for the current month, hour, and minute.

Example:

```python
import time
import san

try:
    san.get(
        "price_usd",
        slug="santiment",
        from_date="utc_now-30d",
        to_date="utc_now",
        interval="1d"
    )
except Exception as e:
    if san.is_rate_limit_exception(e):
        rate_limit_seconds = san.rate_limit_time_left(e)
        print(f"Rate limited. Sleeping for {rate_limit_seconds}s")
        time.sleep(rate_limit_seconds)

calls_by_day = san.api_calls_made()
calls_remaining = san.api_calls_remaining()
```

## Available projects

Returns a DataFrame with all projects tracked by the Santiment API. The `slug` column is the unique identifier used in all metric queries.

```python
san.get("projects/all")
```

```
                 name             slug ticker   totalSupply
0              0chain           0chain    ZCN     400000000
1                  0x               0x    ZRX    1000000000
2           0xBitcoin            0xbtc  0xBTC      20999984
3     0xcert Protocol           0xcert    ZXC     500000000
4              1World           1world    1WO      37219453
...
```

## Non-standard metrics

The following metrics have non-standard response formats and are not included in `san.available_metrics()`.

### Price metrics

**Marketcap, Price USD, Price BTC, and Trading Volume:**

```python
san.get(
    "prices",
    slug="santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
```

**OHLCV (Open, High, Low, Close, Volume, Marketcap):**

> This query cannot be batched and does not support the separate `slug`/`selector` argument format.

```python
san.get(
    "ohlcv/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
```

```
datetime                   openPriceUsd  closePriceUsd  highPriceUsd  lowPriceUsd   volume  marketcap
2018-06-01 00:00:00+00:00  1.24380       1.27668        1.26599       1.19099       852857  7.736268e+07
2018-06-02 00:00:00+00:00  1.26136       1.30779        1.27612       1.20958      1242520  7.864724e+07
2018-06-03 00:00:00+00:00  1.28270       1.28357        1.24625       1.21872      1032910  7.844339e+07
2018-06-04 00:00:00+00:00  1.23276       1.24910        1.18528       1.18010       617451  7.604326e+07
```

### Historical balance

Returns the historical balance for an ERC-20 token or ETH address:

```python
san.get(
    "historical_balance",
    slug="santiment",
    address="0x1f3df0b8390bb8e9e322972c5e75583e87608ec2",
    from_date="2019-04-18",
    to_date="2019-04-23",
    interval="1d"
)
```

```
datetime                     balance
2019-04-18 00:00:00+00:00  382338.33
2019-04-19 00:00:00+00:00  382338.33
2019-04-20 00:00:00+00:00  382338.33
2019-04-21 00:00:00+00:00  215664.33
2019-04-22 00:00:00+00:00  215664.33
```

### Ethereum top transactions

Top ETH transactions for a project's team wallets. `transaction_type` can be `ALL`, `IN`, or `OUT`.

```python
san.get(
    "eth_top_transactions",
    slug="santiment",
    from_date="2019-04-18",
    to_date="2019-04-30",
    limit=5,
    transaction_type="ALL"
)
```

Example result (shortened for convenience):

```
datetime                           fromAddress  fromAddressInExchange           toAddress  toAddressInExchange              trxHash      trxValue
2019-04-29 21:33:31+00:00  0xe76fe52a251c8f...                  False  0x45d6275d9496b...                False  0x776cd57382456a...        100.00
2019-04-29 21:21:18+00:00  0xe76fe52a251c8f...                  False  0x468bdccdc334f...                False  0x848414fb5c382f...         40.95
2019-04-19 14:14:52+00:00  0x1f3df0b8390bb8...                  False  0xd69bc0585e05e...                False  0x590512e1f1fbcf...         19.48
2019-04-19 14:09:58+00:00  0x1f3df0b8390bb8...                  False  0x723fb5c14eaff...                False  0x78e0720b9e72d1...         15.15
```

### Ethereum spent over time

ETH spent per interval from a project's team wallets:

```python
san.get(
    "eth_spent_over_time",
    slug="santiment",
    from_date="2019-04-18",
    to_date="2019-04-23",
    interval="1d"
)
```

```
datetime                    ethSpent
2019-04-18 00:00:00+00:00   0.000000
2019-04-19 00:00:00+00:00  34.630284
2019-04-20 00:00:00+00:00   0.000000
2019-04-21 00:00:00+00:00   0.000158
2019-04-22 00:00:00+00:00   0.000000
```

### Token top transactions

Top transactions for a project's token:

```python
san.get(
    "token_top_transactions",
    slug="santiment",
    from_date="2019-04-18",
    to_date="2019-04-30",
    limit=5
)
```

Example result (shortened for convenience):

```
datetime                           fromAddress  fromAddressInExchange           toAddress  toAddressInExchange              trxHash      trxValue
2019-04-21 13:51:59+00:00  0x1f3df0b8390bb8...                  False  0x5eaae5e949952...                False  0xdbced935b09dd0...  166674.00000
2019-04-28 07:43:38+00:00  0x0a920bfdf7f977...                  False  0x868074aab18ea...                False  0x5f2214d34bcdc3...   33181.82279
2019-04-28 07:53:32+00:00  0x868074aab18ea3...                  False  0x876eabf441b2e...                 True  0x90bd286da38a2b...   33181.82279
2019-04-26 14:38:45+00:00  0x876eabf441b2ee...                   True  0x76af586d041d6...                False  0xe45b86f415e930...   28999.64023
2019-04-30 15:17:28+00:00  0x876eabf441b2ee...                   True  0x1f4a90043cf2d...                False  0xc85892b9ef8c64...   20544.42975
```

### Top transfers

Top token transfers for a project. Optionally filter by `address` and `transaction_type` (`ALL`, `IN`, `OUT`):

```python
san.get(
    "top_transfers",
    slug="santiment",
    from_date="utc_now-30d",
    to_date="utc_now",
)
```

Example result (shortened for convenience):

```
                          fromAddress   toAddress     trxHash       trxValue
datetime
2021-06-17 00:16:26+00:00  0xa48df...  0x876ea...  0x62a56...  136114.069733
2021-06-17 00:10:05+00:00  0xbd3c2...  0x876ea...  0x732a5...  117339.779890
2021-06-19 21:36:03+00:00  0x59646...  0x0d45b...  0x5de31...  112336.882707
...
```

Filter by address and transaction type:

```python
san.get(
    "top_transfers",
    slug="santiment",
    address="0x26e068650ae54b6c1b149e1b926634b07e137b9f",
    transaction_type="ALL",
    from_date="utc_now-30d",
    to_date="utc_now",
)
```

```
                          fromAddress  toAddress    trxHash   trxValue
datetime
2021-06-13 09:14:01+00:00  0x26e06...  0xfd3d...  0x4af6...  69854.528
2021-06-13 09:13:01+00:00  0x876ea...  0x26e0...  0x18c1...  69854.528
2021-06-14 08:54:52+00:00  0x876ea...  0x26e0...  0xdceb...  59920.591
...
```

### Emerging trends

Trending words in crypto social media for a given period:

```python
san.get(
    "emerging_trends",
    from_date="2019-07-01",
    to_date="2019-07-02",
    interval="1d",
    size=5
)
```

```
datetime                        score    word
2019-07-01 00:00:00+00:00  375.160034    lnbc
2019-07-01 00:00:00+00:00  355.323281    dent
2019-07-01 00:00:00+00:00  268.653820    link
2019-07-01 00:00:00+00:00  231.721809  shorts
2019-07-01 00:00:00+00:00  206.812798     btt
2019-07-02 00:00:00+00:00  209.343752  bounce
2019-07-02 00:00:00+00:00  135.412811    vidt
2019-07-02 00:00:00+00:00  116.842801     bat
2019-07-02 00:00:00+00:00   98.517600  bottom
2019-07-02 00:00:00+00:00   89.309975   haiku
```

## Extras

Backtesting and event study utilities are available in `san/extras/`. See the [examples/extras](examples/extras) folder for usage.

## Development

It is recommended to use [pipenv](https://github.com/pypa/pipenv) for managing the local development environment.

```bash
# Set up the project
pipenv install

# Install the package in editable mode
pipenv run pip install -e .

# Install dev dependencies (ruff, pytest)
pipenv run pip install -e '.[dev]'

# Install extra dependencies (numpy, matplotlib, scipy, mlfinlab)
pipenv run pip install -e '.[extras]'

# Run tests (integration tests are excluded by default)
pipenv run pytest

# Run integration tests (requires SANPY_APIKEY)
pipenv run pytest -m integration

# Lint
ruff check .

# Format
ruff format
```
