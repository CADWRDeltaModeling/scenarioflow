"""A scenario: a set of conceptual inputs sharing defines and a workspace."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import pandas as pd
import vtools.functions.unit_conversions as uc
from vtools import rhistinterp, transition_ts

from scenarioflow.builtins import DEFAULT_FUNCTIONS, DEFAULT_READERS, DEFAULT_TRANSFORMS
from scenarioflow.component import Component
from scenarioflow.series import SeriesSpec


@dataclass
class Scenario:
    """A named collection of :class:`~scenarioflow.series.SeriesSpec` with shared configuration.

    Readers, transforms and functions default to the built-in tables and may
    be extended through ``extra_namespace`` in ``from_config``.
    """

    name: str
    dt_target: Optional[str] = None
    series: List[SeriesSpec] = field(default_factory=list)

    readers: Dict[str, Callable[..., Any]] = field(default_factory=lambda: dict(DEFAULT_READERS))
    transforms: Dict[str, Callable[..., Any]] = field(default_factory=lambda: dict(DEFAULT_TRANSFORMS))
    functions: Dict[str, Callable[..., Any]] = field(default_factory=lambda: dict(DEFAULT_FUNCTIONS))

    stitcher: Dict[str, Any] = field(default_factory=lambda: {"name": "ts_splice", "args": {}})

    defines: Dict[str, Any] = field(default_factory=dict)
    workspace: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)

    def get(self, name: str) -> Any:
        return self.outputs.get(name)

    def run(self) -> Dict[str, pd.Series | pd.DataFrame]:
        # Shared workspace exposes common helpers; component outputs accumulate per series
        self.workspace.update({
            "convert_units": uc.convert_units,
            "rhistinterp": rhistinterp,
            "transition_ts": transition_ts,
            "pd": pd,
        })

        results: Dict[str, pd.Series | pd.DataFrame] = {}
        for ss in self.series:
            # isolate series-local run but share workspace to allow cross-references if desired
            final = ss.run(self.defines, self.workspace, self.readers, self.transforms, self.functions)
            self.outputs[ss.name] = final
            results[ss.name] = final
        return results

    @staticmethod
    def from_config(cfg: Dict[str, Any], extra_namespace: Optional[Dict[str, Any]] = None) -> "Scenario":
        defines = dict(cfg.get("define", {}))
        if extra_namespace:
            defines.update({k: v for k, v in extra_namespace.items() if not callable(v)})
        sc_block = cfg.get("scenario")
        if sc_block is None:
            raise ValueError("Config missing 'scenario' block")

        # Scenario-level fields
        sc_name = sc_block.get("name", "scenario")
        sc_dt   = sc_block.get("defaults", {}).get("dt_target") or sc_block.get("dt_target")
        sc_stitcher = sc_block.get("defaults", {}).get("stitcher") or sc_block.get("stitcher", {"name": "ts_splice", "args": {}})

        # Series list
        series_list: List[SeriesSpec] = []
        for sraw in sc_block.get("series", []):
            comps: List[Component] = []
            for craw in sraw.get("components", []):
                comps.append(Component(
                    name=craw.get("name"),
                    type=craw.get("type"),
                    effective=craw.get("effective"),
                    # support both 'load' and 'load_method' keys
                    load_method=craw.get("load") or craw.get("load_method"),
                    method=craw.get("method"),
                    transformations=craw.get("transformations") or [],
                    args=craw.get("args") or {},
                ))
            ss = SeriesSpec(
                name=sraw.get("name"),
                dt_target=sraw.get("dt_target", sc_dt),
                stitcher=sraw.get("stitcher", sc_stitcher),
                components=comps,
            )
            series_list.append(ss)

        sc = Scenario(
            name=sc_name,
            dt_target=sc_dt,
            series=series_list,
            defines=defines,
            stitcher=sc_stitcher,
        )

        if extra_namespace:
            sc.workspace.update(extra_namespace)
            for k in ("readers", "transforms", "functions"):
                if k in extra_namespace and isinstance(extra_namespace[k], dict):
                    getattr(sc, k).update(extra_namespace[k])
        return sc
