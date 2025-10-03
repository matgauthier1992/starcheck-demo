import pandas as pd

def load_fd001(path):
    """
    Load NASA C-MAPSS FD001 dataset.
    Returns dataframe with consistent column names.
    """
    # According to FD001 spec: 26 columns (engine_id, cycle, 3 ops, 21 sensors)
    col_names = (
        ['engine_id', 'cycle', 'setting_1', 'setting_2', 'setting_3'] +
        [f'sensor_{i}' for i in range(1, 22)]
    )

    df = pd.read_csv(
        path,
        sep=r"\s+",
        header=None,
        names=col_names
    )

    return df
