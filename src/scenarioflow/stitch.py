"""Stitching of ordered component outputs into one series."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd
from vtools.functions.merge import ts_merge as _ts_merge_impl
from vtools.functions.merge import ts_splice as _ts_splice


def _stitch_ts(
    series_list: List[pd.Series | pd.DataFrame],
    stitcher: Dict[str, Any],
    effective_points: List[Optional[pd.Timestamp]],
) -> pd.Series | pd.DataFrame:
    name = (stitcher or {}).get("name", "ts_splice")
    args = dict((stitcher or {}).get("args", {}) or {})

    if name == "ts_splice":
        # Optional: clip the first segment by its own effective (comment out if you prefer to clip elsewhere)
        eff0 = effective_points[0] if effective_points else None
        if eff0 is not None:
            t0 = pd.Timestamp(eff0)
            s0 = series_list[0]
            if isinstance(s0.index, pd.PeriodIndex):
                # Clip by comparing at the left-edge timestamp of each period
                mask = s0.index.to_timestamp(how="start") >= t0
                series_list[0] = s0.loc[mask]
            else:
                series_list[0] = s0.loc[t0:]

        # Build transitions strictly from the provided effective_points (skip None), in listed order.
        # effective_points corresponds 1:1 with series_list; we use items 1..N-1.
        transitions = [
            pd.Timestamp(t) for t in (effective_points[1:] if len(effective_points) > 1 else [])
            if t is not None
        ]

        if "transition" not in args:
            args["transition"] = transitions

        return _ts_splice(series_list, **args)

    if name == "ts_merge":
        return _ts_merge_impl(series_list, **args)

    raise ValueError(f"Unknown stitcher '{name}'")
