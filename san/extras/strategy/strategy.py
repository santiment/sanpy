import logging
import datetime
import itertools
import pandas as pd
from croniter import croniter

from .assets import Assets
from .prices import Prices
from .signals import Signals
from san.extras.utils import str_to_ts, parse_str_to_timedelta


pd.options.mode.chained_assignment = None


class Strategy:
    '''
    Tool that allows you to create and backtest trading strategies based on signals.

    Parameters
    ----------
    start_dt : str or datetime
        Datetime when the portfolio was initiated.
    end_dt : str or datetime, default None
        Datetime to stop the strategy.
    granularity : str, default '1D'
        Time distance between datetimes.
    decision_delay : int, default 0
        Time gap between the signal's dt and the action that should be performed due to that signal.
    init_asset:  str or None, default None
        Asset the investor owes before the stategy was initiated. Init_asset will be used in
        order to buy all necessary assets on the first day or later.
        Init_asset automatically will be set as forst reserve_asset if not provided explicitly.
    add_asset_once_authorized: bool, default False
        Refers to authorization policy. Once the asset has been authorized fires a buy signal if True.
        If there's already a buy signal for that asset does nothing. Does nothing if False.
    sell_assets_once_unauthorized: bool, default True
        Refers to authorization policy. Once the asset has been unauthorized fires a sell signal if True.
        If there's already a sell signal for that asset does nothing. Does nothing if False.

    Examples
    ----------
    Portfolio is a collection of assets. Assets' proportions are not constant and could change over time.
    Portfolio is represented by assets and assets' shares in the portfolio on a particular date.
    Given approach works portofolios that are represented by assets' shares (unlike raw money
    equivalent). That approach is agnostic to the amount of money you allocate in the portfolio.

    Portfolio is stored as a pandas DataFrame:
                asset       share
    dt
    2021-01-01  eth         0.5
    2021-01-01  uni         0.25
    2021-01-01  dai         0.25
    2021-01-02  eth         0.5
    2021-01-02  uni         0.5
    '''

    accuracy = 3 * 10**(-6)

    def __init__(
        self,
        start_dt: str or datetime,
        end_dt: str or datetime or None = None,
        granularity: str = '1D',
        decision_delay: int = 0,
        init_asset: str or None = None,
        add_asset_once_authorized: bool = False,
        sell_assets_once_unauthorized: bool = True
    ):
        self._granularity = granularity
        self._start_dt = str_to_ts(start_dt)
        self.end_dt = end_dt
        self.decision_delay = datetime.timedelta(seconds=decision_delay)
        self.init_asset = init_asset
        self.add_asset_once_authorized = add_asset_once_authorized
        self.sell_assets_once_unauthorized = sell_assets_once_unauthorized

        self.assets = Assets(start_dt=start_dt, end_dt=end_dt, granularity=granularity, init_asset=init_asset)
        self.prices = Prices(start_dt=start_dt, end_dt=end_dt, granularity=granularity)
        self.signals = Signals(start_dt=start_dt, end_dt=end_dt, granularity=granularity, decision_delay=decision_delay)

        self.portfolio = pd.DataFrame(None)
        self.asset_shares = pd.DataFrame(None)
        self.trades_log = pd.DataFrame(columns=['dt', 'order', 'share', 'from', 'to', 'fee', 'metadata'])

    def add_periodic_rebalance(self, cron_expr: str, skip_rebalance_on_init: bool = True):
        '''
        Automatically generates rebalance signals when set up according to a provided cron expression.

        Parameters
        ----------
        cron_expr : str
            Cron expression according to each rebalance signals are fired.
            E.g. monthly rebalance: '0 0 1 * *'
        skip_rebalance_on_init : bool, default True
            By default first rebalance signal is fired on start_dt. Should be False in order to
            skip first rebalance signal.

        TODO: how to skip first rebalance?
        '''

        self.cron = croniter(cron_expr, self._start_dt)
        if skip_rebalance_on_init:
            self.cron.get_next()

    def set_rebalance_proportion(self, proportions_df: pd.DataFrame):
        '''
        Sets rebalance propotions.
        Rebalnce proportion is a desired combination of assets in the portfolio. Assets' shares are
        changing over time because of price fluctuations or buy/sell signals. Rebalance proportions
        are used to keep assets' shares in a desired (target) propotions. Usually used once
        rebalance signal is fired.
        Rebalance proportion could be equal or rebalancing could be linked to a specific timeseries.
        E.g. in order to keep assets' shares proportional to it's market cap provide
        market cap timeseries as a rebalance proportion.

        Parameters
        ----------
        proportions_df: pd.DataFrame
            DataFrame in a format (index)dt - (column)asset - (column)value.
            Represents proportions (value) of assets (asset) for a particular datetime (dt).

        Examples
        ----------
        proportions_df example:
                            asset       value
            dt
            2021-01-01      eth         1
            2021-01-01      uni         1
            2021-01-01      dai         2
            2021-01-02      eth         1
            2021-01-02      uni         1
        '''

        assert proportions_df.index.name == 'dt', 'dt index not found'
        assert 'asset' in proportions_df.columns, 'asset column not found.'
        assert 'value' in proportions_df.columns, 'value column not found.'

        # update according to value provided at last
        self.asset_shares = self.asset_shares.append(proportions_df)
        self.asset_shares = self.asset_shares.groupby(['dt', 'asset']).last().reset_index('asset').sort_index()

    def compute_asset_shares_for_dt(self, dt: str or datetime.datetime, assets: list = []):
        '''
        Computes required asset shares for a provided datetime according to rebalance proportions.

        Parameters
        ----------
        dt : str or datetime.datetime
            Datatime to compute asset shares for.
        assets : list, default []
            Pick subset of assets from assets available in rebalance proportions df. If empty picks
            up all available assets.
        '''

        if dt not in self.asset_shares.index:
            logging.warning(f'Assets shares are missing for {dt}. The shares will be set to 1.')
            # TODO: keep same rebalance proportions
            self.set_rebalance_proportion(pd.DataFrame({'dt': dt, 'asset': assets, 'value': 1.0}).set_index('dt'))

        df = self.asset_shares.loc[[dt]]
        if assets:
            # TODO: consider authorized assets only
            df = df[df['asset'].isin(assets)]
        else:
            return []

        df['share'] = df['value'] / df['value'].sum()
        return df[['asset', 'share']]

    def set_default_rebalance_proportion(self, end_dt: datetime.datetime or str or None):
        '''
        Sets equal rebalance proportions for all assets. E.g. all assets have the same
        share in the portfolio.

        Parameters
        ----------
        end_dt : datetime.datetime or str or None
            Final datetime for a rebalance proportion dataframe.
            Sets strategy start_dt if end_dt is None.
        '''

        if not end_dt:
            end_dt = self._start_dt

        df = pd.DataFrame(
            list(itertools.product(
                pd.date_range(self._start_dt, end_dt, freq=self._granularity),  # dates
                self.assets.get_names(),  # non-reserve assets
                [1]  # equal shares
            )),
            columns=['dt', 'asset', 'value']
        ).set_index('dt')
        self.set_rebalance_proportion(df)

    def generate_trade(self, share: float, asset_from: str, asset_to: str, fee=None, metadata: str = ''):
        '''
        Generates a trade record.

        Parameters
        ----------
        share : float
            Asset's share in the portfolio to trade.
        asset_from : str
            Asset to sell.
        asset_to : str
            Asset to buy.
        fee: float or None
            Trade fee value
        metadata : str, default ''
            Trade metadata if needed.

        TODO: do we need variative share anchor? (asset/portfolio)
        '''

        return {
            'share': share,
            'from': asset_from,
            'to': asset_to,
            'fee': fee,
            'metadata': metadata
        }

    def _init_strategy(self):
        ''' Initiates the strategy. '''

        # Portfolio must include at least one asset
        assert len(self.assets.get_names('all')) > 0, 'Add at least one asset to the portfolio!'

        if not self.init_asset:
            assert len(self.assets.get_names('r')) > 0, 'Either init_asset or reserve_assets must be set up!'
            self.init_asset = self.assets.get_names('r')[0]
            logging.info(f'Set {self.init_asset} as init asset.')

        if self.asset_shares.empty:
            logging.info('Setting default (equal) rebalance proportions.')
            self.set_default_rebalance_proportion(self._start_dt)

        # Create a portfolio DataFrame
        self.portfolio = pd.DataFrame(
            {'dt': [self._start_dt], 'asset': [self.init_asset], 'share': [1.0]}
        ).set_index('dt')

    def build_portfolio(
        self,
        start_dt: str or datetime.datetime,
        end_dt: str or datetime.datetime,
        rebuild: bool = False
    ):
        '''
        Builds portfolio for a provided datetime range. Considers buy, sell and rebalance signals,
        prices, rebalance proportions, authorized assets and other parameters.
        There's no logic that create trades in the Strategy class. Strategy class always return
        blank trades even if some signals provided. That logic is supposed to be coded in a child
        class depending on a particular use case. Strategy class is a set of basic tools that are
        common for all usecases we aware of.

        Parameters
        ----------
        start_dt : str or datetime.datetime
            Datetime to compute portfolio from.
        end_dt : str or datetime.datetime
            Final portfolio datetime.
        rebuild : bool, default False
            Discard portfolio in case it's already computed for a provided timerange.
        '''

        def _recompute_asset_shares(dt, prev_dt):

            df = self.portfolio.loc[[prev_dt]]
            df = df.merge(self.prices.prices.loc[dt].reset_index(), on=['asset'])
            df['share'] = df['share'] * df['price_change']  # recompute share (so share column contains new shares)
            df['share'] = df['share'] / df['share'].sum()
            df = df[['dt', 'asset', 'share']].set_index('dt')
            if abs(df['share'].sum() - 1) > self.accuracy:
                logging.warning(f'The asset shares sum on {dt} is equal to {df["share"].sum()}'
                                ' - The prices df may contain errors.')

            self.portfolio = self.portfolio.append(df)
            self.portfolio = self.portfolio.reset_index().drop_duplicates().set_index('dt').sort_index()

        def _get_signals(dt):

            # generate rebalance signals if needed
            if hasattr(self, 'cron') and dt >= self.cron.get_current(datetime.datetime):
                self.signals.add('r', pd.DataFrame({'dt': [dt]}), signal_name='cron_rebalance')
                self.cron.get_next()

            authorized_assets = self.assets.get_authorized_assets_for_dt(dt)
            prev_dt = dt - parse_str_to_timedelta(self._granularity)

            if self.add_asset_once_authorized and dt != self._start_dt:
                # add buy signal if there's no signal already
                # assets that were not authorized on prev_dt but are authorized today and
                # dont have sell signals on a given dt:
                assets_to_add_signals_to = \
                    set(authorized_assets) \
                    - set(self.assets.get_authorized_assets_for_dt(prev_dt)) \
                    - set(self.signals.get_signals_on_dt_asset_names_only(dt=dt, signal_type='buy'))
                if len(assets_to_add_signals_to) > 0:
                    self.signals.add(
                        signal_type='buy',
                        signals_df=pd.DataFrame({
                            'dt': [dt] * len(assets_to_add_signals_to),
                            'asset': list(assets_to_add_signals_to),
                            # maybe set decision delay to 0 instead of default decision delay?
                        }),
                        signal_name='authorization_buy'
                    )

            if self.sell_assets_once_unauthorized and dt != self._start_dt:
                # add sell signals if there's no signal already
                # assets that were authorized on prev_dt but are not authorized today and
                # dont have sell signals on a given dt:
                assets_to_add_signals_to = \
                    set(self.assets.get_authorized_assets_for_dt(prev_dt)) \
                    - set(authorized_assets) \
                    - set(self.signals.get_signals_on_dt_asset_names_only(dt=dt, signal_type='sell'))
                if len(assets_to_add_signals_to) > 0:
                    self.signals.add(
                        signal_type='sell',
                        signals_df=pd.DataFrame({
                            'dt': [dt] * len(assets_to_add_signals_to),
                            'asset': list(assets_to_add_signals_to),
                        }),
                        signal_name='authorization_sell'
                    )

            return {
                'sell_signals': self.signals.get_signals_on_dt(dt, 's'),
                'buy_signals': self.signals.get_signals_on_dt(dt, signal_type='b', assets=authorized_assets),
                'rebalance_signals': self.signals.get_signals_on_dt(dt, 'r')
            }

        def _execute_trades(dt, trades):
            if len(trades) == 0:
                return

            current_portfolio = self.portfolio.loc[[dt]]
            current_portfolio = {item['asset']: item['share'] for i, item in current_portfolio.iterrows()}

            for trade in trades:
                if trade['from'] in current_portfolio and \
                   current_portfolio[trade['from']] >= (trade['share'] - self.accuracy):

                    if abs(trade['share'] - current_portfolio[trade['from']]) < self.accuracy:
                        # Remove the full asset position
                        transferred_share = current_portfolio[trade['from']]
                        del current_portfolio[trade['from']]
                    else:
                        # Remove part of the position
                        transferred_share = trade['share']
                        current_portfolio[trade['from']] -= trade['share']

                    if trade['to'] not in current_portfolio:
                        current_portfolio[trade['to']] = transferred_share
                    else:
                        current_portfolio[trade['to']] += transferred_share
                else:
                    logging.error(f'Trade can not be performed on {dt}: {trade}.'
                                  f'Portfolio structure: {current_portfolio}')
                    return

            if abs(sum(current_portfolio.values()) - 1) > self.accuracy:
                logging.warning(f'Portfolio scructure sum is {sum(current_portfolio.values())}'
                                ' - trades may contain errors')

            for trade in trades:
                self.trades_log.loc[len(self.trades_log)] = {
                    'dt': dt,
                    'order': trades.index(trade),
                    **trade
                }
            result_df = pd.DataFrame(
                {'dt': [dt]*len(current_portfolio), 'asset': list(current_portfolio.keys()), 'share': list(current_portfolio.values())}
            )
            result_df.set_index('dt', inplace=True)

            self.portfolio = self.portfolio[self.portfolio.index != dt]
            self.portfolio = self.portfolio.append(result_df).sort_index()

        if rebuild:
            # discard part of the portfolio. loc[] cant be used as start_dt should be excluded as well
            self.portfolio = self.portfolio[self.portfolio.index < start_dt]
            self.trades_log = self.trades_log[self.trades_log.index < start_dt]

        if self.portfolio.empty:
            self._init_strategy()  # init if needed

        for dt in pd.date_range(start_dt, end_dt, freq=self._granularity):

            prev_dt = dt if dt == self._start_dt else dt - parse_str_to_timedelta(self._granularity)

            if dt in self.portfolio.index and dt != self._start_dt:
                logging.warning(f'Portfolio for {dt} exists already. Skipping {dt}.')  # TODO: remove logging here??
                continue

            _recompute_asset_shares(dt, prev_dt)
            signals = _get_signals(dt)  # check if any trades needed -> check for signals
            if sum([len(x) for x in signals.values()]) > 0:
                trades = self.build_trades(dt=dt, prev_dt=prev_dt, signals=signals)
                _execute_trades(dt, trades=trades)

    def build_trades(self, **kwargs) -> list:
        '''
        Returns trades that should be executed in accodring to:
            1. provided signals
            2. previous portfolio
            3. asset_shares
            4. authorized assets
            5. other params
        That method is usually overloaded in a child class.
        '''

        return []
