# Santiment API python client

## Installation

```bash
pip install sanpy
```

## Configuration

Optionally you can provide an api key which gives access to some restricted metrics:

```python
import san
san.ApiConfig.api_key = 'api-key-provided-by-sanbase'
```

## Retrieving data from the API

The data is fetched by providing a string in the format `query/slug` and additional parameters.

* `query`: Available queries can be found in section: [Available metrics](#available_metrics)
* `slug`: A list of projects with their slugs, names, etc. can be fetched like this:

```python
import san
san.get("projects/all")
```

```
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

#### Fetch single metric

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

#### Batching multiple queries

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

<a name='available_metrics'></a>
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

```
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

```
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

```
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

```
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

```

                                         priceBtc            priceUsd
datetime
2018-06-01 00:00:00+00:00   0.0001649780416666666   1.234634930555555
2018-06-02 00:00:00+00:00  0.00016521851041666669  1.2551352777777771
2018-06-03 00:00:00+00:00    0.000162902558303887   1.251881943462897
2018-06-04 00:00:00+00:00   0.0001600935277777778  1.2135782638888888


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
