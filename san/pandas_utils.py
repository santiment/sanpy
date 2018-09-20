import pandas as pd


def convert_to_datetime_idx_df(data):
    df = pd.DataFrame(data)

    if 'datetime' in df.columns:
        df['datetime'] = pd.to_datetime(df['datetime'], utc=True)
        df.set_index('datetime', inplace=True)

    return df


def merge(df1, df2):
    return pd.merge(df1, df2, on="datetime")
