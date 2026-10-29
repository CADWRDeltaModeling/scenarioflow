"""Built-in transforms, keyed by the name used in ``transformations[].name``.

A transform is called as ``fn(ts, **args)`` and returns the transformed data.
"""

from __future__ import annotations

from typing import Any, Callable, Dict

import vtools.functions.unit_conversions as uc
from vtools import apply_climatology, rhistinterp
from vtools.data.timeseries import rename_columns, to_dataframe


def transform_unit_conversion(ts, *, from_unit: str, to_unit: str, **_):
    return uc.convert_units(ts, from_unit, to_unit)


def transform_rhistinterp(ts, *, dest: str, p: float = 2.0, **kwargs):
    ts.index = ts.index.to_period()
    return to_dataframe(rhistinterp(ts, dest, p=p, **kwargs))


def transform_apply_climatology(ts, *, start=None, end=None, freq=None, index=None, **_):
    return apply_climatology(ts, index=index, start=start, end=end, freq=freq)


def transform_rename_columns(ts, *, colnames, convert_df=True, **_):
    return rename_columns(ts, colnames=colnames, convert_df=convert_df)


DEFAULT_TRANSFORMS: Dict[str, Callable[..., Any]] = {
    "unit_conversion": transform_unit_conversion,
    "rhistinterp": transform_rhistinterp,
    "apply_climatology": transform_apply_climatology,
    "rename_columns": transform_rename_columns,
}
