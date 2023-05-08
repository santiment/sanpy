CUSTOM_QUERIES = {"ohlcv": "get_ohlcv"}

DEPRECATED_QUERIES = {
    "mvrv_ratio": "mvrv_usd",
    "nvt_ratio": "nvt",
    "realized_value": "realized_value_usd",
    "token_circulation": "circulation_1d",
    "burn_rate": "age_destroyed",
    "token_age_consumed": "age_destroyed",
    "token_velocity": "velocity",
    "daily_active_deposits": "active_deposits",
    "social_volume": "social_volume_{source}",
    "social_dominance": "social_dominance_{source}",
}

NO_SLUG_QUERIES = [
    "social_volume_projects",
    "emerging_trends",
    "top_social_gainers_losers",
]
QUERY_MAPPING = {
    "burn_rate": {  # to be removed
        "query": "burnRate",
        "return_fields": ["datetime", "burnRate"],
    },
    "token_age_consumed": {
        "query": "tokenAgeConsumed",
        "return_fields": ["datetime", "tokenAgeConsumed"],
    },
    "average_token_age_consumed_in_days": {
        "query": "averageTokenAgeConsumedInDays",
        "return_fields": ["datetime", "tokenAge"],
    },
    "prices": {
        "query": "historyPrice",
        "return_fields": ["datetime", "priceUsd", "priceBtc", "marketcap", "volume"],
    },
    "ohlc": {
        "query": "ohlc",
        "return_fields": [
            "datetime",
            "openPriceUsd",
            "closePriceUsd",
            "highPriceUsd",
            "lowPriceUsd",
        ],
    },
    "exchange_funds_flow": {
        "query": "exchangeFundsFlow",
        "return_fields": ["datetime", "inOutDifference"],
    },
    # OLD
    "token_velocity": {
        "query": "tokenVelocity",
        "return_fields": ["datetime", "tokenVelocity"],
    },
    # OLD
    "token_circulation": {
        "query": "tokenCirculation",
        "return_fields": ["datetime", "tokenCirculation"],
    },
    # OLD
    "realized_value": {
        "query": "realizedValue",
        "return_fields": ["datetime", "realizedValue"],
    },
    # OLD
    "mvrv_ratio": {"query": "mvrvRatio", "return_fields": ["datetime", "ratio"]},
    # OLD
    "nvt_ratio": {
        "query": "nvtRatio",
        "return_fields": ["datetime", "nvtRatioCirculation", "nvtRatioTxVolume"],
    },
    # OLD
    "daily_active_deposits": {
        "query": "dailyActiveDeposits",
        "return_fields": ["datetime", "activeDeposits"],
    },
    "gas_used": {"query": "gasUsed", "return_fields": ["datetime", "gasUsed"]},
    "miners_balance": {
        "query": "minersBalance",
        "return_fields": ["balance", "datetime"],
    },
    "mining_pools_distribution": {
        "query": "miningPoolsDistribution",
        "return_fields": ["datetime", "other", "top10", "top3"],
    },
    "history_twitter_data": {
        "query": "historyTwitterData",
        "return_fields": ["datetime", "followers_count"],
    },
    "historical_balance": {
        "query": "historicalBalance",
        "return_fields": ["datetime", "balance"],
    },
    # OLD
    "social_dominance": {
        "query": "socialDominance",
        "return_fields": ["datetime", "dominance"],
    },
    "top_holders_percent_of_total_supply": {
        "query": "topHoldersPercentOfTotalSupply",
        "return_fields": [
            "datetime",
            "inExchanges",
            "outsideExchanges",
            "inTopHoldersTotal",
        ],
    },
    "projects": {
        "query": "allProjects",
        "return_fields": ["name", "slug", "ticker", "totalSupply", "marketSegment"],
    },
    "get_metric": {"query": "getMetric", "return_fields": ["datetime", "value"]},
    "topic_search": {
        "query": "topicSearch",
        "return_fields": [("chartData", ["datetime, " "mentionsCount"])],
    },
    "top_transfers": {
        "query": "topTransfers",
        "return_fields": [
            "datetime",
            ("fromAddress", ["address"]),
            ("toAddress", ["address"]),
            "trxValue",
            "trxHash",
        ],
    },
    "eth_top_transactions": {
        "query": "ethTopTransactions",
        "return_fields": [
            "datetime",
            ("fromAddress", ["address", "isExchange"]),
            ("toAddress", ["address", "isExchange"]),
            "trxHash",
            "trxValue",
        ],
    },
    "token_top_transactions": {
        "query": "tokenTopTransactions",
        "return_fields": [
            "datetime",
            ("fromAddress", ["address", "isExchange"]),
            ("toAddress", ["address", "isExchange"]),
            "trxHash",
            "trxValue",
        ],
    },
    "eth_spent_over_time": {
        "query": "ethSpentOverTime",
        "return_fields": ["datetime", "ethSpent"],
    },
    "news": {
        "query": "news",
        "return_fields": ["datetime", "title", "sourceName", "url", "description"],
    },
    "price_volume_difference": {
        "query": "priceVolumeDiff",
        "return_fields": ["datetime", "priceChange", "priceVolumeDiff", "volumeChange"],
    },
    # OLD
    "social_volume": {
        "query": "socialVolume",
        "return_fields": ["datetime", "mentionsCount"],
    },
    "top_social_gainers_losers": {
        "query": "topSocialGainersLosers",
        "return_fields": ["datetime", ("projects", ["change", "slug", "status"])],
    },
    "emerging_trends": {
        "query": "getTrendingWords",
        "return_fields": ["datetime", ("topWords", ["score", "word"])],
    },
    "social_volume_projects": {},
}
