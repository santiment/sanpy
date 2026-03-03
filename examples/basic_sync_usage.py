import os

import san
from san.api_config import ApiConfig

# Setup API Key if you have one (not required for all endpoints, but recommended for higher rate limits)
if "SANBASE_API_KEY" in os.environ:
    ApiConfig.api_key = os.environ["SANBASE_API_KEY"]

# [NEW FEATURE] You can now optionally inject a custom User-Agent to identify your tooling clearly
ApiConfig.user_agent = "MyTradingBot/1.0"

print("--- Sanpy Basic Synchronous Usage ---")

# 1. Fetching a simple metric
print("Fetching daily active addresses for Bitcoin (last 7 days)...")
daa_df = san.get(
    "daily_active_addresses/bitcoin",
    from_date="utc_now-7d",
    to_date="utc_now",
    interval="1d"
)
print(daa_df.head())
print("\n")

# 2. Fetching multiple metrics for a single asset via GraphQL
print("Fetching general project information for all supported assets...")
project_info = san.get(
    "projects/all",
    return_fields=["name", "ticker", "totalSupply", "marketcapUsd"]
)
print(project_info)
print("\n")

# 3. Utilizing Synchronous Batch requests to fetch multiple metrics efficiently
print("Fetching synchronous batch metrics...")
batch = san.Batch()
batch.get(
    "price_usd/bitcoin",
    from_date="utc_now-3d",
    to_date="utc_now",
    interval="1d"
)
batch.get(
    "price_usd/ethereum",
    from_date="utc_now-3d",
    to_date="utc_now",
    interval="1d"
)

# Execute the batch (takes exactly one HTTP request)
results = batch.execute()
print(f"BTC Price length: {len(results[0])}")
print(f"ETH Price length: {len(results[1])}")
print("Done!")
