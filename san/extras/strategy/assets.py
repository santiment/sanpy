import logging
import datetime
import pandas as pd

from san.extras.utils import str_to_ts


class Assets:
    '''
    Assets management tool. Operates with so called authorized assets.

    Authorized assets are assets that could be included in the portfolio on a
    given date. If an asset is authorized on 2021-01-01 that does not mean that
    the asset must be included in the portfolio on 2021-01-01 i.e. it's share
    in the portfolio could be 0.

    There are 2 types of assets (and init_asset as a special case):
    * Common assets
        Common assets are assets that are traded in the portfolio. Typically
        investor bets exactly on common assets. Common assets could be used for
        other purposes as well (like risk hedging, etc).
    * Reserve assets
        Reserve assets are used in some strategies as assets you trade common
        assets to. Usually any stablecoin could be used as reserve asset. Once
        you sell one of common assets you might rebalance other assets in the
        portfolio or just keep funds safe for a next buy (rebalance) signal.
    * Init_asset
        Init_asset is an asset investor owes before the stategy was initiated.

    Parameters
    ----------
    start_dt : str or datetime
        Datetime when the portfolio was initiated.
    end_dt : str or datetime, default None
        Datetime to stop the strategy.
    granularity : str, default '1D'
        Time distance between datetimes.
    decision_delay : int, default 0
        Time gap between the signal's dt and the action that should be
        performed due to that signal.
    init_asset:  str or None, default None
        Asset the investor owes before the stategy was initiated. Init_asset
        will be used in order to buy all necessary assets on the first day or
        later. Init_asset automatically will be set as forst reserve_asset if
        not provided explicitly.

    Examples
    ----------
    Stores authorized reserved and common assets as pandas DataFrame:
                asset
    dt
    2021-01-01  eth
    2021-01-01  uni
    2021-01-02  eth
    2021-01-02  uni
    2021-01-03  uni

    Common and reserve assets are stored separately.
    Init_asset is stored as a string (e.g. 'dai').

    TODO: add add(remove)_assets_from_list
    '''

    def __init__(
        self,
        start_dt: str or datetime,
        end_dt: str or datetime or None = None,
        granularity: str = '1D',
        init_asset: str or None = None,

    ):
        self._granularity = granularity
        self._start_dt = str_to_ts(start_dt)
        self.end_dt = end_dt
        self.init_asset = init_asset

        self.common_assets = pd.DataFrame(columns=['asset'])
        self.reserve_assets = pd.DataFrame(columns=['asset'])

    def __sort_asset_types(self, assets_type, c_case, r_case, skip_a_case=False):

        if not skip_a_case and assets_type.lower() in ('a', 'all'):
            return r_case() + c_case()
        elif assets_type.lower() in ('r', 'res', 'reserve'):
            return r_case()
        elif assets_type.lower() in ('c', 'com', 'common'):
            return c_case()
        logging.error(f'Asset type {assets_type} is invalid.\
                        Asset type must be one of (common, reserve{"" if skip_a_case else ", all"})')

    def add(self, assets: dict, assets_type='common'):
        '''
        Add assets to authorized assets. Each asset should have a time interval
        according to which an asset will be considered as authorized. Datetimes
        are parsed in pairs as start_dt_1, end_dt_1, start_dt_2, end_dt_2...

        Parameters
        ----------
        assets : dict
            Assets with dates to add.
            Example: {
                'ethereum': ['2021-01-01', '2021-01-10', '2021-01-15', '2021-01-21'],
                'uniswap': [2021-01-01, '2021-01-03]
            }
        assets_type : str, default 'common'
            If 'r' or 'res' or 'reserve' adds asset(s) to reserve assets.
            If 'c' or 'com' or 'common' adds asset(s) to common assets.

        TODO: default start/end dts
        TODO: check if asset in reserve AND non-reserve assets in the same time only
        TODO: check if provided datetimes are in self.start - self.end range
        '''

        def _update_assets(assets, new_assets, granularity=self._granularity):
            ''' Updates assets-in-the-portfolio dataFrame.'''
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

        def _test_asset_name(new_assets, assets):
            ''' Checks if asset belongs to one and only one of (assets, reserve_assets).'''
            assets_names = set(assets['asset'].unique())  # works faster than set(assets['asset']) when len(df) is big
            for asset_name in new_assets:
                assert asset_name not in assets_names, \
                    f'{asset_name} cant be used both as reserve and non-reserve asset!'

        if assets_type.lower() in ('r', 'res', 'reserve'):
            _test_asset_name(new_assets=assets, assets=self.common_assets)
            self.reserve_assets = _update_assets(assets=self.reserve_assets, new_assets=assets)
        elif assets_type.lower() in ('c', 'com', 'common'):
            _test_asset_name(new_assets=assets, assets=self.reserve_assets)
            self.common_assets = _update_assets(assets=self.common_assets, new_assets=assets)
        else:
            logging.error(f'Asset type {assets_type} is not valid. Asset type must be one of (common, reserve)')

    def remove(self, assets: dict):
        '''
        Removes assets from reserve or non-reserve assets.

        Parameters
        ----------
        assets : dict
            Assets to remove. Example: {'ethereum': ['2021-01-01', '2021-01-15']}
        '''

        def _remove_assets(assets_df, exclude_asset, exclude_dates, granularity=self._granularity):
            dates = [str_to_ts(dt) for dt in exclude_dates]
            assert len(dates) % 2 == 0, f'Unsupported datetime sequence for {exclude_asset}: odd amount of dates.'

            for i in range(int(len(dates) / 2)):
                exclude_dates = list(pd.date_range(start=dates[2 * i], end=dates[2 * i + 1], freq=granularity))
                assets_df = assets_df[
                    ~((assets_df.index.isin(exclude_dates)) & (assets_df['asset'] == exclude_asset))
                ]
            return assets_df

        common_asset_names = set(self.common_assets['asset'].unique())
        reserve_asset_names = set(self.reserve_assets['asset'].unique())
        for asset in assets:
            if asset in common_asset_names:
                self.common_assets = _remove_assets(
                    assets_df=self.common_assets, exclude_asset=asset, exclude_dates=assets[asset])
            elif asset in reserve_asset_names:
                self.reserve_assets = _remove_assets(
                    assets_df=self.reserve_assets, exclude_asset=asset, exclude_dates=assets[asset])
            else:
                logging.warning(f'can\'t find {asset} in assets.')

    def get_names(self, assets_type: str = 'common'):
        '''
        Returns list of unique asset names.

        Parameters
        ----------
        assets_type : str, default 'common'
            If 'r' or 'res' or 'reserve' returns reserve assets' names.
            If 'c' or 'com' or 'common' returns common assets' names
            If 'a' or 'all' return names of reserve and common assets.
        '''

        def _get_common_assets_names():
            return list(self.common_assets.asset.unique())

        def _get_reserve_assets_names():
            return list(self.reserve_assets.asset.unique())

        return self.__sort_asset_types(
            assets_type=assets_type,
            c_case=_get_common_assets_names,
            r_case=_get_reserve_assets_names
        )

    def get_authorized_assets_for_dt(self, dt: str or datetime.datetime, assets_type: str = 'common'):
        '''
        Returns list of unique authorized asset names for a given dt.

        Parameters
        ----------
        dt : str or datetime.datetime
            Datetime to get authorized assets for.
        assets_type : str, default 'common'
            If 'r' or 'res' or 'reserve' returns reserve assets' names.
            If 'c' or 'com' or 'common' returns common assets' names
            If 'a' or 'all' return names of reserve and common assets.
        '''

        def _get_authorized_common_assets_for_dt():
            if dt in self.common_assets.index:
                return list(self.common_assets.loc[[dt]].asset.unique())
            return []

        def _get_authorized_reserved_assets_for_dt():
            if dt in self.reserve_assets.index:
                return list(self.reserve_assets.loc[[dt]].asset.unique())
            return []

        return self.__sort_asset_types(
            assets_type=assets_type,
            c_case=_get_authorized_common_assets_for_dt,
            r_case=_get_authorized_reserved_assets_for_dt
        )

    def clear_assets(self, assets_type: str = 'common'):
        '''
        Clears all assets of a provided type.

        Parameters
        ----------
        assets_type : str, default 'common'
            If 'r' or 'res' or 'reserve' returns reserve assets' names.
            If 'c' or 'com' or 'common' returns common assets' names
            If 'a' or 'all' return names of reserve and common assets.
        '''

        def _clear_common_assets():
            self.common_assets = pd.DataFrame(columns=['asset'])

        def _clear_reserve_assets():
            self.reserve_assets = pd.DataFrame(columns=['asset'])

        self.__sort_asset_types(
            assets_type=assets_type,
            c_case=_clear_common_assets,
            r_case=_clear_reserve_assets
        )
