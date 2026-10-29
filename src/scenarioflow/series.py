"""A conceptual input assembled from ordered components."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import pandas as pd

from scenarioflow.component import Component
from scenarioflow.expressions import _substitute_scalars
from scenarioflow.stitch import _stitch_ts


@dataclass
class SeriesSpec:
    """Definition of one conceptual input (e.g. a river flow).

    Data components run first in listed order, then function components in
    listed order. Each output is published in the workspace as both
    ``<component>`` and ``<series>.<component>``. Outputs are then stitched in
    listed order using each component's ``effective`` time.
    """

    name: str
    dt_target: Optional[str] = None
    stitcher: Dict[str, Any] = field(default_factory=lambda: {"name": "ts_splice", "args": {}})
    components: List[Component] = field(default_factory=list)

    def run(
        self,
        defines: Dict[str, Any],
        workspace: Dict[str, Any],
        readers: Dict[str, Callable[..., Any]],
        transforms: Dict[str, Callable[..., Any]],
        functions: Dict[str, Callable[..., Any]],
    ) -> pd.Series | pd.DataFrame:
        # --- Pass 1: run DATA components in listed order ---
        for comp in (c for c in self.components if c.type == "data"):
            out = comp.run(defines, workspace, readers, transforms, functions)
            workspace[comp.name] = out
            workspace[f"{self.name}.{comp.name}"] = out

        # --- Pass 2: run FUNCTION components in listed order ---
        for comp in (c for c in self.components if c.type == "function"):
            out = comp.run(defines, workspace, readers, transforms, functions)
            workspace[comp.name] = out
            workspace[f"{self.name}.{comp.name}"] = out

        # --- Build splice inputs (same order as components) ---
        segments: List[pd.Series | pd.DataFrame] = []
        effective_points: List[Optional[pd.Timestamp]] = []
        for comp in self.components:
            ts = workspace.get(comp.name)
            if ts is None:
                continue
            eff = comp.effective
            if isinstance(eff, (str, dict)):
                eff = _substitute_scalars(eff, defines, workspace)
            segments.append(ts)
            try:
                effective_points.append(
                    pd.Timestamp(eff) if eff not in (None, "", "start", "{start}") else None
                )
            except Exception:
                effective_points.append(None)

        final = _stitch_ts(segments, self.stitcher, effective_points) if segments else None
        return final
