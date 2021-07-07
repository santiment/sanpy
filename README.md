# sanpy

[![PyPI version](https://badge.fury.io/py/sanpy.svg)](https://badge.fury.io/py/sanpy)

Santiment API python client.

## Table of contents

- [Table of contents](#table-of-contents)
  - [Installation](#installation)
  - [Upgrade to latest version](#upgrade-to-latest-version)
  - [Configuration](#configuration)
  - [Retrieving data from the API](#retrieving-data-from-the-api)
    - [Fetch single metric](#fetch-single-metric)
    - [Batching multiple queries](#batching-multiple-queries)
    - [Making a custom graphql query to the API](#making-a-custom-graphql-query-to-the-api)
    - [Rate Limit Tools](#rate-limit-tools)
  - [Available metrics](#available-metrics)
    - [Available Metric for Slug](#available-metrics-for-slug)
    - [Metric Complexity](#metric-complexity)
    - [Available Since](#available-since)
    - [Full list of on-chain metrics (including timebounded)](#full-list-of-on-chain-metrics-including-timebounded)
    - [All Projects](#all-projects)
    - [ERC20 Projects](#erc20-projects)
    - [Open, High, Close, Low Prices, Volume, Marketcap](#open-high-close-low-prices-volume-marketcap)
    - [Gas Used](#gas-used)
    - [Miners Balance](#miners-balance)
    - [Mining Pools Distribution](#mining-pools-distribution)
    - [Historical Balance](#historical-balance)
    - [Top Holders Percent of Total Supply](#top-holders-percent-of-total-supply)
    - [Price Volume Difference](#price-volume-difference)
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

```bash
pip install sanpy
```

## Upgrade to latest version

```bash
pip install --upgrade sanpy
```

## Install extra packages

There are few scripts under [extras](/san/extras) directory. To install their dependencies use:

```bash
pip install sanpy[extras]
```

## Restricted metrics

In order to access real-time data or historical data for some of the metrics,
you'll need to set the [API key](#configuration), generated from an account with
a paid API plan.

All restricted metrics are free for "santiment" token.

## Configuration

Optionally you can provide an api key which gives access to some restricted metrics:

```python
import san
san.ApiConfig.api_key = 'api-key-provided-by-sanbase'
```

To obtain an api key you should [log in to sanbase](https://app.santiment.net/login)
and go to the `account` page - [https://app.santiment.net/account](https://app.santiment.net/account).
There is an `API Keys` section and a `Generate new api key` button.

If the account used for generating the api key has enough SAN tokens, the api key will give you
access to the data that requires SAN token staking. The api key can only be used to fetch data and not to execute graphql mutations.

## Retrieving data from the API

The data is fetched by providing a string in the format `query/slug` and additional parameters.

- `query`: Available queries can be found in section: [Available metrics](#available-metrics)
- `slug`: A list of projects with their slugs, names, etc. can be fetched like this:

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

Parameters:

- `from_date`, `to_date` - A date or datetime in iso8601 format specifying the start and end datetime for the returned data or the string for ex: `2018-06-01`, or a string, representing the relative datetime `utc_now-<interval>`
- `interval` - The interval of the returned data - an integer followed by one of: `s`, `m`, `h`, `d` or `w`

Default values for parameters:

- `from_date`: `datetime.now() - 365 days`
- `to_date`: `datetime.now()`
- `interval`: `'1d'`

The returned value for time-series data is in `pandas DataFrame` format indexed by `datetime`.

### Fetch single metric

```python
import san

san.get(
    "daily_active_addresses/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

san.get(
    "prices/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
```

Using the defaults params (last 1 year of data with 1 day interval):

```python
san.get("daily_active_addresses/santiment")
san.get("prices/santiment")
```

### Fetching metadata for a metric

Fetching the metadata for an on-chain metric.

```python
san.metadata(
    "nvt",
    arr=['availableSlugs', 'defaultAggregation', 'humanReadableName', 'isAccessible', 'isRestricted', 'restrictedFrom', 'restrictedTo']
)
```

Example result:

```python
{'availableSlugs': ['0chain', '0x', '0xbtc', '0xcert', '1sg', ...],
'defaultAggregation': 'AVG', 'humanReadableName': 'NVT (Using Circulation)', 'isAccessible': True, 'isRestricted': True, 'restrictedFrom': '2020-03-21T08:44:14Z', 'restrictedTo': '2020-06-17T08:44:14Z'}
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

### Batching multiple queries

```python
from san import Batch

batch = Batch()

batch.get(
    "daily_active_addresses/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

batch.get(
    "transaction_volume/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

[daa, trx_volume] = batch.execute()
```

### Making a custom graphql query to the API

```python
from san.graphql import execute_gql
import pandas as pd

res = execute_gql("""{
  projectBySlug(slug: "santiment") {
    slug
    name
    ticker
    infrastructure
    mainContractAddress
    twitterLink
  }
}""")

pd.DataFrame(res['projectBySlug'], index=[0])
```

```
  infrastructure                         mainContractAddress       name       slug ticker                        twitterLink
0            ETH  0x7c5a0ce9267ed19b22f8cae653f198e3e8daf098  Santiment  santiment    SAN  https://twitter.com/santimentfeed
```

### Rate Limit Tools

There are two functions, which can help you in handling the rate limits:
* ``is_rate_limit_exception`` - Returns whether the exception caught is because of rate limitation
* ``rate_limit_time_left`` - Returns the time left before the rate limit expires

Example:
```python
import time
import san

try:
  san.get(
    "price_usd/santiment",
    from_date="utc_now-30d",
    to_date="utc_now",
    interval="1d"
  )
except Exception as e:
  if san.is_rate_limit_exception(e):
    rate_limit_seconds = san.rate_limit_time_left(e)
    print(f"Will sleep for {rate_limit_seconds}")
    time.sleep(rate_limit_seconds)
```

## Available metrics

Getting all of the metrics as a list is done using the following code:

```python
san.available_metrics()
```

## Available Metrics for Slug

Getting all of the metrics for a given slug is achieved with the following code:

```python
san.available_metrics_for_slug('santiment')
```

## Metric Complexity

Fetch the complexity of a metric. The complexity depends on the from/to/interval parameters, as well as the metric and the subscription plan. A request might have a maximum complexity of 20000. If a request has a higher complexity there are a few ways to solve the issue:

- Break down the request into multiple requests with smaller from-to ranges.
- Upgrade to a higher subscription plan.

```python
san.metric_complexity(
    metric='price_usd',
    from_date='2020-01-01',
    to_date='2020-02-20',
    interval='1d'
)
```

## Available Since

Fetch the first datetime for which a metric is available for a given slug.

```python
san.available_metric_for_slug_since(metric='daily_active_addresses', slug='santiment')
```


Below are described the available metrics and are given examples for fetching them.

### Full list of metrics for a single project

> NOTE: When a new metric is added to the API, `san.available_metrics()` will
> automatically pick it up and it will be accessible with sanpy, but it might
> take some time to be added to this documentation. The list below might not be
> full at times.

The suffixes `_<number>y` and `_<number>d` means that the metric is calculated
only by taken into account the tokens and coins that have moved in the past
number of years or days.

All these metrics are returned as a Pandas dataframe with two columns - `datetime`
and float `value`.

All metrics that do not follow the same format are explicitly listed after that.

#### Holder Metrics

- amount_in_top_holders
- amount_in_exchange_top_holders
- amount_in_non_exchange_top_holders
- holders_distribution_combined_balance_100k_to_1M
- holders_distribution_0.1_to_1
- holders_distribution_0_to_0.001
- holders_distribution_1_to_10
- holders_distribution_1k_to_10k
- holders_distribution_combined_balance_0.01_to_0.1
- holders_distribution_combined_balance_0.1_to_1
- holders_distribution_combined_balance_1k_to_10k
- holders_distribution_100_to_1k
- holders_distribution_combined_balance_10k_to_100k
- holders_distribution_10_to_100
- holders_distribution_10k_to_100k
- holders_distribution_total
- holders_distribution_combined_balance_1M_to_10M
- holders_distribution_combined_balance_10_to_100
- holders_distribution_1M_to_10M
- holders_distribution_0.01_to_0.1
- holders_distribution_0.001_to_0.01
- holders_distribution_combined_balance_1_to_10
- holders_distribution_combined_balance_100_to_1k
- holders_distribution_combined_balance_0_to_0.001
- holders_distribution_combined_balance_0.001_to_0.01
- holders_distribution_combined_balance_10M_to_inf
- holders_distribution_100k_to_1M
- holders_distribution_10M_to_inf
- percent_of_total_supply_on_exchanges
- supply_on_exchanges
- supply_outside_exchanges

#### Social Metrics

- twitter_followers
- social_dominance_telegram
- social_dominance_discord
- social_dominance_reddit
- social_dominance_professional_traders_chat
- social_dominance_total
- social_volume_telegram
- social_volume_discord
- social_volume_reddit
- social_volume_professional_traders_chat
- social_volume_twitter
- social_volume_bitcointalk
- social_volume_total
- community_messages_count_telegram
- community_messages_count_total
- sentiment_positive_total
- sentiment_positive_telegram
- sentiment_positive_professional_traders_chat
- sentiment_positive_reddit
- sentiment_positive_discord
- sentiment_positive_twitter
- sentiment_positive_bitcointalk
- sentiment_negative_total
- sentiment_negative_telegram
- sentiment_negative_professional_traders_chat
- sentiment_negative_reddit
- sentiment_negative_discord
- sentiment_negative_twitter
- sentiment_negative_bitcointalk
- sentiment_balance_total
- sentiment_balance_telegram
- sentiment_balance_professional_traders_chat
- sentiment_balance_reddit
- sentiment_balance_discord
- sentiment_balance_twitter
- sentiment_balance_bitcointalk
- sentiment_volume_consumed_total
- sentiment_volume_consumed_telegram
- sentiment_volume_consumed_professional_traders_chat
- sentiment_volume_consumed_reddit
- sentiment_volume_consumed_discord
- sentiment_volume_consumed_twitter
- sentiment_volume_consumed_bitcointalk

#### Price Metrics

- price_usd
- price_btc
- price_eth
- volume_usd
- marketcap_usd
- daily_avg_marketcap_usd
- daily_avg_price_usd
- daily_closing_marketcap_usd
- daily_closing_price_usd
- daily_high_price_usd
- daily_low_price_usd
- daily_opening_price_usd
- daily_trading_volume_usd
- volume_usd_change_1d
- volume_usd_change_30d
- volume_usd_change_7d
- price_usd_change_1d
- price_usd_change_30d
- price_usd_change_7d

#### Development Metrics

- dev_activity
- dev_activity_change_30d
- dev_activity_contributors_count
- github_activity
- github_activity_contributors_count

#### Derivatives

- bitmex_perpetual_basis
- bitmex_perpetual_funding_rate
- bitmex_perpetual_open_interest
- bitmex_perpetual_open_value

#### MakerDAO Metrics

- dai_created
- dai_repaid
- mcd_collat_ratio
- mcd_collat_ratio_sai
- mcd_collat_ratio_weth
- mcd_dsr
- mcd_erc20_supply
- mcd_locked_token
- mcd_stability_fee
- mcd_supply
- scd_collat_ratio
- scd_locked_token

#### On-Chain Metrics

- active_addresses_24h
- active_addresses_24h_change_1d
- active_addresses_24h_change_30d
- active_addresses_24h_change_7d
- active_deposits
- active_withdrawals
- age_destroyed
- circulation
- circulation_10y
- circulation_180d
- circulation_1d
- circulation_2y
- circulation_30d
- circulation_365d
- circulation_3y
- circulation_5y
- circulation_60d
- circulation_7d
- circulation_90d
- daily_active_addresses
- deposit_transactions
- exchange_balance
- exchange_inflow
- exchange_outflow
- mean_age
- mean_dollar_invested_age
- mean_realized_price_usd
- mean_realized_price_usd_10y
- mean_realized_price_usd_180d
- mean_realized_price_usd_1d
- mean_realized_price_usd_2y
- mean_realized_price_usd_30d
- mean_realized_price_usd_365d
- mean_realized_price_usd_3y
- mean_realized_price_usd_5y
- mean_realized_price_usd_60d
- mean_realized_price_usd_7d
- mean_realized_price_usd_90d
- mvrv_long_short_diff_usd
- mvrv_usd
- mvrv_usd_10y
- mvrv_usd_180d
- mvrv_usd_1d
- mvrv_usd_2y
- mvrv_usd_30d
- mvrv_usd_365d
- mvrv_usd_3y
- mvrv_usd_5y
- mvrv_usd_60d
- mvrv_usd_7d
- mvrv_usd_90d
- mvrv_usd_intraday
- mvrv_usd_intraday_10y
- mvrv_usd_intraday_180d
- mvrv_usd_intraday_1d
- mvrv_usd_intraday_2y
- mvrv_usd_intraday_30d
- mvrv_usd_intraday_365d
- mvrv_usd_intraday_3y
- mvrv_usd_intraday_5y
- mvrv_usd_intraday_60d
- mvrv_usd_intraday_7d
- mvrv_usd_intraday_90d
- network_growth
- nvt
- nvt_transaction_volume
- realized_value_usd
- realized_value_usd_10y
- realized_value_usd_180d
- realized_value_usd_1d
- realized_value_usd_2y
- realized_value_usd_30d
- realized_value_usd_365d
- realized_value_usd_3y
- realized_value_usd_5y
- realized_value_usd_60d
- realized_value_usd_7d
- realized_value_usd_90d
- stock_to_flow
- transaction_volume
- velocity
- withdrawal_transactions

### Fetching lists of projects

#### All Projects

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

#### ERC20 Projects

Returns a DataFrame with all the ERC20 projects available in the Santiment API.
Not all metrics will be available for all the projects. The `slug` is a unique
identifier which can be used to retrieve most of the metrics.

```python
san.get("projects/erc20")
```

Example result:

```
                      name                   slug ticker   totalSupply
0                   0chain                 0chain    ZCN     400000000
1                       0x                     0x    ZRX    1000000000
2                0xBitcoin                  0xbtc  0xBTC      20999984
3          0xcert Protocol                 0xcert    ZXC     500000000
4                   1World                 1world    1WO      37219453
5             AB-Chain RTB           ab-chain-rtb    RTB      27857813
6                  Abulaba                abulaba    AAA     397000000
7                   adbank                 adbank    ADB    1000000000
...
```

### Other Price metrics

#### Open, High, Close, Low Prices, Volume, Marketcap

Note: this query cannot be batched!

```python
san.get(
    "ohlcv/santiment",
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

### Gas Used

Returns used Gas by a blockchain. When you send tokens, interact with a contract or
do anything else on the blockchain, you must pay for that computation.
That payment is calculated in Gas. Currently only ETH is supported.

[Premium metric](#premium-metrics)

```python
san.get(
    "gas_used/ethereum",
    from_date="2019-06-01",
    to_date="2019-06-05",
    interval="1d"
)
```

Example result:

```
datetime                       gasUsed
2019-06-01 00:00:00+00:00  47405557702
2019-06-02 00:00:00+00:00  44769162038
2019-06-03 00:00:00+00:00  46415901420
2019-06-04 00:00:00+00:00  46907686393
2019-06-05 00:00:00+00:00  45925073341
```

### Miners Balance

Returns miner balances over time. Currently only ETH is supported.

[Premium metric](#premium-metrics)

```python
san.get(
    "miners_balance/ethereum",
    from_date="2019-06-01",
    to_date="2019-06-05",
    interval="1d"
)
```

Example result:

```
datetime                        balance
2019-06-01 00:00:00+00:00  1.529488e+06
2019-06-02 00:00:00+00:00  1.533494e+06
2019-06-03 00:00:00+00:00  1.527438e+06
2019-06-04 00:00:00+00:00  1.525666e+06
2019-06-05 00:00:00+00:00  1.527563e+06
```

### Mining Pools Distribution

Returns distribution of miners between mining pools. What part of the miners are using top3, top10 and all the other pools. Currently only ETH is supported.

[Premium metric](#premium-metrics)

```python
san.get(
    "mining_pools_distribution/ethereum",
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
    "historical_balance/santiment",
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

### Price Volume Difference

Fetch the price-volume difference technical indicator for a given slug, display currency and time period. This indicator measures the difference in trend between price and volume, specifically when price goes up as volume goes down.

```python
san.get(
    "price_volume_difference/santiment",
    from_date="2019-04-18",
    to_date="2019-04-23",
    interval="1d",
    currency="USD"
)
```

Example result:

```
datetime                   priceChange  priceVolumeDiff  volumeChange
2019-04-18 00:00:00+00:00     0.017779         0.013606 -39908.007476
2019-04-19 00:00:00+00:00     0.012587         0.007332 -31195.568878
2019-04-20 00:00:00+00:00     0.009062         0.004169 -24550.100411
2019-04-21 00:00:00+00:00     0.002573         0.001035 -19307.845911
2019-04-22 00:00:00+00:00     0.001527         0.000703 -20317.934666
```

### Ethereum Top Transactions

Top ETH transactions for project's team wallets.

Available transaction types:

- ALL
- IN
- OUT

```python
san.get(
    "eth_top_transactions/santiment",
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
    "eth_spent_over_time/santiment",
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
    "token_top_transactions/santiment",
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
    "top_transfers/santiment",
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
    "top_transfers/santiment",
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

Emerging trends for a given period of time

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
