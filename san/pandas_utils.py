from typing import Any

import pandas as pd


def convert_to_datetime_idx_df(data: list[dict[str, Any]]) -> pd.DataFrame:
    df = pd.DataFrame(data)

    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
        df.set_index("datetime", inplace=True)

    return df


def merge(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([df1, df2], axis=1)
