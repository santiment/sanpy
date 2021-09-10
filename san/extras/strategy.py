import datetime
import pandas as pd


class Strategy:

    assets = {}
    reserve_assets = {}

    def __init__(
        self,
        start_dt: str or datetime,
        assets: list = [],
        reserve_assets: list = [],
    ):
        '''
        TODO: add kwargs
        TODO: add docs
        '''
        self._start_dt = start_dt
        self.end_dt = None
        self._granularity = '1D'
        self.decision_delay = datetime.timedelta(days=0)

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
        kwargs: start_dt, end_dt
        TODO: custom start/end dts
        TODO: check if asset in reserve AND non-reserve assets
        TODO: introduce breaks in assets: dataframes instead of series
        TODO: check if provided datetimes are in self.start/self.end range
        TODO: test series performance and memory usage

        Input assets example: {
            'ethereum': ['2021-01-01', '2022-01-01'],
            'uniswap': [2021-01-01, '2021-06-01]
            }

        Result (self.)assets example: {
            'ethereum': pd.Series(),
            'uniswap': pd.Series()
            }
        '''

        def update_assets(assets, new_assets, granularity):
            for asset_name in new_assets:
                dates = new_assets[asset_name]
                assets[asset_name] = pd.date_range(start=dates[0], end=dates[1], freq=granularity)

        if assets_type.lower() in ('r', 'reserve'):
            update_assets(self.reserve_assets, new_assets=assets, granularity=self._granularity)
        else:
            update_assets(self.assets, new_assets=assets, granularity=self._granularity)

    def remove_asset(self, asset_name, **kwargs):
        '''
        remove from reserve or non-reserve assets
        '''
        pass

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
