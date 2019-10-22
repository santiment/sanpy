import datetime
import pandas as pd
import numpy as np
import san
import matplotlib.pyplot as plt

class Backtest:

    def __init__(self, returns:pd.Series, trades:pd.Series, lagged=True, transaction_cost = 0, percent_invested_per_trade = 1):
        """ Initializing Backtesting function
            Init function generates performance of the test and several risk metrics. The object lets
            you specify wether you want to lag the trades to avoid overfitting, the transaction costs
            and the percentage of the portfolio to be invested per trade (50% as 0.5).

            Trade example:
                With given prices [P1, P2, P3] and given trades [False, True, False] 
                you buy asset when the price is P2 and sell when the price is P3.
        """

        if lagged:
            trades = trades.shift(1)
            trades.iloc[0] = False
        self.strategy_returns = ((returns * percent_invested_per_trade) * trades)
        self.trades = trades
        
        self.nr_trades = 0
        for i in range(1, len(trades)):
            if trades[i] != trades[i - 1]:
                self.strategy_returns.iloc[i] -= transaction_cost
                self.nr_trades += 1
        if trades[-1]:  # include last day sell to make benchmark possible
            self.nr_trades += 1

        self.performance = ((self.strategy_returns * percent_invested_per_trade) * trades + 1).cumprod() - 1
        self.benchmark = (returns + 1).cumprod() - 1
        self.sharpe_ratio = (self.strategy_returns.mean() * 365) / (self.strategy_returns.std() * np.sqrt(365))
        
        running_value = np.array(self.performance)
        running_value[0] = 0
        a = np.argmax(np.maximum.accumulate(running_value) - running_value)  # end of the period
        b = np.argmax(running_value[:a])  # start of period
        self.maximum_drawdown = ((running_value[a] - running_value[b]) / running_value[b]) * 100  # Maximum Drawdown


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

    def get_return(self, decimals=2):
        return round(((self.performance.iloc[-1] + 1) / (self.performance.iloc[1] + 1) - 1) * 100, decimals)

    def get_return_benchmark(self, decimals=2):
        return round(((self.benchmark.iloc[-1] + 1) / (self.benchmark.iloc[0] + 1) - 1) * 100, decimals)

    def get_annualized_return(self, decimals=2):
        return round((((self.performance.iloc[-1] + 1) ** (1 / len(self.performance))) - 1) * 365 * 100, decimals)

    def summary(self):
        print("Returns in Percent: ", self.get_return())
        print("Returns Benchmark in Percent: ", self.get_return_benchmark())
        print("Annualized Returns in Percent: ", self.get_annualized_return())
        print("Annualized Sharpe Raito: ", self.get_sharpe_ratio())
        print("Number of Trades: ", self.get_nr_trades())

    def plot_backtest(self, viz=None):
        ''' param viz: None OR "trades" OR "hodl".
        '''
        plt.figure(figsize=(15,8))
        plt.plot(self.performance,label="performance")
        plt.plot(self.benchmark,label="holding")
        if viz == 'trades':
            plt.vlines(
                self.trades[self.trades == True].index, 
                min(self.performance.min(), self.benchmark.min()), 
                max(self.performance.max(), self.benchmark.max()),
                color = '#424242'
            )
        elif viz == 'hodl':
            hodl_periods = []
            for i in range(len(self.trades)):
                state = self.trades[i-1] if i > 0 else self.trades[i]
                if self.trades[i] and not state:
                    start = self.strategy_returns.index[i]
                elif not self.trades[i] and state:
                    hodl_periods.append([start, self.strategy_returns.index[i]])
            if self.trades[-1]:
                hodl_periods.append([start, self.strategy_returns.index[i]])
            for hodl_period in hodl_periods:
                plt.axvspan(hodl_period[0], hodl_period[1], color='#aeffa8')
        plt.legend()
        plt.show()


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
