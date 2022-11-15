# sanpy
---
[![PyPI version](https://badge.fury.io/py/sanpy.svg)](https://badge.fury.io/py/sanpy)

Python client for cryptocurrency data from [Santiment API](https://api.santiment.net/).
This library provides utilities for accessing the GraphQL Santiment API endpoint
and convert the result to pandas dataframe.

More documentation regarding the API and definitions of metrics can be found on [Santiment Academy]()

# Table of contents

- [Table of contents](#table-of-contents)
  - [Installation](#installation)
  - [Upgrade to latest version](#upgrade-to-latest-version)
  - [Install extra packages](#install-extra-packages)
  - [Restricted metrics](#restricted-metrics)
  - [Configuration](#configuration)
    - [Read the API key from the environment](#read-the-api-key-from-the-environment)
    - [Manually configure an API key](#manually-configure-an-api-key)
    - [How to obtain an API key](#how-to-obtain-an-api-key)
  - [Getting the data](#getting-the-data)
    - [Using the provided functions](#using-the-provided-functions)
    - [Execute an arbitrary GraphQL request](#execute-an-arbitrary-graphql-request)
  - [Available metrics](#available-metrics)
  - [Available Metrics for Slug](#available-metrics-for-slug)
  - [Fetch timeseries metric](#fetch-timeseries-metric)
  - [Fetching metadata for a metric](#fetching-metadata-for-a-metric)
  - [Batching multiple queries](#batching-multiple-queries)
  - [Rate Limit Tools](#rate-limit-tools)
  - [Metric Complexity](#metric-complexity)
  - [Include Incomplete Data Flag](#include-incomplete-data-flag)
  - [Metric/Asset pair available cince](#metricasset-pair-available-cince)
  - [Transform the result](#transform-the-result)
  - [Available projects](#available-projects)
  - [Non-standard metrics](#non-standard-metrics)
    - [Other Price metrics](#other-price-metrics)
      - [Marketcap, Price USD, Price BTC and Trading Volume](#marketcap-price-usd-price-btc-and-trading-volume)
      - [Open, High, Close, Low Prices, Volume, Marketcap](#open-high-close-low-prices-volume-marketcap)
    - [Mining Pools Distribution](#mining-pools-distribution)
    - [Historical Balance](#historical-balance)
    - [Ethereum Top Transactions](#ethereum-top-transactions)
    - [Ethereum Spent Over Time](#ethereum-spent-over-time)
    - [Token Top Transactions](#token-top-transactions)
    - [Top Transfers](#top-transfers)
    - [Emerging Trends](#emerging-trends)
    - [Top Social Gainers Losers](#top-social-gainers-losers)
  - [Extras](#extras)
  - [Development](#development)
  - [Running tests](#running-tests)
  - [Running integration tests](#running-integration-tests)

## Installation

To install the latest [sanpy from PyPI](https://pypi.org/project/sanpy/):
```bash
pip install sanpy
```

## Upgrade to latest version

```bash
pip install --upgrade sanpy
```

## Install extra packages

There are few scripts under [extras](/san/extras) directory related to backtesting and event studies. To install their dependencies use:

```bash
pip install sanpy[extras]
```

## Restricted metrics

In order to access real-time data or historical data for some of the metrics,
you'll need to set the [API key](#configuration), generated from an account with
a paid API plan.

## Configuration

You can provide an API key which gives access to the restricted metrics in two different ways:

### Read the API key from the environment

During loading of the `san` module, if the `SANPY_APIKEY` exists, its content
is read and set as the API key.

```shell
export SANPY_APIKEY="my_apikey"
```
```python
import san
>>> san.ApiConfig.api_key
'my_apikey'
```

### Manually configure an API key

```python
import san
san.ApiConfig.api_key = "my_apikey"
```

### How to obtain an API key

To obtain an API key you should [log in to sanbase](https://app.santiment.net/login)
and go to the `Account` page - [https://app.santiment.net/account](https://app.santiment.net/account).
There is an `API Keys` section and a `Generate new api key` button.

## Getting the data

### Using the provided functions

The library provides the `get` and `get_many` functions that are used to fetch data.
`get` is used to fetch timeseries data for a single metric/asset pair.
`get_many` is used to fetch timeseries data for a single metric, but many assets. This is counted as 1 API call.

The first argument to the functions is the metric name.

The rest of the parameters are::

- `slug` - (for `get`) The project identificator, as seen in [the Available projects section](#available-projects)
- `slugs` - (for `get_many`) A list of projects' identificators, as seen in [the Available projects section](#available-projects)
- `selector` - Allow for more flexible selection of the target. Some metrics are
  computed on blockchain addresses, for others you can provide a list of slugs,
  labels, amount of top holders. etc.
- `from_date` - A date or datetime in ISO8601 format specifying the start of the queried period. Defaults to `datetime.utcnow() - 365 days` 
- `to_date` - A date or datetime in ISO86091 format specifying the end of the queried period. Defaults to `datetime.utcnow()`
- `interval` - The interval between the data points in the timeseries. Defaults to `'1d'`
  It is represented in two different ways:
  - a fixed range:  an integer followed by one of: `s`, `m`, `h`, `d` or `w`
  - a function, providing some semantic or a dynamic range: `toStartOfMonth`, `toStartOfDay`, `toStartOfWeek`, `toMonday`..

The returned resulut for time-series data is transformed into `pandas DataFrame` and is indexed by `datetime`.
For `get`, the value column is named `value`.
For `get_many`, there is one column per asset queried. The asset slugs are used for the column names.

For backwards compatibility, fetching the metric by providing `"metric/slug"` as
the first instead of using a separate `'slug'`/`'selector'` continues to work,
but it is not the recommended approach.

For non-metric related data like getting the list of available assets, the data
is fetched by providing a string in the format `query/argument` and additional
parameters.

The examples below contain some of described scenarios.

Fetch metric by providing `metric` as first argument and `slug` as named parameter:

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

Fetch prices for multiple assets:
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

Fetch development activity of a specific Github organization:
```python
import san
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

Fetch a metric for a contract address, not a slug:
```python
import san
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

Fetch top holders metric and specify the number of top holders to be counted:
```python
import san
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

Fetch trade volume of a given DEX for a given slug
```python
import san
# This requires Santiment API PRO apikey configured
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
Fetch metric by providing `metric/slug` as first argument and no `slug` as named parameter:
```python
import san

san.get(
    "daily_active_addresses/bitcoin",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
```
```
datetime                   value      
2018-06-01 00:00:00+00:00  692508.0
2018-06-02 00:00:00+00:00  521887.0
2018-06-03 00:00:00+00:00  531464.0
2018-06-04 00:00:00+00:00  702902.0
2018-06-05 00:00:00+00:00  655695.0
```

Fetch non-timeseries data:
```python
import san
san.get("projects/all")
```
```
                name             slug ticker   totalSupply
0             0chain           0chain    ZCN     400000000
1                 0x               0x    ZRX    1000000000
2          0xBitcoin            0xbtc  0xBTC      20999984
...
```

### Execute an arbitrary GraphQL request

Some of the available queries in the [Santiment API](https://api.santiment.net) do not have a 
dedicated sanpy function. Alternatively, if the returned format needs to be parsed differently, this approach
can be used, too. They can be fetched by providing the raw GraphQL query.

Fetching data for many slugs at the same time. Note that this is also avaialble as `san.get_many`
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

## Available metrics

Getting all of the metrics as a list is done using the following code:

```python
san.available_metrics()
```

## Available Metrics for Slug

Getting all of the metrics for a given slug is achieved with the following code:

```python
san.available_metrics_for_slug("santiment")
```
## Fetch timeseries metric

```python
import san

san.get(
    "daily_active_addresses",
    slug="santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
```

Using the defaults params (last 1 year of data with 1 day interval):

```python
san.get("daily_active_addresses", slug="santiment")
san.get("price_usd", slug="santiment")
```

## Fetching metadata for a metric

Fetching the metadata for an on-chain metric.

```python
san.metadata(
    "nvt",
    arr=["availableSlugs", "defaultAggregation", "humanReadableName", "isAccessible", "isRestricted", "restrictedFrom", "restrictedTo"]
)
```

Example result:

```python
{"availableSlugs": ["0chain", "0x", "0xbtc", "0xcert", "1sg", ...],
"defaultAggregation": "AVG", "humanReadableName": "NVT (Using Circulation)", "isAccessible": True, "isRestricted": True, "restrictedFrom": "2020-03-21T08:44:14Z", "restrictedTo": "2020-06-17T08:44:14Z"}
```

- `availableSlugs` - A list of all slugs available for this metric.
- `defaultAggregation` - If big interval are queried, all values that fall into
  this interval will be aggregated with this aggregation.
- `humanReadableName` - A name of the metric suitable for showing to users.
- `isAccessible` - `True` if the metric is accessible. If API key is configured, c
  hecks the API plan subscriptions. `False` if the metric is not accessbile. For example
  `circulation_1d` requires `PRO` plan subscription in order to be accessbile at
  all.
- `isRestricted` - `True` if time restrictions apply to the metric and your
  current plan (`Free` if no API key is configured). Check `restrictedFrom` and
  `restrictedTo`.
- `restrictedFrom` - The first datetime available of that metric for your current plan.
- `restrictedTo` - The last datetime available of that metric and your current plan.

## Batching multiple queries

Multiple queries can be executed in a batch to speed up the performance.

There are two batch classes provided - `Batch` and `AsyncBatch`.

> Note: Batching improves the performance and the developer experience, but every
> query put inside the batch is still counted as one separate API call.
> To fetch a metric for multiple assets at a time take a look at `san.get_many`
  
- `AsyncBatch` is the recomended batch class. It executes all the queries in
  separate HTTP requests. The benefit of using `AsyncBatch` over looping and
  executing every API call is that the queries can be executed concurrently. 
  Putting multiple API calls in separate HTTP calls also allows to fetch more
  data, otherwise you might run into [Complexity](https://academy.santiment.net/for-developers/#graphql-api-complexity) issues. 
  The concurrency is controlled by the `max_workers` optional parameter to the
  `execute` function. By default the `max_workers` value is 10.
  It also supports `get_many` function to fetch data for many assets.

- `Batch` combines all the provided queries in a single GraphQL document and
  executes them in a single HTTP request. This batching technique should be used
  when lightweight queries that don't fetch a lot of data are used. The reason is
  that the [complexity](https://academy.santiment.net/for-developers/#graphql-api-complexity) of each query
  is accumulated and the batch can be rejected.
  
Note: If you have been using `Batch()` and want to switch to the newer `AsyncBatch()` you only need to
change the batch initialization. The functions for adding queries and executing the batch, as well as the
format of the response, are the same.

```python
from san import Batch

batch = Batch()

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

[daa, trx_volume] = batch.execute()
```

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
batch.get_many(
    "daily_active_addresses",
    slugs=["bitcoin", "ethereum"],
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
[daa, daa_many] = batch.execute(max_workers=10)
```

## Rate Limit Tools

There are two functions, which can help you in handling the rate limits:
* ``is_rate_limit_exception`` - Returns whether the exception caught is because of rate limitation
* ``rate_limit_time_left`` - Returns the time left before the rate limit expires
* ``api_calls_made`` - Returns the API calls for each day in which it was used
* ``api_calls_remaining`` - Returns the API calls remaining for the month, hour and minute

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
    print(f"Will sleep for {rate_limit_seconds}")
    time.sleep(rate_limit_seconds)

...

calls_by_day = san.api_calls_made()
calls_remaining = san.api_calls_remaining()
```


## Metric Complexity

Fetch the complexity of a metric. The complexity depends on the from/to/interval
parameters, as well as the metric and the subscription plan. A request might
have a maximum complexity of 50000. If a request has a higher complexity there
are a few ways to solve the issue:

- Break down the request into multiple requests with smaller from-to ranges.
- Upgrade to a higher subscription plan.

More about the complexity can be found on [Santiment Academy]()
```python
san.metric_complexity(
    metric="price_usd",
    from_date="2020-01-01",
    to_date="2020-02-20",
    interval="1d"
)
```

## Include Incomplete Data Flag

Daily metrics have one value per day. For the current day, the latest computed
value will not include a full day of data. For example, computing
`daily_active_addresses` at 08:00 includes data for one third of the day. To
reduce confusion, the current day value for metrics that have this behaviour is
excluded. To force fetching the current day value, the `includeIncompleteData`
flag must be used.

```python
san.get(
  "daily_active_addresses/bitcoin",
  from_date="utc_now-3d",
  to_date="utc_now",
  interval="1d",
  include_incomplete_data=True
)
```

## Metric/Asset pair available cince

Fetch the first datetime for which a metric is available for a given slug.

```python
san.available_metric_for_slug_since(metric="daily_active_addresses", slug="santiment")
```

## Transform the result

Example usage:
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

Where the parameters, that are not mentioned, are optional:

`transform` - Apply a transformation on the data. The supported transformations are:
- "moving_average" - Replace every value V<sub>i</sub> with the average of the last "moving_average_base" values.
- "consecutive_differences" - Replace every value V<sub>i</sub> with the value V<sub>i</sub> - V<sub>i-1</sub> where i is the position in the list. Automatically fetches some extra data needed in order to compute the first value.
- "percent_change" - Replace every value V<sub>i</sub> with the percent change of V<sub>i-1</sub> and V<sub>i</sub> ( (V<sub>i</sub> / V<sub>i-1</sub> - 1) * 100) where i is the position in the list. Automatically fetches some extra data needed in order to compute the first value.

`aggregation` - the aggregation which is used for the query results.


## Available projects

Returns a DataFrame with all the projects available in the Santiment API. Not all
metrics will be available for each of the projects.

`slug` is the unique identifier of a project, used in the metrics fetching.

```python
san.get("projects/all")
```

Example result:

```csv
                 name             slug ticker   totalSupply
0              0chain           0chain    ZCN     400000000
1                  0x               0x    ZRX    1000000000
2           0xBitcoin            0xbtc  0xBTC      20999984
3     0xcert Protocol           0xcert    ZXC     500000000
4              1World           1world    1WO      37219453
5        AB-Chain RTB     ab-chain-rtb    RTB      27857813
6             Abulaba          abulaba    AAA     397000000
7                 AC3              ac3    AC3    80235326.0
...
```


## Non-standard metrics

Here is a list of metrics that are not part of the returned list of metrics found above.
This is due to having different response format and semantics.

### Other Price metrics

#### Marketcap, Price USD, Price BTC and Trading Volume

```python
san.get(
    "prices",
    slug="santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
```
#### Open, High, Close, Low Prices, Volume, Marketcap

Note: this query cannot be batched!

```python
san.get(
    "ohlcv",
    slug="santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
```

Example result:

```python
datetime                        openPriceUsd  closePriceUsd  highPriceUsd  lowPriceUsd   volume  marketcap
2018-06-01 00:00:00+00:00       1.24380        1.27668       1.26599       1.19099       852857  7.736268e+07
2018-06-02 00:00:00+00:00       1.26136        1.30779       1.27612       1.20958      1242520  7.864724e+07
2018-06-03 00:00:00+00:00       1.28270        1.28357       1.24625       1.21872      1032910  7.844339e+07
2018-06-04 00:00:00+00:00       1.23276        1.24910       1.18528       1.18010       617451  7.604326e+07
```

### Mining Pools Distribution

Returns distribution of miners between mining pools. What part of the miners are using top3, top10 and all the other pools. Currently only ETH is supported.

[Premium metric](#premium-metrics)

```python
san.get(
    "mining_pools_distribution",
    slug="ethereum",
    from_date="2019-06-01",
    to_date="2019-06-05",
    interval="1d"
)
```

Example result:

```
datetime                      other     top10      top3
2019-06-01 00:00:00+00:00  0.129237  0.249906  0.620857
2019-06-02 00:00:00+00:00  0.127432  0.251903  0.620666
2019-06-03 00:00:00+00:00  0.122058  0.249603  0.628339
2019-06-04 00:00:00+00:00  0.127726  0.254982  0.617293
2019-06-05 00:00:00+00:00  0.120436  0.265842  0.613722
```

### Historical Balance

Historical balance for erc20 token or eth address. Returns the historical balance for a given address in the given interval.

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

Example result:

```
datetime                     balance
2019-04-18 00:00:00+00:00  382338.33
2019-04-19 00:00:00+00:00  382338.33
2019-04-20 00:00:00+00:00  382338.33
2019-04-21 00:00:00+00:00  215664.33
2019-04-22 00:00:00+00:00  215664.33
```

### Ethereum Top Transactions

Top ETH transactions for project's team wallets.

Available transaction types:

- ALL
- IN
- OUT

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

Example result:

**The result is shortened for convenience**

```
datetime                           fromAddress  fromAddressInExchange           toAddress  toAddressInExchange              trxHash      trxValue
2019-04-29 21:33:31+00:00  0xe76fe52a251c8f...                  False  0x45d6275d9496b...                False  0x776cd57382456a...        100.00
2019-04-29 21:21:18+00:00  0xe76fe52a251c8f...                  False  0x468bdccdc334f...                False  0x848414fb5c382f...         40.95
2019-04-19 14:14:52+00:00  0x1f3df0b8390bb8...                  False  0xd69bc0585e05e...                False  0x590512e1f1fbcf...         19.48
2019-04-19 14:09:58+00:00  0x1f3df0b8390bb8...                  False  0x723fb5c14eaff...                False  0x78e0720b9e72d1...         15.15
```

### Ethereum Spent Over Time

ETH spent for each interval from the project's team wallet and time period

```python
san.get(
    "eth_spent_over_time",
    slug="santiment",
    from_date="2019-04-18",
    to_date="2019-04-23",
    interval="1d"
)
```

Example result:

```
datetime                    ethSpent
2019-04-18 00:00:00+00:00   0.000000
2019-04-19 00:00:00+00:00  34.630284
2019-04-20 00:00:00+00:00   0.000000
2019-04-21 00:00:00+00:00   0.000158
2019-04-22 00:00:00+00:00   0.000000
```

### Token Top Transactions

Top transactions for the token of a given project

```python
san.get(
    "token_top_transactions",
    slug="santiment",
    from_date="2019-04-18",
    to_date="2019-04-30",
    limit=5
)
```

Example result:

**The result is shortened for convenience**

```
datetime                           fromAddress  fromAddressInExchange           toAddress  toAddressInExchange              trxHash      trxValue
2019-04-21 13:51:59+00:00  0x1f3df0b8390bb8...                  False  0x5eaae5e949952...                False  0xdbced935b09dd0...  166674.00000
2019-04-28 07:43:38+00:00  0x0a920bfdf7f977...                  False  0x868074aab18ea...                False  0x5f2214d34bcdc3...   33181.82279
2019-04-28 07:53:32+00:00  0x868074aab18ea3...                  False  0x876eabf441b2e...                 True  0x90bd286da38a2b...   33181.82279
2019-04-26 14:38:45+00:00  0x876eabf441b2ee...                   True  0x76af586d041d6...                False  0xe45b86f415e930...   28999.64023
2019-04-30 15:17:28+00:00  0x876eabf441b2ee...                   True  0x1f4a90043cf2d...                False  0xc85892b9ef8c64...   20544.42975
```

### Top Transfers

Top transfers for the token of a given project, ``address`` and ``transaction_type`` arguments can be added as well, in the form of a key-value pair. The ``transaction_type`` parameter can have one of these three values: ``ALL``, ``OUT``, ``IN``.

```python
san.get(
    "top_transfers",
    slug="santiment",
    from_date="utc_now-30d",
    to_date="utc_now",
)
```

**The result is shortened for convenience**

Example result:
```
                          fromAddress   toAddress     trxHash       trxValue
datetime                                                                                                                                                                                                                          
2021-06-17 00:16:26+00:00  0xa48df...  0x876ea...  0x62a56...  136114.069733
2021-06-17 00:10:05+00:00  0xbd3c2...  0x876ea...  0x732a5...  117339.779890
2021-06-19 21:36:03+00:00  0x59646...  0x0d45b...  0x5de31...  112336.882707
...
```

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

Example result:
```
                          fromAddress  toAddress    trxHash   trxValue
datetime                                                                                                                                                                                        
2021-06-13 09:14:01+00:00  0x26e06...  0xfd3d...  0x4af6...  69854.528
2021-06-13 09:13:01+00:00  0x876ea...  0x26e0...  0x18c1...  69854.528
2021-06-14 08:54:52+00:00  0x876ea...  0x26e0...  0xdceb...  59920.591
...
```

### Emerging Trends

Emerging trends for a given period of time. 

```python
san.get(
    "emerging_trends",
    from_date="2019-07-01",
    to_date="2019-07-02",
    interval="1d",
    size=5
)
```

Example result:

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

### Top Social Gainers Losers

Top social gainers/losers returns the social volume changes for crypto projects.

```python
san.get(
    "top_social_gainers_losers",
    from_date="2019-07-18",
    to_date="2019-07-30",
    size=5,
    time_window="2d",
    status="ALL"
)
```

Example result:

**The result is shortened for convenience**

```
datetime                              slug     change    status
2019-07-28 01:00:00+00:00     libra-credit  21.000000    GAINER
2019-07-28 01:00:00+00:00             aeon  -1.000000     LOSER
2019-07-28 01:00:00+00:00    thunder-token   5.000000  NEWCOMER
2019-07-28 02:00:00+00:00     libra-credit  43.000000    GAINER
...                                    ...        ...       ...
2019-07-30 07:00:00+00:00            storj  12.000000  NEWCOMER
2019-07-30 11:00:00+00:00            storj  21.000000    GAINER
2019-07-30 11:00:00+00:00            aergo  -1.000000     LOSER
2019-07-30 11:00:00+00:00            litex   8.000000  NEWCOMER
```

## Extras

Take a look at the [examples](/examples/extras) folder.

## Development

It is recommended to use [pipenv](https://github.com/pypa/pipenv) for managing your local environment.

Setup project:

```bash
pipenv install
```

Install main dependencies:

```bash
pipenv run pip install -e .
```

Install extra dependencies:

```bash
pipenv run pip install -e '.[extras]'
```

## Running tests

```bash
python setup.py test
```

## Running integration tests

```bash
python setup.py nosetests -a integration
```
