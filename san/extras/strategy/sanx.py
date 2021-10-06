import logging

from san.extras.strategy.strategy import Strategy


class SanX(Strategy):

    def build_trades(self, dt, prev_dt, signals, **kwargs):
        '''
        # TODO : multiple reserve assets (may be provided via parent class)
        '''

        reserve_asset = self.assets.get_authorized_assets_for_dt(dt, 'r')
        if len(reserve_asset) == 0 or len(reserve_asset) > 1:
            logging.warning('The strategy requires a single reserve asset.')
            return []

        reserve_asset = reserve_asset[0]

        current_portfolio = self.portfolio[self.portfolio['share'] > 0].loc[[dt]]

        current_portfolio = {item['asset']: item['share'] for i, item in current_portfolio.iterrows()}
        trades = []

        # Ignore signals on assets if they have both buy and sell signals
        if len(signals['sell_signals']) > 0 and len(signals['buy_signals']) > 0:
            assets_both = [el for el in signals['sell_signals']['asset'] if el in signals['buy_signals']['asset']]
            signals['sell_signals'] = signals['sell_signals'][~signals['sell_signals']['asset'].isin(assets_both)]
            signals['buy_signals'] = signals['buy_signals'][~signals['buy_signals']['asset'].isin(assets_both)]

        # Ignore buy signals of assets which are already in portfolio
        if len(signals['buy_signals']) > 0:
            signals['buy_signals'] = \
                signals['buy_signals'][~signals['buy_signals']['asset'].isin(list(current_portfolio))]

        # Ignore removing of assets which are missing in the existing portfolio
        if len(signals['sell_signals']) > 0:
            signals['sell_signals'] = \
                signals['sell_signals'][signals['sell_signals']['asset'].isin(list(current_portfolio))]

        # Check if the valid signals remain
        if len(signals['buy_signals']) + len(signals['sell_signals']) + len(signals['rebalance_signals']) == 0:
            return []

        to_remove = list(signals['sell_signals']['asset'].unique()) if len(signals['sell_signals']) > 0 else []
        to_add = list(signals['buy_signals']['asset'].unique()) if len(signals['buy_signals']) > 0 else []

        if reserve_asset in current_portfolio:
            new_portfolio_assets = [asset for asset in to_add if asset not in to_remove]
        else:
            new_portfolio_assets = [asset for asset in list(current_portfolio) + to_add if asset not in to_remove]

        new_portfolio_asset_shares = self.compute_asset_shares_for_dt(dt, new_portfolio_assets)
        new_portfolio_asset_shares = {
            item['asset']: item['share'] for index, item in new_portfolio_asset_shares.iterrows()}

        # New asset has to be added or the rebalance signal appeared (if we have what we want to rebalance)
        if len(to_add) > 0 or (len(signals['rebalance_signals']) > 0 and len(current_portfolio) > 1):
            for asset in current_portfolio:
                if asset != reserve_asset:
                    trades.append(self.generate_trade(current_portfolio[asset], asset, reserve_asset))

            for asset in new_portfolio_asset_shares:
                trades.append(self.generate_trade(new_portfolio_asset_shares[asset], reserve_asset, asset))

        # No new assets or rebalance signals while sell-signal exists
        elif len(to_add) == 0 and len(signals['rebalance_signals']) == 0 and len(to_remove) > 0:
            sold_share = 0
            for asset in to_remove:
                trades.append(self.generate_trade(current_portfolio[asset], asset, reserve_asset))
                sold_share += current_portfolio[asset]

            for asset in new_portfolio_assets:
                trades.append(self.generate_trade(sold_share*new_portfolio_asset_shares[asset], reserve_asset, asset))

        return trades
