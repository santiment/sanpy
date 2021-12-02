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
    The tool provides the ability to calculate portfolio returns
    based on the assets' prices and portfolio structure
    and build strategy models with transaction fees taken into account.

    Backtest is designed to work together with Strategy and Strategy-inherited classes,
    some components may be provided from the Strategy-inherited entity
    which contains the strategy supposed to be backtested.
    '''

    def __init__(self,
                 start_dt: str or datetime.datetime,
                 initial_investment: float = 10**6,
                 default_transfers_limit: int = 1,
                 accuracy: float = 3*10**(-6),
                 granularity: str = '1D'
                 ):
        self.start_dt = str_to_ts(start_dt)
        self.initial_investment = initial_investment
        self.default_transfers_limit = default_transfers_limit
        self.accuracy = accuracy

        self.prices = Prices(start_dt=self.start_dt, granularity=granularity)

        self.portfolio = pd.DataFrame(None)
        self.net_returns = pd.DataFrame(None)
        self.portfolio_price = pd.DataFrame(None)

        self.trades_log = pd.DataFrame(None)
        self.fees = pd.DataFrame(None)

    def add_portfolio(self, portfolio_df: pd.DataFrame, replace: bool = False):
        '''
        Sets or updates the portfolio structure dataframe

        Input dataframe is supposed to be indexes with DateTimeIndex
        or to have a column named 'dt' which contains date/datetime objects
        or string values that can be parsed as date/datetime

        The DataFrame examples:

                        asset   share
        dt
        2020-01-01       eth     0.5
        2020-01-01       uni     0.5
        2020-01-02       eth     0.6
        2020-01-03       uni     0.4


                dt               asset   share
        index
        1       2020-01-01       eth     0.5
        2       2020-01-01       uni     0.5
        3       2020-01-02       eth     0.6
        4       2020-01-03       uni     0.4
        '''
        df = prepare_df(portfolio_df)

        if replace:
            self.portfolio = self.portfolio[~self.portfolio.index.isin(list(df.index))]
        else:
            df = df[~df.index.isin(self.portfolio.index)]
        self.portfolio = self.portfolio.append(df).sort_index()

    def add_trades(self, trades_df: pd.DataFrame, replace: bool = False):
        '''
        Sets or updates the trades dataframe
        '''

        df = prepare_df(trades_df)
        if replace:
            self.trades_log = self.trades_log[~self.trades_log.index.isin(list(df.index))]
        else:
            df = df[~df.index.isin(list(self.trades_log.index))]
        self.trades_log = self.trades_log.append(df).sort_index()

    def add_fees(self, fees_df: pd.DataFrame):
        '''
        Sets or updates the fees data.
        Fee values should be provided in the same currency that is used for prices.

        The DataFrame examples:

                        value
        dt
        2020-01-01       7.5
        2020-01-01       10.0
        2020-01-02       9.0
        2020-01-03       9.5


                dt               value
        index
        1       2020-01-01       7.5
        2       2020-01-01       10.0
        3       2020-01-02       9.0
        4       2020-01-03       9.5
        '''

        df = prepare_df(fees_df)
        df['value'] *= self.default_transfers_limit
        self.fees = self.fees[~self.fees.index.isin(df.index)]
        self.fees = self.fees.append(df).sort_index()

    def update_default_transfers_limit(self, new_default_transfers_limit: int):
        '''
        Updates the fees data according to new transfers_limit value
        '''
        coeff = new_default_transfers_limit/self.default_transfers_limit
        self.fees['value'] *= coeff

    def get_trades_fee_and_amount(self, dt):
        '''
        Calculates the total trades fee for the provided dt and the amount of transactions on the dt.
        '''
        current_trades = self.trades_log[self.trades_log.index == dt]
        if len(current_trades) == 0:
            return 0, 0

        # If the fee values are provided via trades log
        # They are used instead of the fees metric
        total_trade_fee = 0
        trades_amount = len(current_trades)

        if 'fee' in self.trades_log.columns:
            # Take the transactions with provided txn fee
            # And exclude them from the temp current_trades df
            total_trade_fee += float(current_trades['fee'].sum())
            current_trades = current_trades[(current_trades['fee'].isna())]

        # Calculate the remaining transfer fees according to the fees dataframe of the entity
        if len(current_trades) > 0:
            txn_fee = float(self.fees.loc[dt]['value'])
            total_trade_fee += len(current_trades) * txn_fee
        return total_trade_fee, trades_amount

    def init_net_returns(self):
        '''
        Initiates the net returns dataframe
        '''

        if self.start_dt not in list(self.portfolio.index):
            logging.error('Please provide the portfolio dataframe')
            return

        self.net_returns = pd.DataFrame({
            'dt': [self.start_dt],
            'value': [1]
        }).set_index('dt')

    def init_portfolio_price(self):
        '''
        Initiates the portfolio price dataframe
        '''

        dt_portfolio_price = self.initial_investment

        trades_fee, trades_amount = self.get_trades_fee_and_amount(self.start_dt)
        if trades_fee:
            dt_portfolio_price -= trades_fee

        self.portfolio_price = pd.DataFrame({
            'dt': [self.start_dt],
            'value': [dt_portfolio_price],
            'trades_amount': [trades_amount],
            'trades_fee': [trades_fee]
        }).set_index('dt')

    def get_available_portfolio_dts(self, df, start_dt, end_dt):
        '''
        Gets the available date/datetime points from the range of start_dt and end_dt
        from the provided dataframe
        '''

        dt1 = start_dt if type(start_dt) == datetime.datetime else str_to_ts(start_dt)

        if end_dt:
            dt2 = end_dt if end_dt and type(end_dt) == datetime.datetime else str_to_ts(end_dt)
            return list(df[(df.index >= dt1) & (df.index <= dt2)].index.unique())
        else:
            return list(df[df.index >= dt1].index.unique())

    def build_net_returns(self,
                          start_dt: str or datetime,
                          end_dt: str or datetime or None = None,
                          rebuild: bool = False):
        '''
        Builds the net returns of the portfolio in the range from the start_dt to the end_dt
        based only on the price changes and the assets' shares in the portfolio.
        '''

        if rebuild:
            self.net_returns = self.net_returns[self.net_returns.index <= start_dt]

        if self.net_returns.empty:
            self.init_net_returns()

        dts = self.get_available_portfolio_dts(self.portfolio, start_dt, end_dt)

        for dt in dts[1:]:
            if dt in self.net_returns.index:
                logging.info(f'The net returns data already contains values for {dt}')
                continue

            prev_dt = dts[dts.index(dt) - 1]
            dt_portfolio = self.portfolio[self.portfolio['share'] > 0].loc[[prev_dt]]

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

            self.net_returns = self.net_returns[self.net_returns.index != dt]
            self.net_returns.loc[dt] = {'value': dt_price_change}

    def build_portfolio_price(self,
                              start_dt: str or datetime,
                              end_dt: str or datetime or None = None,
                              rebuild: bool = False):
        '''
        Calculates the portfolio price in the range from the start_dt to the end_dt.
        Takes into account the initial investment, trades log and fees.
        Calculates the returns and the performance based the portfolio price.

        Calls build_net_returns in case the net_returns is missing.
        '''

        if rebuild:
            self.portfolio_price = self.portfolio_price[self.portfolio_price.index <= start_dt]

        dts = self.get_available_portfolio_dts(self.portfolio, start_dt, end_dt)

        # We need portfolio price change for the desired time range to run the backtest with transfers
        if any(dt not in self.net_returns.index for dt in dts):
            self.build_net_returns(start_dt, end_dt, rebuild)

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
            dt_portfolio_price = float(self.portfolio_price.loc[prev_dt]['value']) \
                * float(self.net_returns.loc[dt]['value'])

            trades_fee, trades_amount = self.get_trades_fee_and_amount(dt)
            if trades_fee:
                dt_portfolio_price -= trades_fee

            self.portfolio_price.loc[dt] = {
                'value': dt_portfolio_price,
                'trades_amount': trades_amount,
                'trades_fee': trades_fee
            }

        self.portfolio_price['returns'] = 1 + self.portfolio_price['value'].pct_change().fillna(0)
        self.portfolio_price['performance'] = self.portfolio_price['returns'].cumprod()
