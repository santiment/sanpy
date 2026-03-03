"""Modern async usage of the sanpy SDK."""

import asyncio
import os
import time

import san
from san import SanError, SanRateLimitError

# --- Configuration ---
if "SANPY_APIKEY" in os.environ:
    san.ApiConfig.api_key = os.environ["SANPY_APIKEY"]

san.ApiConfig.user_agent = "AsyncDataPipeline/2.0"


async def demonstrate_native_async():
    print("--- 1. Native Async Fetching ---")
    start = time.time()

    # Fetch multiple assets concurrently with asyncio.gather
    btc, eth, link = await asyncio.gather(
        san.get_async("price_usd", slug="bitcoin", from_date="utc_now-10d", to_date="utc_now", interval="1d"),
        san.get_async("price_usd", slug="ethereum", from_date="utc_now-10d", to_date="utc_now", interval="1d"),
        san.get_async("price_usd", slug="chainlink", from_date="utc_now-10d", to_date="utc_now", interval="1d"),
    )

    print(f"Fetched 3 metrics in {time.time() - start:.2f}s")
    print(f"BTC rows: {len(btc)}, ETH rows: {len(eth)}, LINK rows: {len(link)}\n")


async def demonstrate_get_many_async():
    print("--- 2. Async Multi-Asset Fetch ---")

    # Fetch one metric for multiple slugs in a single API call
    df = await san.get_many_async(
        "price_usd",
        slugs=["bitcoin", "ethereum", "tether"],
        from_date="utc_now-7d",
        to_date="utc_now",
        interval="1d",
    )
    print(df)
    print()


async def demonstrate_async_batch():
    print("--- 3. AsyncBatch Fetching ---")
    start = time.time()

    batch = san.AsyncBatch()
    for i in range(10):
        batch.get("price_usd/bitcoin", from_date=f"utc_now-{10 + i}d", to_date=f"utc_now-{i}d", interval="1d")

    print("Queued 10 requests, executing concurrently...")
    results = await batch.execute_async(max_workers=10)

    print(f"Fetched {len(results)} results in {time.time() - start:.2f}s\n")


async def demonstrate_error_handling():
    print("--- 4. Error Handling ---")
    try:
        await san.get_async("price_usd", slug="bitcoin", from_date="2022-01-01", to_date="2022-01-05")
    except SanRateLimitError as e:
        print(f"Rate limited — retry after {san.rate_limit_time_left(e)}s")
    except SanError as e:
        print(f"API error: {e}")
    print()


async def main():
    await demonstrate_native_async()
    await demonstrate_get_many_async()
    await demonstrate_async_batch()
    await demonstrate_error_handling()

    # Clean shutdown
    san.close_client()
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
