import logging
import datetime
import itertools
import pandas as pd
from croniter import croniter

from san.extras.utils import str_to_ts, parse_str_to_timedelta

pd.options.mode.chained_assignment = None


class Strategy:

    buy_signals = pd.DataFrame(columns=['dt', 'signal', 'asset', 'trade_percantage', 'decision_delay'])
    sell_signals = pd.DataFrame(columns=['dt', 'signal', 'asset', 'trade_percantage', 'decision_delay'])
    rebalance_signals = pd.DataFrame(columns=['dt', 'signal', 'asset', 'trade_percantage', 'decision_delay'])
    assets = pd.DataFrame(columns=['asset'])
    reserve_assets = pd.DataFrame(columns=['asset'])
    prices = pd.DataFrame(columns=['dt', 'asset', 'price', 'price_change']).set_index('dt')
    asset_shares = pd.DataFrame(None)
    trades_log = pd.DataFrame(columns=['dt', 'share', 'from', 'to', 'metadata'])
    portfolio = pd.DataFrame(None)
    default_trade_percantage = 1

    accuracy = 3*10**(-6)

    def __init__(
        self,
        start_dt: str or datetime,
        end_dt: str or datetime or None = None,
        granularity: str = '1D',
        decision_delay: int = 0,
        init_asset: str or None = None,

    ):
        self._granularity = granularity
        self._start_dt = str_to_ts(start_dt)
        self.end_dt = end_dt
        self.decision_delay = datetime.timedelta(seconds=decision_delay)
        self.init_asset = init_asset

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

            return assets.reset_index().drop_duplicates().set_index('index').sort_index()

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

    def add_signals(self, signal_type: str, signals_df: pd.DataFrame, signal_name: str or None = None):
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

    def remove_signals(self, signal_type: str, signal_name: str or None = None):
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

    def add_periodic_rebalance(self, cron_expr: str, skip_rebalance_on_init: bool = True):
        '''
        TODO: how to skip first rebalance?
        '''
        self.cron = croniter(cron_expr, self._start_dt)
        if skip_rebalance_on_init:
            self.cron.get_next()

    def set_rebalance_proportion(self, proportions_df: pd.DataFrame):
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

    def compute_asset_shares_for_dt(self, dt: datetime.datetime, assets: list = []):
        ''' Computes rebalance proportions.'''

        if dt not in self.asset_shares.index:
            logging.warning(f'Assets shares are missing for {dt}. The shares will be set to 1.')
            self.set_rebalance_proportion(pd.DataFrame({'dt': dt, 'asset': assets, 'value': 1.0}).set_index('dt'))

        df = self.asset_shares.loc[[dt]]
        if assets:
            df = df[df['asset'].isin(assets)]

        df['share'] = df['value'] / df['value'].sum()
        return df[['asset', 'share']]

    def __set_default_rebalance_proportion(self, end_dt: datetime.datetime):
        '''
        Should be called inside build_portfolio().
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

    def set_prices(self, price_df: pd.DataFrame):
        '''
        TODO: check price gaps

        price df:
                    asset       price       price_change
        dt
        2021-01-01  eth         4000        1
        2021-01-01  dai         1           1
        2021-01-02  eth         4100        1.025
        2021-01-02  dai         1           1
        '''
        if not isinstance(price_df.index, pd.DatetimeIndex):
            price_df.index = pd.DatetimeIndex(price_df.index)
        # compute price multiplier as 1 + (x[t] - x[t-1]) / x[t]
        # fillna with 1 - normally Nan-s appear only at self._start_dt. When strategy initiation starts we have to
        # recompute asset shares in the portfolio according to price changes. But on the first day prices cant
        # change in comparison to init dt so the price change is 1.
        price_df['price_change'] = price_df.groupby('asset').transform(
            lambda x: 1 + pd.DataFrame.pct_change(x)).fillna(1)
        self.prices = self.prices.append(price_df)  # append new prices
        # remove duplicated records. In case of duplicates leave last value. Leaving last value makes
        # possible prices updates - just set new prices.
        self.prices = self.prices.groupby(['dt', 'asset']).last().reset_index('asset').sort_index()

    def genetate_trade(self, share, asset_from, asset_to, metadata=''):
        '''
        # TODO: do we need variative share anchor? (asset/portfolio)
        '''
        return {
            'share': share,
            'from': asset_from,
            'to': asset_to,
            'metadata': metadata
        }

    def init_strategy(self):
        '''
        Initiates the strategy.
        '''
        assert len(self.assets.asset.unique()) + len(self.reserve_assets.asset.unique()) > 0, \
            'Add at least one asset to the portfolio!'

        if not self.init_asset:
            assert len(self.reserve_assets.asset.unique()) > 0, 'Either init_asset or reserve_assets must be set up!'
            init_asset = self.reserve_assets.asset.unique()[0]
            logging.info(f'Setting {init_asset} as init asset.')
            self.init_asset = init_asset

        if self.asset_shares.empty:
            logging.info('Setting default (equal) rebalance proportions.')
            self.__set_default_rebalance_proportion(self._start_dt)

        self.portfolio = pd.DataFrame(
            {'dt': [self._start_dt], 'asset': [self.init_asset], 'share': [1.0]}
        ).set_index('dt')

    def build_portfolio(self, start_dt: str or datetime.datetime, end_dt: str or datetime.datetime, rebuild=False):
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
            df = self.portfolio.loc[prev_dt]
            if isinstance(df, pd.Series):
                df = pd.DataFrame(df).T
            df = df.merge(self.prices.loc[dt].reset_index(), on=['asset'])
            df['share'] = df['share'] * df['price_change']  # recompute share (so share column contains new shares)
            df['share'] = df['share'] / df['share'].sum()
            df = df[['dt', 'asset', 'share']].set_index('dt')
            if abs(df['share'].sum() -1) > 2*self.accuracy:
                logging.warning(f'The asset shares sum on {dt} is equal to {df["share"].sum()} - The prices df may contain errors.')
            self.portfolio = self.portfolio.append(df)
            self.portfolio = self.portfolio.reset_index().drop_duplicates().set_index('dt').sort_index()

        def get_current_signals(dt, signals, assets_check=False):
            if dt not in signals.index:
                return ''
            if assets_check:
                return '' if dt not in self.assets.index else signals[signals['asset'].isin(self.assets.loc[[dt]]['asset'])].loc[[dt]]
            return signals.loc[[dt]]

        def check_signals(dt):
            '''
            TODO: other signals checks?
            TODO: also check for asset shares!
            '''
            # check/generate rebalance signals
            if hasattr(self, 'cron') and dt >= self.cron.get_current(datetime.datetime):
                self.add_signals('r', pd.DataFrame({'dt': [dt]}), signal_name='cron_rebalance')
                self.cron.get_next()

            signals = {
                'sell_signals': get_current_signals(dt, self.sell_signals),
                'buy_signals': get_current_signals(dt, self.buy_signals, True),
                'rebalance_signals': get_current_signals(dt, self.rebalance_signals),
            }
            return signals

        def execute_trades(dt, trades):
            if len(trades) == 0:
                return

            current_portfolio = self.portfolio.loc[[dt]]
            current_portfolio = {item['asset']: item['share'] for i, item in current_portfolio.iterrows()}

            for trade in trades:
                if trade['from'] in current_portfolio and current_portfolio[trade['from']] >= (trade['share'] - self.accuracy):

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
                    logging.error(f'Trade can not be performed on {dt}: {trade}. Portfolio structure: {current_portfolio}')
                    return

            if abs(sum(current_portfolio.values()) - 1) > 2*self.accuracy:
                logging.warning(f'Portfolio scructure sum is {sum(current_portfolio.values())} - trades may contain errors')

            for trade in trades:
                self.trades_log.loc[len(self.trades_log)] = {
                    'dt': dt,
                    **trade
                }
            result_df = pd.DataFrame({'dt': dt, 'asset': list(current_portfolio.keys()), 'share': list(current_portfolio.values())})
            result_df.set_index('dt', inplace=True)
            self.portfolio = self.portfolio[self.portfolio.index != dt]

            self.portfolio = self.portfolio.append(result_df).sort_index()

        if rebuild:
            # discard part of the portfolio. loc[] cant be used as start_dt should be excluded as well
            self.portfolio = self.portfolio[self.portfolio.index < start_dt]

        if self.portfolio.empty:
            self.init_strategy()  # init if needed

        for dt in pd.date_range(start_dt, end_dt, freq=self._granularity):

            prev_dt = dt if dt == self._start_dt else dt - parse_str_to_timedelta(self._granularity)

            if dt in self.portfolio.index and dt != self._start_dt:
                logging.warning(f'Portfolio for {dt} exists already. Skipping {dt}.')  # TODO: remove logging here??
                continue

            recompute_asset_shares(dt, prev_dt)
            signals = check_signals(dt)  # check if any trades needed -> check for signals
            if sum([len(x) for x in signals.values()]) > 0:
                trades = self.build_trades(dt, prev_dt, signals)
                execute_trades(dt, trades=trades)

    def build_trades(self, dt, prev_dt, signals, **kwargs):
        '''
        That method must be redefined in a child class
        '''
        pass

        return []
