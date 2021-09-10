from datetime import datetime
import pandas as pd


class Strategy:

    def __init__(
        self,
        start_dt: str or datetime,
        assets: list = [],
        reserve_assets: list = [],
    ):
        self.start_dt = start_dt
        self.end_dt = None
        self.granularity = datetime.timedelta(days=1)

        self.assets = assets
        # Example: {'ethereum': [{'start_dt': 10, 'end_dt': 15}]}
        self.reserve_assets = reserve_assets

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
        self.percentage_anchor = 'portfolio'  # 'portfolio' or 'asset'

        # wait for signals after an asset was added or removed
        self.structure_change_behaviour = False

    def add_periodic_rebalance(self):
        pass

    def init_strategy(self):
        self.transaction_log = pd.DataFrame(None)
        self.portfolio = pd.DataFrame(None)

    def add_asset(self, assets_type, asset_name, **kwargs):

        def update_assets(assets, new_asset_name, **kwargs):
            pass

        if assets_type == 'reserve':
            update_assets(self.reserve_assets, new_asset_name=asset_name, **kwargs)
        else:
            update_assets(self.assets, new_asset_name=asset_name, **kwargs)


# TODO:

# remove_asset()

# add_signals(self, signal_type, signal_name, signals_df)
# remove_signals(self, signal_type, signal_name)
# show_signal_names(self, signal_type)
# show_signals(self, signal_type, signal_name)

# add_periodic_rebalance(self, priod)

# set_assets_shares(self, shares_df)
# show_assets_shares()

# init_strategy(self, init_option)
# build_portfolio(self, start_date, end_date)
#     -generate_rebalance_signals()
#     -update_portfolio()
#     -build_trades(): update: self.transaction_log()
