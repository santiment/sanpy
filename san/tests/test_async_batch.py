from unittest.mock import AsyncMock, patch

import pandas.testing as pdt

from san.async_batch import AsyncBatch
from san.pandas_utils import convert_to_datetime_idx_df


@patch("san.get_async", new_callable=AsyncMock)
def test_async_batch_get(mock_get_async):
    """Test AsyncBatch with get() calls."""
    df1 = convert_to_datetime_idx_df([
        {"datetime": "2024-01-01T00:00:00Z", "value": 100},
        {"datetime": "2024-01-02T00:00:00Z", "value": 200},
    ])
    df2 = convert_to_datetime_idx_df([
        {"datetime": "2024-01-01T00:00:00Z", "value": 300},
        {"datetime": "2024-01-02T00:00:00Z", "value": 400},
    ])
    mock_get_async.side_effect = [df1, df2]

    batch = AsyncBatch()
    batch.get("daily_active_addresses/bitcoin", from_date="2024-01-01", to_date="2024-01-03", interval="1d")
    batch.get("daily_active_addresses/ethereum", from_date="2024-01-01", to_date="2024-01-03", interval="1d")

    results = batch.execute()

    assert len(results) == 2
    pdt.assert_frame_equal(results[0], df1)
    pdt.assert_frame_equal(results[1], df2)


@patch("san.get_many_async", new_callable=AsyncMock)
def test_async_batch_get_many(mock_get_many_async):
    """Test AsyncBatch with get_many() calls."""
    df = convert_to_datetime_idx_df([
        {"datetime": "2024-01-01T00:00:00Z", "bitcoin": 100, "ethereum": 200},
    ])
    mock_get_many_async.return_value = df

    batch = AsyncBatch()
    batch.get_many("daily_active_addresses", slugs=["bitcoin", "ethereum"], from_date="2024-01-01", to_date="2024-01-02")

    results = batch.execute()

    assert len(results) == 1
    pdt.assert_frame_equal(results[0], df)


def test_async_batch_empty():
    """Test AsyncBatch with no queries."""
    batch = AsyncBatch()
    results = batch.execute()
    assert results == []


@patch("san.get_async", new_callable=AsyncMock)
def test_async_batch_preserves_order(mock_get_async):
    """Test that results are returned in the same order as queries were added."""
    dfs = []
    for i in range(5):
        df = convert_to_datetime_idx_df([
            {"datetime": "2024-01-01T00:00:00Z", "value": float(i)},
        ])
        dfs.append(df)

    mock_get_async.side_effect = dfs

    batch = AsyncBatch()
    for i in range(5):
        batch.get(f"metric_{i}/bitcoin", from_date="2024-01-01", to_date="2024-01-02", interval="1d")

    results = batch.execute()

    assert len(results) == 5
    for i, result in enumerate(results):
        pdt.assert_frame_equal(result, dfs[i])


@patch("san.get_async", new_callable=AsyncMock)
def test_async_batch_respects_max_workers(mock_get_async):
    """Test that execute accepts max_workers parameter."""
    df = convert_to_datetime_idx_df([
        {"datetime": "2024-01-01T00:00:00Z", "value": 1.0},
    ])
    mock_get_async.return_value = df

    batch = AsyncBatch()
    batch.get("daily_active_addresses/bitcoin", from_date="2024-01-01", to_date="2024-01-02", interval="1d")

    # Should not raise with custom max_workers
    results = batch.execute(max_workers=2)
    assert len(results) == 1
