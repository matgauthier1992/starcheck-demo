import pandas as pd

def add_rul(df):
    """
    Add Remaining Useful Life (RUL) column.
    For each engine, RUL = max(cycle) - current cycle.
    """
    rul = df.groupby("engine_id")["cycle"].transform("max") - df["cycle"]
    df = df.copy()
    df["RUL"] = rul
    return df

def add_features(df):
    """
    Add engineered features to match training + app consistently.
    Uses rolling mean (window=5) and first difference
    for selected sensors.
    """
    df = df.copy()

    # Rolling mean (window = 5)
    for sensor in [7, 11, 12]:
        df[f"sensor_{sensor}_rollmean_w5"] = (
            df.groupby("engine_id")[f"sensor_{sensor}"]
              .transform(lambda x: x.rolling(window=5, min_periods=1).mean())
        )

    # First difference (delta from previous cycle)
    for sensor in [7, 11, 12]:
        df[f"sensor_{sensor}_diff"] = (
            df.groupby("engine_id")[f"sensor_{sensor}"].diff().fillna(0)
        )

    return df
