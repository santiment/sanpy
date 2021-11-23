import datetime
import pandas as pd

from san.extras.utils import str_to_ts, resample_dataframe


class Prices:
    '''
    Prices management tool.

    Prices are stored in a pd.DataFrame as follows:
                asset       price       price_change
    dt
    2021-01-01  eth         4000        1
    2021-01-01  dai         1           1
    2021-01-02  eth         4100        1.025
    2021-01-02  dai         1           1

    TODO: check price gaps
    TODO: prices interpolation
    '''

    def __init__(
        self,
        start_dt: str or datetime,
        end_dt: str or datetime or None = None,
        granularity: str = '1D',
        fill_gaps_by_default: bool = False,
        fill_gaps_function: str = 'pad'
    ):
        # These parameters could be used later for checking price gaps, interpolation, etc.
        self._granularity = granularity
        self._start_dt = str_to_ts(start_dt)
        self.end_dt = end_dt

        self.prices = pd.DataFrame(columns=['dt', 'asset', 'price', 'price_change']).set_index('dt')
        self.fill_gaps_by_default = fill_gaps_by_default
        self.fill_gaps_function = fill_gaps_function

    def fill_prices_gaps(self):
        price_df = resample_dataframe(self.prices, self._granularity, 'price', 'asset', self.fill_gaps_function)
        self.set(price_df)

    def set(self, price_df: pd.DataFrame):
        '''
        Sets prices. New values overwrite previously provided values.

        Parameters
        ----------
        price df : pd.DataFrame
            DataFrame with prices. Expected columns: ['asset', 'price']. Expected
            index is called 'dt' and should be in a datetime readable format.
            Example:
                        asset       price
            dt
            2021-01-01  eth         4000
            2021-01-01  dai         1
            2021-01-02  eth         4100
            2021-01-02  dai         1
        '''

        if not isinstance(price_df.index, pd.DatetimeIndex):
            price_df.index = pd.DatetimeIndex(price_df.index)

        if self.fill_gaps_by_default:
            price_df = resample_dataframe(price_df, self._granularity, 'price', 'asset', self.fill_gaps_function)

        # Compute price multiplier as 1 + (x[t] - x[t-1]) / x[t]
        # Fillna with 1 - normally Nan-s appear only at self._start_dt. When strategy initiation
        # starts we have to recompute asset shares in the portfolio according to price changes.
        # On the first price change is explicitly set to 1.
        price_df['price_change'] = price_df.groupby('asset').transform(
            lambda x: 1 + pd.DataFrame.pct_change(x)).fillna(1)
        self.prices = self.prices.append(price_df)  # append new prices

        # remove duplicated records. In case of duplicates leave last value. Leaving last value makes
        # possible prices updates - just set new prices.
        self.prices = self.prices.groupby(['dt', 'asset']).last().reset_index('asset').sort_index()
