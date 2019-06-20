# Santiment API python client

## Table of contents

- [Table of contents](#table-of-contents)
  - [Installation](#installation)
  - [Upgrade to latest version](#upgrade-to-latest-version)
  - [Configuration](#configuration)
  - [Retrieving data from the API](#retrieving-data-from-the-api)
    - [Fetch single metric](#fetch-single-metric)
    - [Batching multiple queries](#batching-multiple-queries)
  - [Available metrics](#available-metrics)
    - [All Projects](#all-projects)
    - [ERC20 Projects](#erc20-projects)
    - [Daily Active Addresses](#daily-active-addresses)
    - [Network Growth](#network-growth)
    - [Burn Rate - deprecated, replaced by 'Token Age Consumed'](#burn-rate---deprecated-replaced-by-token-age-consumed)
    - [Token Age Consumed](#token-age-consumed)
    - [Average Token Age Consumed in Days](#average-token-age-consumed-in-days)
    - [Transaction volume](#transaction-volume)
    - [Token Velocity](#token-velocity)
    - [Token Circulation](#token-circulation)
    - [Realized Value](#realized-value)
    - [MVRV Ratio](#mvrv-ratio)
    - [NVT Ratio](#nvt-ratio)
    - [Daily Active Deposits](#daily-active-deposits)
    - [Github Activity](#github-activity)
    - [Prices](#prices)
    - [Open, High, Close, Low Prices, Volume, Marketcap](#open-high-close-low-prices-volume-marketcap)
    - [Exchange Funds Flow](#exchange-funds-flow)
    - [Social Volume Projects](#social-volume-projects)
    - [Social Volume](#social-volume)
    - [Share of Deposits](#share-of-deposits)
  - [Running tests](#running-tests)
  - [Running integration tests](#running-integration-tests)
    
## Installation

```
pip install sanpy
```

## Upgrade to latest version

```
pip install --upgrade sanpy
```

## Premium metrics
In order to access real time data or historical data (older than 3 months), 
you'll need to set the [api key](#configuration) and have some SAN tokens in your account.
All premium metrics are free for "santiment" token.

## Configuration

Optionally you can provide an api key which gives access to some premium metrics:

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

- `from_date`, `to_date` - A date or datetime in iso8601 format specifying the start and end datetime for the returned data for ex: `2018-06-01`
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

Using the defaults params:

```python
san.get("daily_active_addresses/santiment")
san.get("prices/santiment")
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

### All Projects

Returns a DataFrame with all the projects available in the Santiment API. Not all
metrics will be available for all the projects. The `slug` is a unique identifier
which can be used to retrieve most of the metrics.

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

### ERC20 Projects

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

### Daily Active Addresses

This metric includes the number of unique addresses that participated in the transfers of given token during the day. 

[Premium metric](#premium-metrics)

```python
san.get(
    "daily_active_addresses/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
```

Example result:

```
                           activeAddresses
datetime
2018-06-01 00:00:00+00:00                2
2018-06-02 00:00:00+00:00                4
2018-06-03 00:00:00+00:00                6
2018-06-04 00:00:00+00:00                6
2018-06-05 00:00:00+00:00               14
```

### Network Growth

Network Growth shows the number of new addresses being created on the project network each day.

[Premium metric](#premium-metrics)

```python
san.get(
    "network_growth/santiment",
    from_date="2018-12-01",
    to_date="2018-12-05",
    interval="1d"
)
```

```
                          newAddresses
datetime
2018-12-01 00:00:00+00:00            3
2018-12-02 00:00:00+00:00            2
2018-12-03 00:00:00+00:00            6
2018-12-04 00:00:00+00:00            2
2018-12-05 00:00:00+00:00            1
```

### Burn Rate - deprecated, replaced by 'Token Age Consumed'

Each transaction has an equivalent burn rate record. The burn rate is calculated by multiplying 
the number of tokens moved by the number of blocks in which they appeared. 
Spikes in burn rate could indicate large transactions or movement of tokens that have been held for a long time. 

[Premium metric](#premium-metrics)

Burn rate returns the same results as 'Token Age Consumed' and will be removed in the near future.

```python
san.get(
    "burn_rate/santiment",
    from_date="2018-05-01",
    to_date="2018-05-05",
    interval="1d"
)
```

Example result:

```
                               burnRate
datetime                                   
2018-05-01 00:00:00+00:00      2.514926e+09
2018-05-02 00:00:00+00:00      1.363158e+10
2018-05-03 00:00:00+00:00      2.182971e+09
2018-05-04 00:00:00+00:00      9.731035e+09
2018-05-05 00:00:00+00:00      2.867054e+10
```

### Token Age Consumed

Each transaction has an equivalent 'Age consumed' record. The consumed age is calculated by multiplying 
the number of tokens moved by the number of blocks in which they appeared. 
Spikes in consumed token age could indicate large transactions or movement of tokens that 
have been held for a long time. 

[Premium metric](#premium-metrics)

```python
san.get(
    "token_age_consumed/santiment",
    from_date="2018-05-01",
    to_date="2018-05-05",
    interval="1d"
)
```

Example result:

```
                           tokenAgeConsumed
datetime                                   
2018-05-01 00:00:00+00:00      2.514926e+09
2018-05-02 00:00:00+00:00      1.363158e+10
2018-05-03 00:00:00+00:00      2.182971e+09
2018-05-04 00:00:00+00:00      9.731035e+09
2018-05-05 00:00:00+00:00      2.867054e+10
```

### Average Token Age Consumed in Days

Based on 'Token Age Consumed' above, this returns the Token Age that gets consumed on 
average over the interval. The result is given in days instead of blocks. 

[Premium metric](#premium-metrics)


```python
san.get(
    "average_token_age_consumed_in_days/santiment",
    from_date="2018-05-01",
    to_date="2018-05-05",
    interval="1d"
)
```

Example result:

```
                             tokenAge
datetime                             
2018-05-01 00:00:00+00:00    6.353738
2018-05-02 00:00:00+00:00   22.303985
2018-05-03 00:00:00+00:00    3.873644
2018-05-04 00:00:00+00:00  140.566428
2018-05-05 00:00:00+00:00   56.730010
```


### Transaction Volume

Total amount of tokens for a project that were transacted on the blockchain. 
This metric includes only on-chain volume, not volume in exchanges. 

[Premium metric](#premium-metrics)


```python
san.get(
    "transaction_volume/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
```

Example result:

```
                           transactionVolume
datetime                                    
2018-06-01 00:00:00+00:00          46.848943
2018-06-02 00:00:00+00:00         666.194095
2018-06-03 00:00:00+00:00       31326.856743
2018-06-04 00:00:00+00:00        1371.245641
2018-06-05 00:00:00+00:00       42825.036598
```

### Token Velocity

Token Velocity returns the average number of times that a token changes wallets over the interval.
Simply put, a higher token velocity means that the same token is used in transactions more 
often within a set time frame. 

[Premium metric](#premium-metrics)


```python
san.get(
    "token_velocity/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d")
```

Example result:

```
                           tokenVelocity
datetime                                
2018-06-01 00:00:00+00:00           1.00
2018-06-02 00:00:00+00:00           3.00
2018-06-03 00:00:00+00:00           1.97
2018-06-04 00:00:00+00:00           1.00
2018-06-05 00:00:00+00:00           2.92
```

### Token Circulation

Token Circulation returns the total amount of tokens that have been sent at least once during 
each given time period. Minimum interval is '1d'.

[Premium metric](#premium-metrics)


```python
san.get(
    "token_circulation/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
```

Example result:

```
                           tokenCirculation
datetime                                   
2018-06-01 00:00:00+00:00         46.848943
2018-06-02 00:00:00+00:00        222.194095
2018-06-03 00:00:00+00:00      15933.955221
2018-06-04 00:00:00+00:00       1371.245641
2018-06-05 00:00:00+00:00      14678.249398
```

### Realized Value

Realized Value returns the total acquisition cost of all tokens on the network, 
based on the historical price when each coin was last sent, in USD. 
Returns RV for all tokens and RV for all tokens known to be on exchanges. 

[Premium metric](#premium-metrics)

```python
san.get(
    "realized_value/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
```

Example result:

```
                           nonExchangeRealizedValue  realizedValue
datetime                                                          
2018-06-01 00:00:00+00:00              2.334917e+07   9.248495e+07
2018-06-02 00:00:00+00:00              2.334917e+07   9.248498e+07
2018-06-03 00:00:00+00:00              2.335106e+07   9.248275e+07
2018-06-04 00:00:00+00:00              2.335138e+07   9.248269e+07
2018-06-05 00:00:00+00:00              2.335073e+07   9.243114e+07
```

### MVRV Ratio

MVRV ratio returns the ratio of the market value of all tokens (market cap) to the 
realized value of all tokens. 

[Premium metric](#premium-metrics)


```python
san.get(
    "mvrv_ratio/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
```

Example result:

```
                              ratio
datetime                           
2018-06-01 00:00:00+00:00  0.836489
2018-06-02 00:00:00+00:00  0.850379
2018-06-03 00:00:00+00:00  0.848195
2018-06-04 00:00:00+00:00  0.822243
2018-06-05 00:00:00+00:00  0.781964
```

### NVT Ratio

NVT ratio returns the Network-Value-to-Transactions ratio. We use the market cap as network value 
and either token circulation or transaction volume as a measurement for transactions, returning two values. 

[Premium metric](#premium-metrics)

```python
san.get(
    "nvt_ratio/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
```

Example result:

```
                           nvtRatioCirculation  nvtRatioTxVolume
datetime                                                        
2018-06-01 00:00:00+00:00         1.337498e+06      1.337498e+06
2018-06-02 00:00:00+00:00         2.820074e+05      9.405723e+04
2018-06-03 00:00:00+00:00         3.868500e+03      2.000213e+03
2018-06-04 00:00:00+00:00         4.569595e+04      4.569595e+04
2018-06-05 00:00:00+00:00         4.268927e+03      1.463171e+03
```

### Daily Active Deposits

Daily Active Deposits, similar to Daily Active Addresses, returns the number of unique addresses 
that participated in the transfers of tokens to exchange deposit addresses during the day. 

[Premium metric](#premium-metrics)

```python
san.get(
    "daily_active_deposits/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
```

Example result:

```
                           activeDeposits
datetime                                 
2018-06-01 00:00:00+00:00               0
2018-06-02 00:00:00+00:00               2
2018-06-03 00:00:00+00:00               0
2018-06-04 00:00:00+00:00               2
2018-06-05 00:00:00+00:00               6
```


### Github Activity

Returns a list of github activity for a given slug and time interval. 

[Premium metric](#premium-metrics)

[An article explaining the github activity tracking](https://medium.com/santiment/tracking-github-activity-of-crypto-projects-introducing-a-better-approach-9fb1af3f1c32)

```python
san.get(
    "github_activity/santiment",
    from_date="2018-05-01",
    to_date="2018-05-05",
    interval="1d"
)
```

Example result:

```
                           activity
datetime
2018-05-02 00:00:00+00:00        32
2018-05-03 00:00:00+00:00         9
2018-05-04 00:00:00+00:00        18
```

You can also fetch only events connected to development activity by using the `devActivity` query.

```python
san.get(
    "dev_activity/santiment",
    from_date="2018-05-01",
    to_date="2018-05-05",
    interval="1d"
)
```

Example result:

```
                           activity
datetime
2018-05-02 00:00:00+00:00        29
2018-05-03 00:00:00+00:00         9
2018-05-04 00:00:00+00:00        16
```

### Prices

Fetch history price in USD or BTC, traded volume and marketcap for a given slug.

```python
san.get(
    "prices/santiment",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

san.get(
    "prices/ethereum",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
```

Example result:

```
                              marketcap  priceBtc  priceUsd   volume
datetime
2018-06-01 00:00:00+00:00  7.736268e+07  0.000165  1.234635   852857
2018-06-02 00:00:00+00:00  7.864724e+07  0.000165  1.255135  1242520
2018-06-03 00:00:00+00:00  7.844339e+07  0.000163  1.251882  1032910
2018-06-04 00:00:00+00:00  7.604326e+07  0.000160  1.213578   617451

                              marketcap  priceBtc    priceUsd      volume
datetime
2018-06-01 00:00:00+00:00  5.756716e+10  0.077083  576.825315  1945890000
2018-06-02 00:00:00+00:00  5.875660e+10  0.077475  588.620775  1880390000
2018-06-03 00:00:00+00:00  6.097134e+10  0.079460  610.682490  1832550000
2018-06-04 00:00:00+00:00  6.015676e+10  0.079466  602.399792  1903430000
```

### Open, High, Close, Low Prices, Volume, Marketcap

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

```
                           openPriceUsd  closePriceUsd  highPriceUsd  lowPriceUsd   volume     marketcap
datetime
2018-06-01 00:00:00+00:00       1.24380        1.27668       1.26599      1.19099   852857  7.736268e+07
2018-06-02 00:00:00+00:00       1.26136        1.30779       1.27612      1.20958  1242520  7.864724e+07
2018-06-03 00:00:00+00:00       1.28270        1.28357       1.24625      1.21872  1032910  7.844339e+07
2018-06-04 00:00:00+00:00       1.23276        1.24910       1.18528      1.18010   617451  7.604326e+07
```

### Exchange Funds Flow

Fetch the difference between the tokens that were deposited minus the tokens that were withdrawn 
from an exchange for a given slug in the selected time period. 

[Premium metric](#premium-metrics)

```python
san.get(
    "exchange_funds_flow/santiment",
    from_date="2018-04-16T10:02:19Z",
    to_date="2018-05-23T10:02:19Z",
    interval="1d"
)
```

Example result:

```
                         inOutDifference
datetime
2018-04-16 10:02:19+00:00    -208.797310
2018-04-17 00:00:00+00:00     164.006467
2018-04-18 00:00:00+00:00       0.000000
2018-04-19 00:00:00+00:00  -45213.112849
2018-04-20 00:00:00+00:00 -135364.839572
```

### Social Volume Projects

Fetch a list of slugs for which there is social volume data.

```python
san.get("social_volume_projects")
```

Example result:

```
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

[Premium metric](#premium-metrics)

Arguments description:

- `endpoint` - social_volume/project_slug
- `interval` - an integer followed by one of: `m`, `h`, `d`, `w`
- `from_date` - a string representation of datetime value according to the iso8601 standard, e.g. "2018-04-16T10:02:19Z"
- `to_date` - a string representation of datetime value according to the iso8601 standard, e.g. "2018-05-23T10:02:19Z"
- `social_volume_type` - the source of mention counts, one of the following:
  * "PROFESSIONAL_TRADERS_CHAT_OVERVIEW" - shows how many times the given project was mentioned in the professional traders chat
  * "TELEGRAM_CHATS_OVERVIEW" - shows how many times the given project was mentioned across all telegram chats, except the project's own community chat (if there is one)
  * "TELEGRAM_DISCUSSION_OVERVIEW" - the general volume of messages in the project's community chat (if there is one)
  * "DISCORD_DISCUSSION_OVERVIEW" - shows how many times the given project has been mentioned in the discord channels

```python
san.get(
    "social_volume/dragonchain",
    interval="1d",
    from_date="2018-04-16T10:02:19Z",
    to_date="2018-05-23T10:02:19Z",
    social_volume_type="PROFESSIONAL_TRADERS_CHAT_OVERVIEW"
)
```

Example result:

```
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

### Topic search

Returns lists with the mentions of the search phrase from the selected source. 
The results are in two formats - the messages themselves and the data for building graph representation of the result. 

[Premium metric](#premium-metrics)

Arguments description:

- `endpoint` - a string in the format "topic_search/`fields`" where `fields` is one of the following:
  * "messages"
  * "chart_data"
- `source` - one of the following:
  * TELEGRAM
  * PROFESSIONAL_TRADERS_CHAT
  * REDDIT
  * DISCORD
- `search_text` - a string containing the key words for which the sources should be searched.
- `from_date` - a string representation of datetime value according to the iso8601 standard, e.g. "2018-04-16T10:02:19Z"
- `to_date` - a string representation of datetime value according to the iso8601 standard, e.g. "2018-04-16T10:02:19Z"
- `interval` - an integer followed by one of: `m`, `h`, `d`, `w`

```python
san.get(
    "topic_search/messages",
    source="TELEGRAM",
    search_text="btc moon",
    from_date="2018-08-01T12:00:00Z",
    to_date="2018-08-15T12:00:00Z",
    interval="6h"
)
```

Example result:

```
                                             messages
0   {'text': 'Btc dominance increasing', 'datetime...
1   {'text': 'Above the deafening noise of Sidera ...
2   {'text': 'Neo could finosh today in the green ...
```

or

```python
san.get(
    "topic_search/chart_data",
    source="TELEGRAM",
    search_text="btc moon",
    from_date="2018-08-01T12:00:00Z",
    to_date="2018-08-15T12:00:00Z",
    interval="6h"
)
```

Example result:

```
                                            chartData
0   {'mentionsCount': 224, 'datetime': '2018-08-01...
1   {'mentionsCount': 266, 'datetime': '2018-08-01...
2   {'mentionsCount': 191, 'datetime': '2018-08-02...
```


### Share of Deposits

Returns information for the shares of deposits that a given project has during the time interval. 

[Premium metric](#premium-metrics)

```python
san.get(
    "share_of_deposits/santiment",
    from_date="2019-01-01T00:00:00Z",
    to_date="2019-05-01T00:00:00Z",
    interval="1d"
)
```

Example result:


```
                           activeAddresses  activeDeposits  shareOfDeposits
datetime                                                                   
2019-01-01 00:00:00+00:00                5               1        20.000000
2019-01-02 00:00:00+00:00                2               0         0.000000
2019-01-03 00:00:00+00:00               13               2        15.384615
2019-01-04 00:00:00+00:00                8               2        25.000000
2019-01-05 00:00:00+00:00                7               1        14.285714

```

## Running tests

```
python setup.py test
```

## Running integration tests

```
python setup.py nosetests -a integration
```
