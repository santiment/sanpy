import san
from san.extras.backtest import Backtest

data = san.get("ohlcv/bitcoin", from_date="2018-01-01", to_date="2020-02-01")
data["returns"]= data.closePriceUsd.pct_change()

# Defining two moving averages
data["ma5"] = data.closePriceUsd.rolling(5).mean()
data["ma20"] = data.closePriceUsd.rolling(20).mean()

data = data.dropna()

trades = data["ma5"] > data["ma20"]

back_test = Backtest(
    data.returns,
    trades,
    lagged=True,
    transaction_cost = 0.003,
    percent_invested_per_trade = 1
)

print(back_test.summary())

back_test.plot_backtest(viz='hodl')
