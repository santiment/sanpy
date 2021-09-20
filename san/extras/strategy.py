import logging
import datetime
import itertools
import pandas as pd
from croniter import croniter

from san.extras.utils import str_to_ts, pairwise


class Strategy:

    buy_signals = pd.DataFrame(columns=['dt', 'signal', 'asset', 'trade_percantage', 'decision_delay'])
    sell_signals = pd.DataFrame(columns=['dt', 'signal', 'asset', 'trade_percantage', 'decision_delay'])
    rebalance_signals = pd.DataFrame(columns=['dt', 'signal', 'asset', 'trade_percantage', 'decision_delay'])
    assets = pd.DataFrame(columns=['asset'])
    reserve_assets = pd.DataFrame(columns=['asset'])
    prices = pd.DataFrame(columns=['dt', 'asset', 'price', 'price_change']).set_index('dt')
    asset_shares = pd.DataFrame(None)
    transaction_log = pd.DataFrame(None)
    portfolio = pd.DataFrame(None)

    rebalance_on_sell_signals = False

    # default_trade_percantage = 1
    # trade_reserve_assets = False  # applies both to sell and buy signals
    # add_absent_assets_on_rebalance = False
    # percentage_anchoring_to_asset = True  # percentage_anchor = 'portfolio'  # 'portfolio' or 'asset'
    # structure_change_behaviour = False  # wait for signals after an asset was added or removed

    def __init__(
        self,
        start_dt: str or datetime,
        end_dt: str or datetime or None = None,
        granularity: str = '1D',
        decision_delay: int = 0
    ):
        self._granularity = granularity
        self._start_dt = str_to_ts(start_dt)
        self.end_dt = end_dt
        self.decision_delay = datetime.timedelta(seconds=decision_delay)

        # TODO: reindex with end_dt if provided
        assets_index = pd.date_range(start=start_dt, freq=granularity, periods=1)
        self.assets = pd.DataFrame(index=assets_index)
        self.reserve_assets = pd.DataFrame(index=assets_index)

        self.prices = pd.DataFrame(None)
        self.asset_shares = pd.DataFrame(None)

        self.buy_signals = pd.DataFrame(columns=['dt', 'signal', 'asset', 'trade_percantage', 'delay', 'delayed_dt'])
        self.sell_signals = pd.DataFrame(columns=['dt', 'signal', 'asset', 'trade_percantage', 'delay', 'delayed_dt'])
        self.rebalance_signals = pd.DataFrame(columns=['dt', 'signal', 'asset', 'trade_percantage', 'delay', 'delayed_dt'])

        # applies both to sell and buy signals
        self.trade_reserve_assets = False

        self.default_sell_percentage = 1
        self.default_buy_percentage = 1
        self.default_trade_percantage = 1

        self.rebalance_on_sell_signals = False
        self.default_rebalance_period = None

        self.add_absent_assets_on_rebalance = False
        # self.percentage_anchor = 'portfolio'  # 'portfolio' or 'asset' ->
        self.percentage_anchoring_to_asset = True

        # wait for signals after an asset was added or removed
        self.structure_change_behaviour = False

    def add_assets(self, assets_type: str, assets: dict):
        '''
        TODO: default start/end dts
        TODO: check if asset in reserve AND non-reserve assets in the same time only
        TODO: check if provided datetimes are in self.start - self.end range
        TODO: maybe add self.asset_names, self.reserve_asset_names

        Input assets example: {
            'ethereum': ['2021-01-01', '2022-01-02'],
            'uniswap': [2021-01-01, '2021-01-03]
            }
        Result (self.)assets: DataFrame
                    asset
        dt
        2021-01-01  eth
        2021-01-01  uni
        2021-01-02  eth
        2021-01-02  uni
        2021-01-03  uni
        '''

        def update_assets(assets, new_assets, granularity=self._granularity):
            ''' Updates assets-in-the-portfolio dataFrame. '''
            for asset_name in new_assets:
                # Convert and test datetimes
                dates = [str_to_ts(dt) for dt in new_assets[asset_name]]
                assert min(dates) >= self._start_dt, \
                    f'Provided datetime ({min(dates)}) is smaller than expected ({self._start_dt}). [{asset_name}]'
                assert len(dates) % 2 == 0, f'Unsupported datetime sequence for {asset_name}: odd amount of dates.'

                # Update assets in the portfolio
                for i in range(int(len(dates) / 2)):
                    assets = assets.append(pd.DataFrame(
                        index=pd.date_range(start=dates[2 * i], end=dates[2 * i + 1], freq=granularity),
                        data={'asset': asset_name}
                    ))

            return assets[~(assets.index.duplicated() & assets.duplicated())].sort_index()

        def test_asset_name(new_assets, assets):
            ''' Check if asset belongs to one and only one of (assets, reserve_assets).'''
            assets_names = set(assets['asset'].unique())  # works faster than set(assets['asset']) when len(df) is big
            for asset_name in new_assets:
                assert asset_name not in assets_names, \
                    f'*{asset_name}* cant be used both as reserve and non-reserve asset!'

        if assets_type.lower() in ('r', 'res', 'reserve'):
            test_asset_name(new_assets=assets, assets=self.assets)
            self.reserve_assets = update_assets(assets=self.reserve_assets, new_assets=assets)
        else:
            test_asset_name(new_assets=assets, assets=self.reserve_assets)
            self.assets = update_assets(assets=self.assets, new_assets=assets)

    def remove_assets(self, assets: dict):
        '''Removes assets from reserve or non-reserve assets.

        # TODO: add complete asset removal
        # TODO: maybe add self.clear_assets()
        '''

        def remove_assets(assets_df, exclude_asset, exclude_dates, granularity=self._granularity):
            dates = [str_to_ts(dt) for dt in exclude_dates]
            assert len(dates) % 2 == 0, f'Unsupported datetime sequence for {exclude_asset}: odd amount of dates.'

            for i in range(int(len(dates) / 2)):
                exclude_dates = list(pd.date_range(start=dates[2 * i], end=dates[2 * i + 1], freq=granularity))
                assets_df = assets_df[
                    ~((assets_df.index.isin(exclude_dates)) & (assets_df['asset'] == exclude_asset))
                ]
            return assets_df

        asset_names = set(self.assets['asset'].unique())
        reserve_asset_names = set(self.reserve_assets['asset'].unique())
        for asset in assets:
            if asset in asset_names:
                self.assets = remove_assets(
                    assets_df=self.assets, exclude_asset=asset, exclude_dates=assets[asset])
            elif asset in reserve_asset_names:
                self.reserve_assets = remove_assets(
                    assets_df=self.reserve_assets, exclude_asset=asset, exclude_dates=assets[asset])
            else:
                logging.warning(f'can\'t find {asset} in assets.')

    def add_signals(self, signal_type, signals_df, signal_name=None):
        '''
        signal_type: 'buy', 'b', 'sell', 's', 'rebalance', 'r'

        Input DataFrame example:

        dt                      signal      asset       trade_percantage        desicion_delay
        2021-01-01 00:00:00     mvrv_lower  ethereum    0.3                     3 days (datetime.timedelta)
        2021-02-01 13:00:00     mvrv_lower  uniswap     0.2                     3 days

        The signals df main contain only 'dt' and 'asset' columns in case of buy/sell
        signals or 'dt' in case of rebalance signals.
        The signals_name will be generated and remaining columns will be filled with default values.

        TODO: signals collisions, repeating (probably should be resolved on the step of signals fetching)
        TODO: unify columns set
        '''

        def update_signals(signals, df, signal_name):
            if not signal_name:
                # Trying to define signals_1 as the default name
                # Find available signals_n if 'signals_1' is busy
                signal_name = "signals_1"
                while signal_name in signals['signal'].unique():
                    signal_name = signal_name.split('_')[0] + '_' + str(int(signal_name.split('_')[1])+1)

            df['signal'] = signal_name
            df['dt'] = df['dt'].apply(lambda x: str_to_ts(x))

            if 'trade_percantage' not in df.columns:
                df['trade_percantage'] = self.default_trade_percantage

            if 'decision_delay' not in df.columns:
                df['decision_delay'] = self.decision_delay

            df['delayed_dt'] = df['dt']+df['decision_delay']

            df.set_index('delayed_dt', inplace=True)
            df.set_index(df.index.ceil(freq=self._granularity), inplace=True)

            # df = df['dt', 'signal', 'asset', 'decision_delay', 'trade_percantage']
            return signals.append(df)

        df = signals_df.copy(deep=True)
        if signal_type.lower() in ('buy', 'b'):
            self.buy_signals = update_signals(self.buy_signals, df, signal_name)

        elif signal_type.lower() in ('sell', 's'):
            self.sell_signals = update_signals(self.sell_signals, df, signal_name)

        elif signal_type.lower() in ('rebalance', 'r'):
            self.rebalance_signals = update_signals(self.rebalance_signals, df, signal_name)

        else:
            logging.error(f'Signal_type {signal_type} is not valid. Please provide valid signal_type')

    def remove_signals(self, signal_type, signal_name=None):
        '''
        Deletes labelled signals in case of signal_name provided
        Othervise drops all of the signals
        '''

        def update_signals(signals, signal_name):
            if signal_name:
                logging.info(f'Deleting {len(signals[signals["signal"] == signal_name])} signals named {signal_name}')
                return signals[~(signals['signal'] == signal_name)]
            else:
                logging.info(f'''Deleting {len(signals)} signals''')
                return signals.drop(index=signals.index)

        if signal_type.lower() in ('buy', 'b'):
            self.buy_signals = update_signals(self.buy_signals, signal_name)
        elif signal_type.lower() in ('sell', 's'):
            self.sell_signals = update_signals(self.sell_signals, signal_name)
        elif signal_type.lower() in ('rebalance', 'r'):
            self.rebalance_signals = update_signals(self.rebalance_signals, signal_name)
        else:
            logging.error(f'Signal_type {signal_type} is not valid. Please provide valid signal_type')

    def add_periodic_rebalance(self, cron_expr: str, skip_first_rebalance=False):
        '''
        '''
        self.cron = croniter(cron_expr, self._start_dt)
        self.cron.get_next()
        if skip_first_rebalance:
            self.cron.get_next()

    def set_rebalance_proportion(self, proportions_df):
        '''
        Input: proportions_df
        dt              asset       value
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

    def compute_asset_shares_for_dt(self, dt, assets=[]):
        ''' Computes rebalance proportions.'''
        df = self.asset_shares.loc[dt]
        if assets:
            df = df[df['asset'].isin(assets)]

        df['share'] = df['value'] / df['value'].sum()
        return df[['asset', 'share']]

    def __set_default_rebalance_proportion(self, end_dt):
        '''
        Should be called inside build_portfolio().
        # TODO: when setting equal asset shares consider assets availability (self.assets)
        '''
        df = pd.DataFrame(
            list(itertools.product(
                pd.date_range(self._start_dt, end_dt, freq=self._granularity),  # dates
                list(self.assets.asset.unique()) + list(self.reserve_assets.asset.unique()),  # all available assets
                [1]  # equal shares
            )),
            columns=['dt', 'asset', 'value']
        ).set_index('dt')
        self.set_rebalance_proportion(df)

    def set_prices(self, price_df):
        '''
        TODO: check price gaps

        price df:
                    asset       price       price_change
        dt
        2021-01-01  eth         4000        NaN
        2021-01-01  dai         1           NaN
        2021-01-02  eth         4100        1.025
        2021-01-02  dai         1           1
        '''
        if not isinstance(price_df.index, pd.DatetimeIndex):
            price_df.index = pd.DatetimeIndex(price_df.index)
        # compute price multiplier as 1 + (x[t] - x[t-1]) / x[t]
        price_df['price_change'] = price_df.groupby('asset').transform(lambda x: 1 + pd.DataFrame.pct_change(x))
        # append new prices
        self.prices = self.prices.append(price_df)
        # remove duplicated records. In case of duplicates leave last value. Leaving last value makes
        # possible prices updates - just set new prices.
        self.prices = self.prices.groupby(['dt', 'asset']).last().reset_index('asset').sort_index()

    def init_strategy(self):
        '''
        Initiates the strategy.
        '''
        assert len(self.assets.asset.unique()) + len(self.reserve_assets.asset.unique()) > 0, \
            'Add at least one asset to the portfolio!'

        if self.asset_shares.empty:
            self.__set_default_rebalance_proportion(self._start_dt)

        self.portfolio = self.compute_asset_shares_for_dt(self._start_dt)

    def build_portfolio(self, start_dt, end_dt, rebuild=False):
        '''
        Portfolio df:
                    asset       share
        dt
        2021-01-01  eth         0.5
        2021-01-01  uni         0.25
        2021-01-01  dai         0.25
        2021-01-02  eth         0.5
        2021-01-02  uni         0.5...
        '''

        def recompute_asset_shares(dt, prev_dt):
            '''TODO: add docs'''
            df = self.portfolio.loc[prev_dt].merge(self.prices.loc[dt].reset_index(), on=['asset'])
            df['share'] = df['share'] * df['price_change']  # recompute share (so share column contains new shares)
            df['share'] = df['share'] / df['share'].sum()
            df = df[['dt', 'asset', 'share']].set_index('dt')
            self.portfolio = self.portfolio.append(df)

        def check_signals(dt):
            '''
            TODO: other signals checks?
            TODO: also check for asset shares!
            '''
            # check/generate rebalance signals
            if dt >= self.get_current(datetime.datetime):
                self.add_signals('r', pd.DataFrame({'dt': [dt]}), signal_name='cron_rebalance')
                self.cron.get_next()

        def execute_trades():
            pass

        if rebuild:
            # discard part of the portfolio. loc[] cant be used as start_dt should be excluded as well
            self.portfolio = self.portfolio[self.portfolio.index < start_dt]

        if self.portfolio.empty:
            self.init_strategy()  # init if needed

        for prev_dt, dt in pairwise(pd.date_range(start_dt, end_dt, freq=self._granularity)):

            if dt == self._start_dt:
                # Initial portfolio must be computed with init_strategy(). Most probably it's already computed.
                continue
            if dt in self.portfolio.index:
                logging.warning(f'Portfolio for {dt} exists already. Skipping {dt}.')  # TODO: remove logging here??
                continue

            recompute_asset_shares(dt, prev_dt)
            signals = check_signals()  # check if any trades needed -> check for signals
            if signals:
                trades = self.build_trades(dt, signals)
                execute_trades(trades=trades)

    def build_trades(self, **kwargs):
        '''
        That method must be redefined in a child class
        '''
        return []
