import datetime
import pandas as pd
import numpy as np
import san

class Backtest:

    def __init__(self, returns, trades, lagged=True, transaction_cost = 0, percent_invested_per_trade = 1):
        """ Initializing Backtesting function

        Init function generates performance of the test and several risk metrics. The object lets
        you specify wether you want to lag the trades to avoid overfitting, the transaction costs
        and the percentage of the portfolio to be invested per trade (50% as 0.5).
        """

        if lagged:
            trades = trades.shift(1)
            trades.iloc[0] = False

        else:
            pass

        self.strategy_returns = ((returns * percent_invested_per_trade) * trades)

        #if transaction_cost != 0:
        self.nr_trades = 0
        for index, trade in enumerate(trades):
            if (trade != 0) & (trades[index - 1] == 0):
                self.strategy_returns.iloc[index + 1] = self.strategy_returns.iloc[index + 1] - transaction_cost
                self.nr_trades += 1
            elif (trade == 0) & (trades[index - 1] != 0):
                self.strategy_returns.iloc[index + 1] = self.strategy_returns.iloc[index + 1] - transaction_cost
                self.nr_trades += 1
            else:
                pass

        self.performance = ((self.strategy_returns * percent_invested_per_trade) * trades + 1).cumprod() -1

        self.benchmark = (returns + 1).cumprod() -1
        self.sharpe_ratio = (self.strategy_returns.mean() * 365) / (self.strategy_returns.std() * np.sqrt(365))

        max_draw = 0  # Maximum drawdown
        try:
            running_value = np.array(self.performance)
            a = np.argmax(np.maximum.accumulate(running_value) - running_value)  # end of the period
            b = np.argmax(running_value[:a])  # start of period
            max_draw = ((running_value[a]-running_value[b])/running_value[b]) * 100  # Maximum Drawdown
        except Exception as e:
            print(e)

        self.maximum_drawdown = max_draw


    def get_sharpe_ratio(self):
        return round(self.sharpe_ratio, 2)


    def get_value_at_risk(self, percentile=5):
        sorted_rets = sorted(self.strategy_returns)
        var = np.percentile(sorted_rets, percentile)
        return round(var * 100, 2)

    def get_nr_trades(self):
        return self.nr_trades

    def get_maximum_drawdown(self):
        return round(self.maximum_drawdown, 2)


    def get_return(self):
        return round(((self.performance.iloc[-1] + 1) / (self.performance.iloc[0] + 1) - 1) * 100, 2)


    def get_return_benchmark(self):
        return round(((self.benchmark.iloc[-1] + 1) / (self.benchmark.iloc[0] + 1) - 1) * 100, 2)


    def get_annualized_return(self):
        return round((((self.performance.iloc[-1] + 1)** (1/len(self.performance))) - 1) *365 * 100, 2)


    def summary(self):
        print("Returns in Percent: ", self.get_return())
        print("Returns Benchmark in Percent: ", self.get_return_benchmark())
        print("Annualized Returns in Percent: ", self.get_annualized_return())
        print("Annualized Sharpe Raito: ", self.get_sharpe_ratio())
        print("Number of Trades: ", self.get_nr_trades())

class Portfolio:

    def __init__(self, start_date="2017-01-01", end_date=datetime.datetime.now().strftime("%Y-%m-%d"), asset_list=[]):
        """ Takes in list of project slugs"""

        self.start_date = start_date
        self.end_date = end_date
        self.asset_list = asset_list
        self.portfolio = pd.DataFrame()
        self.benchmark = san.get("ohlcv/bitcoin", from_date=start_date,
                                 to_date=end_date).closePriceUsd.pct_change()

        for portfolio_asset in asset_list:
            self.portfolio[portfolio_asset] = san.get("ohlcv/" + portfolio_asset,
                                                      from_date=start_date,
                                                      to_date=end_date).closePriceUsd.pct_change()
            self.portfolio = self.portfolio.replace([np.inf, -np.inf], 0)
            self.metrics = dict()


    def add_project(self, project):
        self.asset_list.append(project)
        self.portfolio[project] = san.get("ohlcv/" + project, from_date=self.start_date,
                                          to_date=self.end_date).closePriceUsd.pct_change()
        self.portfolio = self.portfolio.replace([np.inf, -np.inf], 0)

    def remove_project(self, project):
        self.portfolio = self.portfolio.drop([project], axis=1)
        self.asset_list.remove(project)


    def all_assets(self):
        print(self.asset_list)
        return self.asset_list


    def metrics(self, metric):
        metric_data = pd.DataFrame()
        for asset in self.asset_list:
            metric_data[asset] =  san.get(metric + "/" + asset,
                                          from_date=self.start_date, to_date=self.end_date).iloc[:,0]

        self.metrics[metric] = metric_data
        return metric_data


    def show_portfolio(self):
        return self.portfolio
