'''
TODO: Do we need some constants section? (columns sets etc)
'''

import datetime
import pandas as pd
import logging
import re
import numpy as np

def convert_dt(timestamp_string, postfix=' 00:00:00'):

    if type(timestamp_string) == datetime.date:
        timestamp_string = timestamp_string.strftime('%Y-%m-%d')

    if type(timestamp_string) == datetime.datetime:
        timestamp_string = timestamp_string.strftime('%Y-%m-a%d %H:%M:%S')

    timestamp_string = timestamp_string.replace('Z', '').replace('T', ' ')
    timestamp_string = timestamp_string[:19]

    if re.match(r'\d\d\d\d-\d\d-\d\d.\d\d:\d\d:\d\d', timestamp_string):
        return timestamp_string[:10] + ' ' + timestamp_string[11:]
    elif re.match(r'\d\d\d\d-\d\d-\d\d', timestamp_string):
        return timestamp_string + postfix
    else:
        raise Exception(f"Unknown format: {timestamp_string} !")


def str_to_ts(x):
    return datetime.datetime.strptime(convert_dt(x), '%Y-%m-%d %H:%M:%S')


class Strategy:

<<<<<<< HEAD
=======
    buy_signals = pd.DataFrame(columns=['dt', 'signal', 'asset', 'trade_percantage', 'delay', 'delayed_dt'])
    sell_signals = pd.DataFrame(columns=['dt', 'signal', 'asset', 'trade_percantage', 'delay', 'delayed_dt'])
    rebalance_signals = pd.DataFrame(columns=['dt', 'signal', 'asset', 'trade_percantage', 'delay', 'delayed_dt'])
    assets = pd.DataFrame(columns=['asset'])
    reserve_assets = pd.DataFrame(columns=['asset'])
    prices = pd.DataFrame(None)
    asset_shares = pd.DataFrame(None)
    assets = pd.DataFrame(columns=['asset'])
    reserve_assets = pd.DataFrame(columns=['asset'])
    transaction_log = pd.DataFrame(None)
    portfolio = pd.DataFrame(None)

    default_trade_percantage = 1
    trade_reserve_assets = False  # applies both to sell and buy signals
    rebalance_on_sell_signals = False
    default_rebalance_period = None
    add_absent_assets_on_rebalance = False
    percentage_anchoring_to_asset = True  # percentage_anchor = 'portfolio'  # 'portfolio' or 'asset'
    structure_change_behaviour = False  # wait for signals after an asset was added or removed

