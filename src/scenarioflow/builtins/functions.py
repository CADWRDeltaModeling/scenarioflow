"""Built-in functions for ``type: function`` components, keyed by ``method``.

A function is called with keyword arguments only and returns a time series.
"""

from __future__ import annotations

from typing import Any, Callable, Dict

import pandas as pd
from vtools import transition_ts


def func_transition_ts(*, ts0=None, ts1=None, method="linear", window=None, overlap=(0, 0),
                       return_type="series", names=None, max_snap=None, **_):
    if ts0 is None or ts1 is None:
        raise ValueError("transition_ts requires ts0 and ts1")
    return transition_ts(ts0, ts1, method=method, window=window, overlap=overlap,
                         return_type=return_type, names=names, max_snap=max_snap)


def func_extrapolate_ts(*, ts, start, end, method="ffill", **kwargs):
    ts = ts.sort_index()
    if isinstance(ts.index, pd.PeriodIndex):
        ts = ts.to_timestamp(how="start")
    if method == "ffill":
        freq = ts.index.inferred_freq or ts.index.freq
        if freq is None:
            raise ValueError("Cannot infer frequency for extrapolation; ensure regular index or set freq")
        idx = pd.date_range(start=start, end=end, freq=freq)
        out = ts.reindex(ts.index.union(idx)).ffill().reindex(idx)
        return out
    raise NotImplementedError(f"extrapolate_ts method '{method}' not implemented")


DEFAULT_FUNCTIONS: Dict[str, Callable[..., Any]] = {
    "transition_ts": func_transition_ts,
    "extrapolate_ts": func_extrapolate_ts,
}
