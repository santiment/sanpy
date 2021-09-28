import logging
import datetime
import pandas as pd

from san.extras.utils import str_to_ts


_shared_error_msg = 'Asset type {} is not valid. Asset type must be one of (common, reserve)'


class Assets:
    '''
    Assets management tool. Operates with so called authorized assets.

    Authorized assets are assets that could be included in the portfolio on a
    given date. If an asset is authorized on 2021-01-01 that does not mean that
    the asset must be included in the portfolio on 2021-01-01 i.e. it's share
    in the portfolio could be 0.

    Inherits init parameters from Strategy class.

    TODO: rename assets property to common_assets
    '''

    assets = pd.DataFrame(columns=['asset'])
    reserve_assets = pd.DataFrame(columns=['asset'])

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

    def add(self, assets: dict, assets_type='common'):
        '''
        TODO: default start/end dts
        TODO: check if asset in reserve AND non-reserve assets in the same time only
        TODO: check if provided datetimes are in self.start - self.end range

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
            _test_asset_name(new_assets=assets, assets=self.assets)
            self.reserve_assets = _update_assets(assets=self.reserve_assets, new_assets=assets)
        elif assets_type.lower() in ('c', 'com', 'common'):
            _test_asset_name(new_assets=assets, assets=self.reserve_assets)
            self.assets = _update_assets(assets=self.assets, new_assets=assets)
        else:
            logging.error(_shared_error_msg.format(assets_type))

    def remove(self, assets: dict):
        '''Removes assets from reserve or non-reserve assets.

        # TODO: add complete asset removal
        # TODO: maybe add self.clear_assets()
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

        asset_names = set(self.assets['asset'].unique())
        reserve_asset_names = set(self.reserve_assets['asset'].unique())
        for asset in assets:
            if asset in asset_names:
                self.assets = _remove_assets(
                    assets_df=self.assets, exclude_asset=asset, exclude_dates=assets[asset])
            elif asset in reserve_asset_names:
                self.reserve_assets = _remove_assets(
                    assets_df=self.reserve_assets, exclude_asset=asset, exclude_dates=assets[asset])
            else:
                logging.warning(f'can\'t find {asset} in assets.')

    def get_names(self, assets_type: str = 'common'):
        '''
        Returns list of unique asset names.

        assets_type: str
            If 'r' or 'res' or 'reserve' returns reserve assets' names.
            If 'c' or 'com' or 'common' returns common assets' names
            If 'a' or 'all' return names of reserve and common assets.

        TODO: maybe keep it as state.
        '''

        def _get_assets_names():
            return list(self.assets.asset.unique())

        def _get_reserve_assets_names():
            return list(self.reserve_assets.asset.unique())

        if assets_type.lower() in ('a', 'all'):
            return _get_reserve_assets_names() + _get_assets_names()
        elif assets_type.lower() in ('r', 'res', 'reserve'):
            return _get_reserve_assets_names()
        elif assets_type.lower() in ('c', 'com', 'common'):
            return _get_assets_names()
        logging.error(_shared_error_msg.format(assets_type))

    def get_authorized_assets_for_dt(self, dt, assets_type: str = 'common'):
        '''
        Returns list of unique authorized asset names for a given dt.

        assets_type: str
            If 'r' or 'res' or 'reserve' returns reserve assets' names.
            If 'c' or 'com' or 'common' returns common assets' names
            If 'a' or 'all' return names of reserve and common assets.
        '''

        def _get_authorized_assets_for_dt():
            if dt in self.assets.index:
                return list(self.assets.loc[[dt]].asset.unique())
            return []

        def _get_authorized_reserved_assets_for_dt():
            if dt in self.reserve_assets.index:
                return list(self.reserve_assets.loc[[dt]].asset.unique())
            return []

        if assets_type.lower() in ('a', 'all'):
            return _get_authorized_reserved_assets_for_dt() + _get_authorized_assets_for_dt()
        elif assets_type.lower() in ('r', 'res', 'reserve'):
            return _get_authorized_reserved_assets_for_dt()
        elif assets_type.lower() in ('c', 'com', 'common'):
            return _get_authorized_assets_for_dt()
        logging.error(_shared_error_msg.format(assets_type))
