import datetime
import pandas as pd
import logging
import re


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

    def __init__(
        self,
        start_dt: str or datetime,
        granularity='1D'
    ):
        '''
        TODO: add kwargs?
        TODO: add docs
        '''
        self._start_dt = str_to_ts(start_dt)
        self.end_dt = None
        self._granularity = granularity
        self.decision_delay = datetime.timedelta(days=0)

        # TODO: reindex with end_dt if provided
        assets_index = pd.date_range(start=start_dt, freq=granularity, periods=1)
        self.assets = pd.DataFrame(index=assets_index)
        self.reserve_assets = pd.DataFrame(index=assets_index)

        self.prices = pd.DataFrame(None)
        self.asset_shares = pd.DataFrame(None)

        self.buy_signals = []
        self.sell_signals = []
        self.rebalance_signals = []

        # applies both to sell and buy signals
        self.trade_reserve_assets = False

        self.default_sell_percentage = 1
        self.default_buy_percentage = 1

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
        TODO: check if provided datetimes are in self.start/self.end range

        Input assets example: {
            'ethereum': ['2021-01-01', '2022-01-02'],
            'uniswap': [2021-01-01, '2021-01-04]
            }

        Result (self.)assets: DataFrame
                    eth     uni
        dt
        2021-01-01  1       1
        2021-01-02  1       1
        2021-01-03  0       1
        2021-01-04  0       1
        '''

        def update_assets(assets, check_list, new_assets=assets, granularity=self._granularity):
            ''' Updates assets-in-the-portfolio dataFrame. '''

            for asset_name in new_assets:
                # Check if asset belongs to one and only one of (assets, reserve_assets)
                assert asset_name not in check_list, \
                    f'*{asset_name}* cant be used both as reserve and non-reserve asset!'

                # Convert datetimes
                dates = [str_to_ts(dt) for dt in new_assets[asset_name]]
                assert min(dates) >= self._start_dt, \
                    f'Provided datetime ({min(dates)}) is smaller than expected ({self._start_dt}). [{asset_name}]'

                # Add given asset to the assets list if it isn't there already
                if asset_name not in assets:
                    assets[asset_name] = False

                # If new dateranges exceed current daterange, update current daterange
                if max(dates) > max(assets.index):
                    new_index = pd.date_range(
                        start=min(dates + list(assets.index)),
                        end=max(dates + list(assets.index)),
                        freq=granularity)
                    assets = assets.reindex(assets.index.join(new_index, how='outer')).fillna(False)

                # Finally update assets in the portfolio
                assert len(dates) % 2 == 0, f'Unsupported datetime sequence for {asset_name}: odd amount of dates.'
                for i in range(int(len(dates) / 2)):
                    series_index = pd.date_range(start=dates[2 * i], end=dates[2 * i + 1], freq=granularity)
                    assets[asset_name] |= pd.Series(index=series_index, data=True)

            return assets

        if assets_type.lower() in ('r', 'reserve'):
            self.reserve_assets = update_assets(assets=self.reserve_assets, check_list=self.assets)
        else:
            self.assets = update_assets(assets=self.assets, check_list=self.reserve_assets)

    def remove_asset(self, assets: dict):
        '''Removes from reserve or non-reserve assets.

        # TODO: add complete asset removal
        '''

        def remove_assets(assets_df, exclude_asset, exclude_dates):
            dates = [str_to_ts(dt) for dt in exclude_dates]
            assert len(dates) % 2 == 0, f'Unsupported datetime sequence for {exclude_asset}: odd amount of dates.'
            for i in range(int(len(dates) / 2)):
                assets_df[exclude_asset].loc[dates[2 * i]:dates[2 * i + 1]] = False

        for asset in assets:
            if asset in self.reserve_assets:
                remove_assets(assets_df=self.reserve_assets, exclude_asset=asset, exclude_dates=assets[asset])
            elif asset in self.assets:
                remove_assets(assets_df=self.assets, exclude_asset=asset, exclude_dates=assets[asset])
            else:
                logging.warning(f'can\'t find {asset} in assets.')

    def add_signals(self, signal_type, signals_df, **kwargs):
        '''
        TODO: default signal_name (kwargs)
        TODO: default signal delay
        TODO: trade percentages
        '''

        '''
        sell / buy -> {
            'mvrv_lower': {'signals_df': signals_df, 'decision_delay': timedelta, 'trade_percentage': trade_percentage}
            ...
        }
        rebalance -> {
            'rebalance_name': {'rebalance_dts': [...], 'decision_delay': timedelta}
        }

        signals_df:
                asset   value   metadata
        dt_1     eth      ..       {}
        '''

        pass

    def remove_signals(self, signal_type, signal_name):
        pass

    def add_periodic_rebalance(self):
        '''
        TODO: cron support
        TODO: is rebalance_period field neccessary
        '''
        # self.default_rebalance_period
        pass

    def set_assets_shares(self, shares_df):
        '''
        TODO: df

                asset       share
        dt

                asset_1     asset_2 ...
        dt      <share>     <share>
        '''
        self.asset_shares = shares_df

    def build_portfolio(self, start_dt, end_dt):

        def init_strategy(self):
            self.transaction_log = pd.DataFrame(None)
            self.portfolio = pd.DataFrame(None)

            # TODO: df = generate_equal_asset_shares(assets, start_dt, end_dt)
            # self.set_assets_shares(df)
            # TODO: generate/regenerate/check and generate rebalance signals
            # TODO: other checks
            # TODO: add warning for blank asset list

        def build_trades():
            '''returns trades'''
            # TODO: maybe move to separate module

            if self.trade_reserve_assets and \
               self.structure_change_behaviour and \
               self.add_absent_assets_on_rebalance and \
               self.percentage_anchoring_to_asset:
                return default_build_trades()

        def check_signals():
            pass

        def recompute_asset_shares():
            pass

        init_strategy()

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
