
CUSTOM_QUERIES = {
    'ohlcv': 'get_ohlcv'
}

DEPRECATED_QUERIES = {
    'mvrv_ratio': 'mvrv_usd',
    'nvt_ratio': 'nvt',
    'realized_value': 'realized_value_usd',
    'token_circulation': 'circulation_1d',
    'burn_rate': 'age_destroyed',
    'token_age_consumed': 'age_destroyed',
    'token_velocity': 'velocity',
    'daily_active_deposits': 'active_deposits',
    'social_volume': 'social_volume_{source}',
    'social_dominance': 'social_dominance_{source}'
}

NO_SLUG_QUERIES = [
    'social_volume_projects',
    'emerging_trends',
    'top_social_gainers_losers'
]
