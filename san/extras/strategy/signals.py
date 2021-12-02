import logging
import datetime
import pandas as pd

from san.extras.utils import str_to_ts


_shared_error_msg = 'Signal_type {} is not valid. Please provide valid signal_type'


class Signals:
    '''
    Signals management tool.

    Signal is an event that happens in a certain point in time. In general case
    the signal could be represented by a set of datetimes. A signal could
    correspond to a particular asset or to a few assets.

    Signals are interpreted in a 3 different ways:
    1. Buy-signals
        Buy-signal an instruction to buy a particluar asset. E.g. include a
        particular asset in the portfolio. In general case, increase asset's
        share in the portfolio.
    2. Sell-signals
        Sell-signal an instruction to sell a particluar asset. E.g. exclude a
        particular asset from the portfolio. In general case, decrease
        asset's share in the portfolio.
    3. Rebalance-signals
        Rebalance-signals leads to some changes in the portfolio structure.
        These changes may or may not lead to including an asset or complete
        asset excluding from the portfolio.
    '''

    _default_signals_df = pd.DataFrame(columns=['dt', 'signal', 'asset', 'trade_percantage', 'decision_delay'])

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
        self.default_trade_percantage = 1

        self.buy_signals = self._default_signals_df.copy()
        self.sell_signals = self._default_signals_df.copy()
        self.rebalance_signals = self._default_signals_df.copy()

    def add(self, signal_type: str, signals_df: pd.DataFrame, signal_name: str or None = None):
        '''
        Parameters
        ----------
        signal_type : str, one of ['buy', 'b', 'sell', 's', 'rebalance', 'r']
            How to interpret a provided signals.
        signals_df : pd.DataFrame
            The signals df main contain only 'dt' and 'asset' columns in case of
            buy/sell signals or 'dt' only in case of rebalance signals.
            Example:
            dt                      signal      asset       trade_percantage    desicion_delay
            2021-01-01 00:00:00     mvrv_lower  ethereum    0.3                 3 days (datetime.timedelta)
            2021-02-01 13:00:00     mvrv_lower  uniswap     0.2                 3 days
        signals_name : str or None, default None
            Signals_name will be generated and remaining columns will be filled with default values.

        TODO: signals collisions, repeating (probably should be resolved on the step of signals fetching)
        TODO: unify columns set
        '''

        def _update_signals(signals: pd.DataFrame, df: pd.DataFrame, signal_name: str or None = None):
            if not signal_name:
                # Set up a default signal's name if not provided.
                # Try to define signals_1 as the default name.
                # Find available signals_n if 'signals_1' is busy.
                signal_name = "signals_1"
                while signal_name in signals['signal'].unique():
                    signal_name = signal_name.split('_')[0] + '_' + str(int(signal_name.split('_')[1]) + 1)

            df['signal'] = signal_name
            df['dt'] = df['dt'].apply(lambda x: str_to_ts(x))

            if 'trade_percantage' not in df.columns:
                df['trade_percantage'] = self.default_trade_percantage

            if 'decision_delay' not in df.columns:
                df['decision_delay'] = self.decision_delay

            df['delayed_dt'] = df['dt'] + df['decision_delay']

            df.set_index('delayed_dt', inplace=True)
            df.set_index(df.index.ceil(freq=self._granularity), inplace=True)

            # df = df['dt', 'signal', 'asset', 'decision_delay', 'trade_percantage']
            return signals.append(df)

        df = signals_df.copy()
        if signal_type.lower() in ('buy', 'b'):
            self.buy_signals = _update_signals(self.buy_signals, df, signal_name)
        elif signal_type.lower() in ('sell', 's'):
            self.sell_signals = _update_signals(self.sell_signals, df, signal_name)
        elif signal_type.lower() in ('rebalance', 'r'):
            self.rebalance_signals = _update_signals(self.rebalance_signals, df, signal_name)
        else:
            logging.error(_shared_error_msg.format(signal_type))  # Raise error instead of logging.error?

    def remove(self, signal_type: str, signal_name: str or None = None):
        '''
        Deletes labelled signals in case of signal_name provided
        Othervise drops all of the signals
        '''

        def _update_signals(signals: pd.DataFrame, signal_name: str or None):
            if signal_name:
                logging.info(f'Deleting {len(signals[signals["signal"] == signal_name])} signals named {signal_name}')
                return signals[~(signals['signal'] == signal_name)]
            else:
                logging.info(f'''Deleting {len(signals)} signals''')
                return signals.drop(index=signals.index)  # delete all signals of a given type

        if signal_type.lower() in ('buy', 'b'):
            self.buy_signals = _update_signals(self.buy_signals, signal_name)
        elif signal_type.lower() in ('sell', 's'):
            self.sell_signals = _update_signals(self.sell_signals, signal_name)
        elif signal_type.lower() in ('rebalance', 'r'):
            self.rebalance_signals = _update_signals(self.rebalance_signals, signal_name)
        else:
            logging.error(_shared_error_msg.format(signal_type))

    def get_signals_on_dt(self, dt: str, signal_type: str, assets: list = []):
        '''
        Returns signals that were fired on a provided dt. Decision_delay is taken into account.
        '''

        def _get_signals_on_dt_or_empty(signals_df, dt, assets):
            if dt in signals_df.index:
                if assets:
                    return signals_df[(signals_df['asset'].isin(assets)) & (signals_df.index == dt)]
                return signals_df.loc[[dt]]
            return self._default_signals_df.copy()  # blank df

        if signal_type.lower() in ('buy', 'b'):
            return _get_signals_on_dt_or_empty(self.buy_signals, dt, assets)
        elif signal_type.lower() in ('sell', 's'):
            return _get_signals_on_dt_or_empty(self.sell_signals, dt, assets)
        elif signal_type.lower() in ('rebalance', 'r'):
            return _get_signals_on_dt_or_empty(self.rebalance_signals, dt, assets)
        logging.error(_shared_error_msg.format(signal_type))

    def get_signals_on_dt_asset_names_only(self, dt: str, signal_type: str, assets: list = []):
        '''
        Returns asset names that have signals on a provided dt. Decision_delay is taken into account.
        '''
        signals = self.get_signals_on_dt(dt, signal_type, assets)
        return list(signals['asset'].unique())
