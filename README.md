# Santiment API python client

## Installation

```console
pip install sanpy
```

## Configuration

Optionally you can provide an api key which gives access to some restricted metrics:

```python
import san
san.ApiConfig.api_key = 'api-key-provided-by-sanbase'
```

To obtain an api key you should [log in to sanbase](https://sanbase-low.santiment.net/login) and go to the `account` page - [https://sanbase-low.santiment.net/account](https://sanbase-low.santiment.net/account). There is an `API Keys` section and a `Generate new api key` button.

If the account used for generating the api key has enough SAN tokens, the api key will give you access to the data that requires SAN token staking. The api key can only be used to fetch data and not to execute graphql mutations.

## Retrieving data from the API

The data is fetched by providing a string in the format `query/slug` and additional parameters.

* `query`: Available queries can be found in section: [Available metrics](#available-metrics)
* `slug`: A list of projects with their slugs, names, etc. can be fetched like this:

```python
import san
san.get("projects/all")
```

```console
               name                      slug ticker
0                0x                        0x    ZRX
1            Achain                    achain    ACT
2              AdEx                   adx-net    ADX
...
```

Parameters:

* `from_date`, `to_date` - A date or datetime in iso8601 format specifying the start and end datetime for the returned data for ex: `2018-06-01`
* `interval` - The interval of the returned data - an integer followed by one of: `s`, `m`, `h`, `d` or `w`

Default values for parameters:

* `from_date`: `datetime.now() - 365 days`
* `to_date`: `datetime.now()`
* `interval`: `'1d'`

The returned value for time-series data is in `pandas DataFrame` format indexed by `datetime`.

### Fetch single metric

```python
import san

daa = san.get(
    "daily_active_addresses/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

prices = san.get(
    "prices/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

```

Using the defaults params:

```python

daa = san.get("daily_active_addresses/santiment")
prices = san.get("prices/santiment")

```

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
    "daily_active_addresses/santiment",
    from_date="2018-06-06",
    to_date="2018-06-10",
    interval="1d"
)
[daa1, daa2] = batch.execute()

```

## Available metrics

Below are described some available metrics and are given examples for fetching and for the returned format.

### Daily Active Addresses

This metric includes the number of unique addresses that participated in the transfers of given token during the day.

```python

daa = san.get(
    "daily_active_addresses/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

```

Example result:

```console
                           activeAddresses
datetime
2018-06-01 00:00:00+00:00                2
2018-06-02 00:00:00+00:00                4
2018-06-03 00:00:00+00:00                6
2018-06-04 00:00:00+00:00                6
2018-06-05 00:00:00+00:00               14
```

### Token aging (burn rate)

Each transaction has an equivalent burn rate record. The burn rate is calculated by multiplying the number of tokens moved by the number of blocks in which they appeared. Spikes in burn rate could indicate large transactions or movement of tokens that have been held for a long time.

```python

burn_rate = san.get(
    "burn_rate/santiment",
    from_date="2018-05-01",
    to_date="2018-05-02",
    interval="1h"
)

```

Example result:

```console
                               burnRate
datetime
2018-05-01 11:00:00+00:00  3.009476e+06
2018-05-01 14:00:00+00:00  2.161845e+09
2018-05-01 17:00:00+00:00  7.263414e+05
2018-05-01 19:00:00+00:00  7.424445e+07
2018-05-01 21:00:00+00:00  6.987085e+07
2018-05-01 22:00:00+00:00  2.052304e+08
```

### Transaction volume

Total amount of tokens for a project that were transacted on the blockchain. This metric includes only on-chain volume, not volume in exchanges.

```python

tv = san.get(
    "transaction_volume/santiment",
    from_date="2018-05-01",
    to_date="2018-05-02",
    interval="1h"
)

```

Example result:

```console
                           transactionVolume
datetime
2018-05-01 11:00:00+00:00         298.707310
2018-05-01 14:00:00+00:00       19356.439888
2018-05-01 17:00:00+00:00        1088.967586
2018-05-01 19:00:00+00:00          99.600000
2018-05-01 21:00:00+00:00        6177.411536
2018-05-01 22:00:00+00:00       41397.348795
2018-05-01 23:00:00+00:00         300.000000
```

### Github Activity

Returns a list of github activity for a given slug and time interval.

[An article explaining the github activity tracking](https://medium.com/santiment/tracking-github-activity-of-crypto-projects-introducing-a-better-approach-9fb1af3f1c32)

```python
ga = san.get(
    "github_activity/santiment",
    from_date="2018-05-01",
    to_date="2018-05-05",
    interval="24h"
)

```

Example result:

```console
                           activity
datetime
2018-05-02 00:00:00+00:00        32
2018-05-03 00:00:00+00:00         9
2018-05-04 00:00:00+00:00        18
```

### Prices

Fetch price history for a given slug in USD or BTC.

```python

prices = san.get(
    "prices/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

prices = san.get(
    "prices/ethereum",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

```

Example result:

```console

                                         priceBtc            priceUsd
datetime
2018-06-01 00:00:00+00:00   0.0001649780416666666   1.234634930555555
2018-06-02 00:00:00+00:00  0.00016521851041666669  1.2551352777777771
2018-06-03 00:00:00+00:00    0.000162902558303887   1.251881943462897
2018-06-04 00:00:00+00:00   0.0001600935277777778  1.2135782638888888


                                      priceBtc           priceUsd
datetime
2018-06-01 00:00:00+00:00  0.07708937311827956   576.862577060932
2018-06-02 00:00:00+00:00   0.0774746559139785  588.6194336917561
2018-06-03 00:00:00+00:00  0.07944145999999996  610.5163418181814
2018-06-04 00:00:00+00:00  0.07947329054545459  602.5116327272724

```

### Exchange funds flow

Fetch the difference between the tokens that were deposited minus the tokens that were withdrawn from an exchange for a given slug in the selected time period.

```python

exchange_funds_flow = san.get(
    "exchange_funds_flow/santiment",
    from_date="2018-04-16T10:02:19Z",
    to_date="2018-05-23T10:02:19Z"
)

```

Example result:

```console

                              fundsFlow
datetime
2018-04-16 10:02:19+00:00      0.000000
2018-04-16 10:17:18+00:00      0.000000
2018-04-16 12:03:51+00:00      0.000000
2018-04-16 13:50:24+00:00   -208.797310

```

### ERC20 Exchange Funds Flow

Fetch the exchange funds flow for all ERC20 projects in the given interval.

Arguments description:

* from_date - a string representation of datetime value according to the iso8601 standard, e.g. "2018-04-16T10:02:19Z"
* to_date - a string representation of datetime value according to the iso8601 standard, e.g. "2018-05-23T10:02:19Z"

Fields description:

* ticker - The ticker of the project
* contract - The contract identifier of the project
* exchangeIn - How many tokens were deposited in the given period
* exchangeOut - How many tokens were withdrawn in the given period
* exchangeDiff - The difference between the deposited and the withdrawn tokens: exchangeIn - exchangeOut
* exchangeInUsd - How many tokens were deposited in the given period converted to USD based on the daily average price of the token
* exchangeOutUsd - How many tokens were withdrawn in the given period converted to USD based on the daily average price of the token
* exchangeDiffUsd - The difference between the deposited and the withdrawn tokens in USD: exchangeInUsd - exchangeOutUsd
* percentDiffExchangeDiffUsd - The percent difference between exchangeDiffUsd for the current period minus the exchangeDiffUsd for the previous period based on exchangeDiffUsd for the current period: (exchangeDiffUsd for current period - exchangeDiffUsd for previous period) * 100 / abs(exchangeDiffUsd for current period)
* exchangeVolumeUsd - The volume of all tokens in and out for the given period in USD: exchangeInUsd + exchangeOutUsd
* percentDiffExchangeVolumeUsd - The percent difference between exchangeVolumeUsd for the current period minus the exchangeVolumeUsd for the previous period based on exchangeVolumeUsd for the current period: (exchangeVolumeUsd for current period - exchangeVolumeUsd for previous period) * 100 / abs(exchangeVolumeUsd for current period)
* exchangeInBtc - How many tokens were deposited in the given period converted to BTC based on the daily average price of the token
* exchangeOutBtc - How many tokens were withdrawn in the given period converted to BTC based on the daily average price of the token
* exchangeDiffBtc - The difference between the deposited and the withdrawn tokens in BTC: exchangeInBtc - exchangeOutBtc
* percentDiffExchangeDiffBtc - The percent difference between exchangeDiffBtc for the current period minus the exchangeDiffBtc for the previous period based on exchangeDiffBtc for the current period: (exchangeDiffBtc for current period - exchangeDiffBtc for previous period) * 100 / abs(exchangeDiffBtc for current period)
* exchangeVolumeBtc - The volume of all tokens in and out for the given period in BTC: exchangeInBtc + exchangeOutBtc
* percentDiffExchangeVolumeBtc - The percent difference between exchangeVolumeBtc for the current period minus the exchangeVolumeBtc for the previous period based on exchangeVolumeBtc for the current period: (exchangeVolumeBtc for current period - exchangeVolumeBtc for previous period) * 100 / abs(exchangeVolumeBtc for current period)

```python

erc20_exchange_funds_flow = san.get(
    "erc20_exchange_funds_flow",
    from_date="2018-04-16T10:02:19Z",
    to_date="2018-05-23T10:02:19Z"
)

```

Example result:

```console

                                     contract  exchangeDiff  exchangeDiffBtc  \
0   0x006bea43baa3f7a6f765f14f10a1a1b08334ef45 -5.353089e+03        -0.691860
1   0x0371a82e4a9d0a4312f3ee2ac9c6958512891372 -1.993464e+04        -0.050134
2   0x08711d3b02c8758f2fb3ab4e80228418a7f8e39c  2.712031e+06       209.894542
3   0x089a6d83282fb8988a656189f1e7a73fa6c1cac2  1.214960e+04         0.000000
4   0x08f5a9235b08173b7569f83645d2c7fb55e8ccd8 -9.398656e+05        -1.687275

    exchangeDiffUsd    exchangeIn  exchangeInBtc  exchangeInUsd   exchangeOut  \
0     -7.017060e+03  4.213794e+04       2.226106   1.999951e+04  4.749103e+04
1     -4.372710e+02  3.120267e+04       0.078270   7.055826e+02  5.113730e+04
2      1.897489e+06  5.308479e+06     397.788044   3.584974e+06  2.596448e+06
3      0.000000e+00  6.740607e+04       0.000000   0.000000e+00  5.525647e+04
4     -2.628859e+03  3.067355e+07     412.468640   3.711345e+06  3.161342e+07

    exchangeOutBtc  exchangeOutUsd  exchangeVolumeBtc  exchangeVolumeUsd  \
0         2.917965    2.701657e+04           5.144071       4.701608e+04
1         0.128404    1.142854e+03           0.206674       1.848436e+03
2       187.893502    1.687485e+06         585.681547       5.272459e+06
3         0.000000    0.000000e+00           0.000000       0.000000e+00
4       414.155914    3.713974e+06         826.624554       7.425320e+06

    percentDiffExchangeDiffBtc  percentDiffExchangeDiffUsd  \
0                   -37.732414                  -53.544924
1                 -1017.120786                -1082.665604
2                    14.589978                   31.029558
3                          NaN                         NaN
4                 -2890.486742               -15372.926874

    percentDiffExchangeVolumeBtc  percentDiffExchangeVolumeUsd ticker
0                      -6.591777                      8.992750    STX
1                    -718.046381                   -670.219511    STU
2                      10.075328                     22.742302    EDG
3                            NaN                           NaN    PGL
4                      41.544110                     48.203277    TNT

```

### Social Volume Projects

Fetch a list of slugs for which there is social volume data.

```python

projects = san.get("social_volume_projects")

```

Example result:

```console

                   0
0            cardano
1       bitcoin-cash
2            bitcoin
3        dragonchain
4                eos
5   ethereum-classic
6           ethereum
7      kyber-network
8           litecoin
9               iota
10          ontology
11              tron
12          wanchain
13           stellar
14            ripple
15             verge
16                0x

```

### Social Volume

Fetch a list of mentions count for a given project and time interval.

Arguments description:

* endpoint - social_volume/project_slug
* interval - an integer followed by one of: `m`, `h`, `d`, `w`
* from_date - a string representation of datetime value according to the iso8601 standard, e.g. "2018-04-16T10:02:19Z"
* to_date - a string representation of datetime value according to the iso8601 standard, e.g. "2018-05-23T10:02:19Z"
* social_volume_type - one of the following:
    1. PROFESSIONAL_TRADERS_CHAT_OVERVIEW
    2. TELEGRAM_CHATS_OVERVIEW
    3. TELEGRAM_DISCUSSION_OVERVIEW

    It is used to select the source of the mentions count.

```python

social_volume = san.get(
    "social_volume/dragonchain",
    interval="1d",
    from_date="2018-04-16T10:02:19Z",
    to_date="2018-05-23T10:02:19Z",
    social_volume_type="PROFESSIONAL_TRADERS_CHAT_OVERVIEW"
)

```

Example result:

```console

                           mentionsCount
datetime
2018-04-17 00:00:00+00:00              4
2018-04-18 00:00:00+00:00              8
2018-04-19 00:00:00+00:00              7
2018-04-20 00:00:00+00:00              1
2018-04-21 00:00:00+00:00              3
2018-04-22 00:00:00+00:00              2
2018-04-23 00:00:00+00:00              1

```