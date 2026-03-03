"""Basic synchronous usage of the sanpy SDK."""

import os

import san
from san import SanError, SanRateLimitError

# --- Configuration ---

# API key (optional; set via env or directly)
if "SANPY_APIKEY" in os.environ:
    san.ApiConfig.api_key = os.environ["SANPY_APIKEY"]

# Custom User-Agent to identify your tooling
san.ApiConfig.user_agent = "MyTradingBot/1.0"

# Retry and timeout settings (defaults shown)
san.ApiConfig.request_timeout = 60.0   # seconds
san.ApiConfig.max_retries = 3          # retries for transient failures
san.ApiConfig.retry_base_delay = 1.0   # base delay for exponential backoff

print("--- 1. Fetch a single metric ---")
daa = san.get(
    "daily_active_addresses",
    slug="bitcoin",
    from_date="utc_now-7d",
    to_date="utc_now",
    interval="1d",
)
print(daa)
print()

print("--- 2. Fetch a metric for multiple assets ---")
prices = san.get_many(
    "price_usd",
    slugs=["bitcoin", "ethereum"],
    from_date="utc_now-7d",
    to_date="utc_now",
    interval="1d",
)
print(prices)
print()

print("--- 3. Batch requests (single HTTP round-trip) ---")
batch = san.Batch()
batch.get("price_usd/bitcoin", from_date="utc_now-3d", to_date="utc_now", interval="1d")
batch.get("price_usd/ethereum", from_date="utc_now-3d", to_date="utc_now", interval="1d")
[btc, eth] = batch.execute()
print(f"BTC rows: {len(btc)}, ETH rows: {len(eth)}")
print()

print("--- 4. Error handling ---")
try:
    san.get("price_usd", slug="bitcoin", from_date="2022-01-01", to_date="2022-01-05")
except SanRateLimitError as e:
    print(f"Rate limited — retry after {san.rate_limit_time_left(e)}s")
except SanError as e:
    print(f"API error: {e}")
print()

# Clean shutdown (closes the persistent HTTP connection)
san.close_client()
print("Done!")
