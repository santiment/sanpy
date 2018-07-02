# Santiment API python client

## Installation

## Configuration

## Retrieving data from the API

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