>>>>>>> f198614... Resolve linter issues and conflicts
    def __init__(
        self,
        start_dt: str or datetime,
        granularity='1D'
    ):
        '''
        TODO: add kwargs?
        TODO: add docs
        '''
        self._granularity = granularity
        self._start_dt = str_to_ts(start_dt)
        self.end_dt = None
        self.decision_delay = datetime.timedelta(days=0)

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

            return assets.sort_index()

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

    def add_signals(self, signal_type, signals_df, **kwargs):
        '''
        signal_type (str): buy, b, sell, s, rebalance, r
        kwargs: desicion_delay: timedelta, signals_name: str

        ---------
        (old)
        sell / buy signals
        {
            'mvrv_lower':
                {
                    'df': signals_df,
                    'decision_delay': timedelta,
                    'trade_percentage': trade_percentage
                },
        }

        signals_df:
                asset   value   metadata
        dt_1     eth      ?       {}

        ---------

        signals_df:
        dt      asset       signal          trade_percentage        delay       delayed_dt
        10      eth         1               40                      1           11
        20      uni         2               10                      2           22

        ---------

        TODO: trigger warning in case of signal name already exists
        TODO: signals collisions (simultaneous opposite signals)
        TODO: unify signals dts with granularity
        TODO: unify columns set
        '''

        def update_signals(signals, df, **kwargs):
            if 'signals_name' in kwargs.keys():
                name = kwargs['signals_name']
            else:
                # Trying to define signals_1 as the default name
                # Find available signals_n if 'signals_1' is busy
                name = "signals_1"
                while name in signals['signal'].unique():
                    name = name.split('_')[0] + '_' + str(int(name.split('_')[1])+1)

            df['signal'] = name
            df['dt'] = df['dt'].apply(lambda x: str_to_ts(x))

            df['trade_percantage'] = df.apply(lambda x: x['trade_percantage'] \
                if 'trade_percantage' in x.keys() and isinstance(x['trade_percantage'], (float, int)) and not np.isnan(x['trade_percantage']) \
                else self.default_trade_percantage, axis=1)

            delay = kwargs['decision_delay'] if 'decision_delay' in kwargs.keys() else self.decision_delay
            df['delay'] = delay
            df['delayed_dt'] = df['dt']+delay

            return signals.append(df).reset_index(drop=True)

        df = signals_df.copy(deep=True)
        if signal_type.lower() in ('buy', 'b'):
            self.buy_signals = update_signals(self.buy_signals, df, **kwargs)

        elif signal_type.lower() in ('sell', 's'):
            self.sell_signals = update_signals(self.sell_signals, df, **kwargs)

        elif signal_type.lower() in ('rebalance', 'r'):
            self.rebalance_signals = update_signals(self.rebalance_signals, df, **kwargs)

        else:
            logging.error(f'Signal_type {signal_type} is not valid. Please provide valid signal_type')

    def remove_signals(self, signal_type, signal_name=None):
        '''
        Deletes labelled signals in case of signal_name provided
        Othervise drops all of the signals
        '''

        def update_signals(signals, signal_name):
            if signal_name:
                logging.info(f'''Deleting {len(signals[signals['signal'] == signal_name])} signals named {signal_name}''')
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

    def add_periodic_rebalance(self):
        '''
        TODO: cron support
        TODO: is rebalance_period field neccessary
        '''
        # self.default_rebalance_period
        pass

    def set_rebalance_proportion(self, proportions_df):
        '''
        TODO: should reserve asset have the same share?

        Input: proportions_df
        dt      asset       value
        10      eth         1
        10      uni         1
        10      dai         2
        15      eth         1
        15      uni         1

        Output: updated self.shares_df
        dt      asset       share
        10      eth         0.5
        10      uni         0.25
        10      dai         0.25
        15      eth         0.5
        15      uni         0.5
        '''

        if 'value' not in proportions_df.columns:
            logging.warning('`value` column name not found. Setting assets to equal shares.')
            proportions_df['value'] = 1

        # transform proportion metric into assets' shares in the portfolio
        proportions_df['share'] = proportions_df['value'] / proportions_df.groupby('dt')['value'].transform(sum)
        self.asset_shares = proportions_df[['dt', 'asset', 'share']]

    def set_default_rebalance_proportion(self, end_dt):
        '''
        Should be called inside build_portfolio().
        '''
        dates = pd.date_range(self._start_dt, end_dt, self._granularity)
        df = pd.DataFrame(
            list(itertools.product(dates, list(self.assets.asset.unique()) + list(self.reserve_assets.asset.unique()))),
            columns=['dt', 'asset']
        ).set_index('dt')
        self.set_rebalance_proportion(df)

    def init_strategy(self):
        '''
        Initiates the strategy.
        '''
        assert len(self.assets.asset.unique()) + len(self.reserve_assets.asset.unique()) > 0, \
            'Add at least one asset to the portfolio!'

        if self.asset_shares.empty:
            self.set_default_rebalance_proportion(self._start_dt)

        self.portfolio = self.asset_shares.loc[self._start_dt]

    def build_portfolio(self, start_dt, end_dt):
        '''
        Portfolio df:
                    asset       share
        dt
        2021-01-01  eth         0.5
        2021-01-01  uni         0.25
        2021-01-01  dai         0.25
        2021-01-02  eth         0.5
        2021-01-02  uni         0.5
        ...
        '''

        def build_trades():
            '''returns trades'''
            # TODO: maybe move to separate module

            if self.trade_reserve_assets and \
               self.structure_change_behaviour and \
               self.add_absent_assets_on_rebalance and \
               self.percentage_anchoring_to_asset:
                return default_build_trades()

        def check_signals():
            # TODO: check/generate rebalance signals
            # TODO: other signals checks?
            pass

        def recompute_asset_shares():
            pass

        if self.portfolio.empty:
            self.init_strategy()

        for day in pd.timedelta_range(start_dt, end_dt, self.granularity):
            # check if any trades needed -> check for signals
            signals = check_signals()
            if signals:
                trades = build_trades(day)
                recompute_asset_shares(trades=trades)
            else:
                recompute_asset_shares(trades=[])


def default_build_trades():
    pass

# 10-01 sell (delay = 2)
# --
# 12-01 sell

# 1 eth: 50% dai: 50%

# -2-
# signal: sell eth (...)          ['eth', 'dai'] -> ['dai', 'uni'], {'dai': 75%, 'uni': 25%}
#     trx: eth(50%) -> dai(25%) + uni(25%)

# update_portfolio:
#     dai: 75%, uni: 25%

# -3-
# signal: ...
#     trx: ...

#     ...
