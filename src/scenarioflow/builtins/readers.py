"""Built-in readers, keyed by the name used in ``load.name``."""

from __future__ import annotations

from typing import Any, Callable, Dict

import pandas as pd
from dms_datastore.read_multi import read_ts_repo
from dms_datastore.read_ts import read_ts


def read_climatology(source: str, **kwargs) -> pd.DataFrame:
    """
    Reads a climatology file (CSV or Excel) and returns a DataFrame.
    Assumes the file contains a datetime or period index and one or more value columns.
    """
    if source.lower().endswith(".csv"):
        df = pd.read_csv(source, index_col=0, parse_dates=False, **kwargs)
    else:
        raise ValueError(f"Unsupported climatology file format: {source}")
    return df


DEFAULT_READERS: Dict[str, Callable[..., Any]] = {
    "read_ts": read_ts,                 # dms_datastore read_ts
    "read_ts_repo": read_ts_repo,       # dms_datastore read_ts_repo
    "read_csv": pd.read_csv,            # plain pandas
    "read_climatology": read_climatology
}
