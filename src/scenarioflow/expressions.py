"""Substitution of ``${...}`` parameters and ``$!{...}`` workspace expressions.

``${name}``
    A parameter from the ``define:`` block or, failing that, an environment
    variable. Always produces text.

``$!{expr}``
    An expression evaluated against the scenario workspace, e.g.
    ``$!{forecast.last_valid_index()}``. When the whole string is a single
    ``$!{...}`` the evaluated object is returned; otherwise its text is inlined.
    Evaluation uses :func:`eval` with no builtins and the names in
    ``_ALLOWED_FUNCS`` plus the workspace.
"""

from __future__ import annotations

import math
import os
import re
from typing import Any, Dict

import pandas as pd

_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")
_WS_PATTERN  = re.compile(r"\$\!\{([^}]+)\}")
_FULL_WS_PATTERN = re.compile(r'^\s*\$\!\{([^}]+)\}\s*$')

_ALLOWED_FUNCS = {
    "days":    lambda n=0: pd.Timedelta(days=float(n)),
    "hours":   lambda n=0: pd.Timedelta(hours=float(n)),
    "minutes": lambda n=0: pd.Timedelta(minutes=float(n)),
    "pd": pd,
    "math": math,
}


def _safe_eval(expr: str, workspace: Dict[str, Any]) -> Any:
    env = dict(_ALLOWED_FUNCS)
    env.update(workspace)
    return eval(expr, {"__builtins__": {}}, env)


def _substitute_scalars(obj: Any, defines: Dict[str, Any], workspace: Dict[str, Any]) -> Any:
    if isinstance(obj, dict):
        return {k: _substitute_scalars(v, defines, workspace) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_substitute_scalars(v, defines, workspace) for v in obj]
    if not isinstance(obj, str):
        return obj

    # 1) If the whole string is a $!{…}, return the evaluated OBJECT (not a string)
    m = _FULL_WS_PATTERN.match(obj)
    if m:
        return _safe_eval(m.group(1), workspace)

    # 2) Otherwise do normal ${…} vars then inline $!{…} as strings
    def _var_replace(m):
        key = m.group(1).strip()
        if key in defines:
            return str(defines[key])
        val = os.environ.get(key)
        if val is None:
            raise KeyError(f"Undefined variable '{key}' for ${{...}} substitution")
        return val

    s = _VAR_PATTERN.sub(_var_replace, obj)

    def _eval_replace(m):
        val = _safe_eval(m.group(1), workspace)
        return str(val)  # inline replacement must be text
    s = _WS_PATTERN.sub(_eval_replace, s)
    return s
