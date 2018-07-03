# Santiment API python client

## Installation

```bash
pip install -r requirements.txt
```

Running tests:
```bash
python setup.py test
```


## Configuration

Optionally you can provide an api key which gives access to some restricted metrics:

```python
import san
san.ApiConfig.api_key = 'api-key-provided-by-sanbase'
```

## Retrieving data from the API

The data is fetched by providing a string in the format `query/slug` and additional parameters.

Parameters:

* `from_date`, `to_date` - A date or datetime in iso8601 format specifying the start and end datetime for the returned data for ex: `2018-06-01`
* `interval` - The interval of the returned data - an integer followed by one of: `s`, `m`, `h`, `d` or `w`

The returned value is in `pandas DataFrame` format.

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
    "prices/san_usd",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)
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
   activeAddresses              datetime
0                2  2018-06-01T00:00:00Z
1                4  2018-06-02T00:00:00Z
2                6  2018-06-03T00:00:00Z
3                6  2018-06-04T00:00:00Z
4               14  2018-06-05T00:00:00Z
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
       burnRate              datetime
0  3.009476e+06  2018-05-01T11:00:00Z
1  2.161845e+09  2018-05-01T14:00:00Z
2  7.263414e+05  2018-05-01T17:00:00Z
3  7.424445e+07  2018-05-01T19:00:00Z
4  6.987085e+07  2018-05-01T21:00:00Z
5  2.052304e+08  2018-05-01T22:00:00Z
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
               datetime  transactionVolume
0  2018-05-01T11:00:00Z         298.707310
1  2018-05-01T14:00:00Z       19356.439888
2  2018-05-01T17:00:00Z        1088.967586
3  2018-05-01T19:00:00Z          99.600000
4  2018-05-01T21:00:00Z        6177.411536
5  2018-05-01T22:00:00Z       41397.348795
6  2018-05-01T23:00:00Z         300.000000
```

### Prices
Fetch price history for a given ticker in USD or BTC.

```python

prices = san.get(
    "prices/san_usd",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

prices = san.get(
    "prices/san_btc",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

prices = san.get(
    "prices/eos_usd",
    from_date="2018-06-01",
    to_date="2018-06-05",
    interval="1d"
)

```

Example result:

```

               datetime            priceUsd
0  2018-06-01T00:00:00Z   1.234634930555555
1  2018-06-02T00:00:00Z  1.2551352777777771
2  2018-06-03T00:00:00Z   1.251881943462897
3  2018-06-04T00:00:00Z  1.2135782638888888


               datetime                priceBtc
0  2018-06-01T00:00:00Z   0.0001649780416666666
1  2018-06-02T00:00:00Z  0.00016521851041666669
2  2018-06-03T00:00:00Z    0.000162902558303887
3  2018-06-04T00:00:00Z   0.0001600935277777778


               datetime            priceUsd
0  2018-06-01T00:00:00Z  12.179371527777779
1  2018-06-02T00:00:00Z  13.733567361111099
2  2018-06-03T00:00:00Z   14.72066584507042
3  2018-06-04T00:00:00Z   13.91701289198606

```
