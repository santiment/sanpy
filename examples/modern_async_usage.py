import asyncio
import os
import time

import san
from san.api_config import ApiConfig

# Configure credentials
if "SANBASE_API_KEY" in os.environ:
    ApiConfig.api_key = os.environ["SANBASE_API_KEY"]

# Identify your client
ApiConfig.user_agent = "AsyncDataPipeline/2.0"

async def demonstrate_native_async():
    print("--- 1. Native Async Fetching ---")
    start = time.time()
    
    # We can fetch multiple assets inherently concurrently without thread pools!
    tasks = [
        san.get_async("price_usd/bitcoin", from_date="utc_now-10d", to_date="utc_now", interval="1d"),
        san.get_async("price_usd/ethereum", from_date="utc_now-10d", to_date="utc_now", interval="1d"),
        san.get_async("price_usd/chainlink", from_date="utc_now-10d", to_date="utc_now", interval="1d")
    ]
    
    # Run them all through the asyncio event loop using httpx internally
    results = await asyncio.gather(*tasks)
    
    print(f"Fetched 3 disjoint network metrics in {time.time() - start:.2f} seconds.")
    print(f"BTC records: {len(results[0])}, ETH records: {len(results[1])}, LINK records: {len(results[2])}\n")


async def demonstrate_async_batch():
    print("--- 2. AsyncBatch Fetching ---")
    start = time.time()
    
    # AsyncBatch is now backed by `asyncio.gather` and scales astronomically well compared to ThreadPools.
    batch = san.AsyncBatch()
    
    # Queue up 50 requests
    for i in range(10):
        # Using simple open-tier metrics
        batch.get(
            "price_usd/bitcoin",
            from_date=f"utc_now-{10+i}d",
            to_date=f"utc_now-{i}d",
            interval="1d"
        )
        
    print(f"Queued 10 requests. Executing AsyncBatch (using concurrent chunking)...")
    
    # `execute_async()` will automatically partition the 50 queries into `max_workers` concurrent chunks, 
    # executing them seamlessly without blocking the main Python thread.
    batch_results = await batch.execute_async(max_workers=10)
    
    print(f"Fetched {len(batch_results)} batch results in {time.time() - start:.2f} seconds.")
    print("Done!")

async def main():
    await demonstrate_native_async()
    await demonstrate_async_batch()

if __name__ == "__main__":
    asyncio.run(main())
