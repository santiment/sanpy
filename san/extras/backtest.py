import datetime
import pandas as pd
import logging
from san.extras.strategy.prices import Prices
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from san.extras.utils import str_to_ts


def prepare_df(source_df: pd.DataFrame):
    '''
    DF can be provided to the object with dt index or dt column
    which will be transformed into index.
    '''
    df = source_df.copy()
    if 'dt' in df.columns:
        if not is_datetime(df['dt']):
            df['dt'] = df['dt'].apply(lambda x: str_to_ts(x))
        df.set_index('dt', inplace=True)
    else:
        if type(df.index) != pd.core.indexes.datetimes.DatetimeIndex:
            logging.error('Please provide a df with datetime index or index data using column named "dt"')
            return
        else:
            df.index.name = 'dt'
            df = df.reset_index()
            df['dt'] = [item.replace(tzinfo=None) for item in df['dt']]
            df.set_index('dt', inplace=True)
    return df


class Backtest:
    '''
    Backtest class provides the ability to calculate portfolio step-by step returns
    based on the assets' price returns and portfolio structure
    and build strategy models with transaction fees taken into account.

    TODO:
    '''

    def __init__(self,
                 start_dt: str or datetime.datetime,
                 initial_investment: float = 10**6,
                 default_trades_limit: int = 1,
                 accuracy: float = 3*10**(-6)
                 ):
        self.start_dt = str_to_ts(start_dt)
        self.initial_investment = initial_investment
        self.default_transfers_limit = default_trades_limit
        self.accuracy = accuracy

        self.prices = Prices(start_dt=self.start_dt)
        self.portfolio_price_change = pd.DataFrame(None)
        self.portfolio_price = pd.DataFrame(None)
        self.portfolio = pd.DataFrame(None)
        self.trades_log = pd.DataFrame(None)
        self.fees = pd.DataFrame(None)

    def add_portfolio(self, portfolio_df, replace=False):
        '''
        Input DataFrame examples:

                        asset   share
        dt
        2020-01-01       eth     0.5
        2020-01-01       uni     0.5
        2020-01-02       eth     0.6
        2020-01-03       uni     0.4
        dt is pandas DateTimeIndex.

                dt               asset   share
        index
        1       2020-01-01       eth     0.5
        2       2020-01-01       uni     0.5
        3       2020-01-02       eth     0.6
        4       2020-01-03       uni     0.4
        dt contains date/datetime objects
        or string values that can be parsed as date/datetime
        '''
        df = prepare_df(portfolio_df)

        if replace:
            self.portfolio = self.portfolio[~self.portfolio.index.isin(list(df.index))]
        else:
            df = df[~df.index.isin(self.portfolio.index)]
        self.portfolio = self.portfolio.append(df).sort_index()

    def add_trades(self, trades_df, replace=False):
        df = prepare_df(trades_df)
        if replace:
            self.trades_log = self.trades_log[~self.trades_log.index.isin(list(df.index))]
        else:
            df = df[~df.index.isin(list(self.trades_log.index))]
        self.trades_log = self.trades_log.append(df).sort_index()

    def add_fees(self, fees_df: pd.DataFrame):
        df = prepare_df(fees_df)
        self.fees = self.fees[~self.fees.index.isin(df.index)]
        self.fees = self.fees.append(df).sort_index()

    def get_trades_amount(self, dt):
        trades_amount = len(self.trades_log[self.trades_log.index == dt])
        trades_amount *= self.default_transfers_limit
        return trades_amount

    def init_portfolio_price_change(self):
        if self.start_dt not in list(self.portfolio.index):
            logging.error('Please provide the portfolio dataframe')
            return

        self.portfolio_price_change = pd.DataFrame({
            'dt': [self.start_dt],
            'price_change': [1]
        }).set_index('dt')

    def init_portfolio_price(self):
        dt_portfolio_price = self.initial_investment
        dt_trades_amount = self.get_trades_amount(self.start_dt)
        if dt_trades_amount > 0:
            txn_fee = float(self.fees.loc[self.start_dt]['value'])
            dt_fee = txn_fee * dt_trades_amount
            dt_portfolio_price -= dt_fee

        self.portfolio_price = pd.DataFrame({
            'dt': [self.start_dt],
            'value': [dt_portfolio_price],
            'max_trades': [dt_trades_amount]
        }).set_index('dt')

    def get_available_portfolio_dts(self, start_dt, end_dt):
        dt1 = start_dt if type(start_dt) == datetime.datetime else str_to_ts(start_dt)

        if end_dt:
            dt2 = end_dt if end_dt and type(end_dt) == datetime.datetime else str_to_ts(end_dt)
            return list(self.portfolio[(self.portfolio.index >= dt1) & (self.portfolio.index <= dt2)].index.unique())
        else:
            return list(self.portfolio[self.portfolio.index >= dt1].index.unique())

    def build_portfolio_price_change(self, start_dt, end_dt, rebuild=False):
        '''
        Build the daily returns of the provided strategy
        '''

        if rebuild:
            self.portfolio_price_change = self.portfolio_price_change[self.portfolio_price_change.index <= start_dt]

        if self.portfolio_price_change.empty:
            self.init_portfolio_price_change()

        dts = self.get_available_portfolio_dts(start_dt, end_dt)

        for dt in dts[1:]:
            if dt in self.portfolio_price_change.index:
                logging.info(f'The price change data already contains values for {dt}')
                continue

            prev_dt = dts[dts.index(dt) - 1]
            dt_portfolio = self.portfolio[self.portfolio['share'] > 0].loc[prev_dt]

            dt_prices = self.prices.prices.loc[[dt]][['asset', 'price_change']]
            dt_prices = dt_prices[dt_prices['price_change'] > 0]
            dt_prices = dt_prices[dt_prices['asset'].isin(list(dt_portfolio['asset'].unique()))]

            dt_portfolio = {el['asset']: el['share'] for i, el in dt_portfolio.iterrows()}
            dt_prices = {el['asset']: el['price_change'] for i, el in dt_prices.iterrows()}

            if abs(sum(dt_portfolio.values()) - 1) > self.accuracy:
                logging.warning(f'Portfolio asset shares sum is different from 1 on {dt} ')

            if not all(asset in dt_prices for asset in dt_portfolio):
                logging.error(f'Price data is missing for some of assets on {dt}')
                return

            dt_price_change = 0
            for asset in dt_portfolio:
                dt_price_change += dt_portfolio[asset] * dt_prices[asset]

            self.portfolio_price_change = self.portfolio_price_change[self.portfolio_price_change.index != dt]
            self.portfolio_price_change.loc[dt] = {'price_change': dt_price_change}

    def build_portfolio_price(self, start_dt, end_dt, rebuild=False):
        '''
        TODO: process txns limit for each trade (provided via metadata or a separate column?)
        '''

        if rebuild:
            self.portfolio_price_change = self.portfolio_price_change[self.portfolio_price_change.index <= start_dt]

        dts = self.get_available_portfolio_dts(start_dt, end_dt)

        # We need portfolio price change for the desired time range to run the backtest with transfers
        if any(dt not in self.portfolio_price_change.index for dt in dts):
            self.build_portfolio_price_change(start_dt, end_dt, rebuild)

        if self.portfolio_price.empty:
            self.init_portfolio_price()

        for dt in dts[1:]:

            if dt in self.portfolio_price.index:
                logging.info(f'The portfolio price data already contains values for {dt}')
                continue

            prev_dt = dts[dts.index(dt) - 1]
            if prev_dt not in self.portfolio_price.index:
                logging.error(f'Portfolio price data is missing for {prev_dt}')
                return
            dt_portfolio_price = float(self.portfolio_price.loc[prev_dt]['value']) * float(self.portfolio_price_change.loc[dt]['price_change'])

            dt_trades_amount = self.get_trades_amount(dt)
            if dt_trades_amount > 0:
                txn_fee = float(self.fees.loc[dt]['value'])
                dt_fee = txn_fee * dt_trades_amount
                dt_portfolio_price -= dt_fee

            self.portfolio_price.loc[dt] = {
                'value': dt_portfolio_price,
                'max_trades': dt_trades_amount
            }
