"""Static matplotlib plots of components and the assembled series."""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from scenarioflow.expressions import _substitute_scalars

logger = logging.getLogger(__name__)


def _normalize_output_path(out, series_names):
    if out is None:
        return {s: None for s in series_names}
    outp = Path(out)
    if len(series_names) == 1:
        return {series_names[0]: outp}
    if outp.suffix.lower() in (".png", ".jpg", ".jpeg", ".svg", ".pdf"):
        stem = outp.with_suffix("")
        suf = outp.suffix
        return {s: stem.with_name(f"{stem.name}_{s}").with_suffix(suf) for s in series_names}
    else:
        outp.mkdir(parents=True, exist_ok=True)
        return {s: outp / f"{s}.png" for s in series_names}



def _plot_one_series(ax, name, comp_series, final_series, scenario_start=None, scenario_end=None):
    linestyles = ["--", ":", "-.", (0, (3, 1, 1, 1)), (0, (1, 1))]
    markers = ["o", "s", "^", "d", "x", "v", "P", "*"]
    ls_i = 0
    mk_i = 0

    all_idx = None
    vals = list(comp_series.values())
    if final_series is not None:
        vals.append(final_series)
    for s in vals:
        idx = s.index.to_timestamp() if isinstance(s.index, pd.PeriodIndex) else s.index
        all_idx = idx if all_idx is None else all_idx.union(idx)

    if all_idx is None or len(all_idx) == 0:
        raise SystemExit(f"No data to plot for series '{name}'.")

    aligned = {}
    for cname, s in comp_series.items():
        idx = s.index.to_timestamp() if isinstance(s.index, pd.PeriodIndex) else s.index
        ss = s.copy()
        ss.index = idx
        aligned[cname] = ss.reindex(all_idx)

    final_aligned = None
    if final_series is not None:
        f_idx = final_series.index.to_timestamp() if isinstance(final_series.index, pd.PeriodIndex) else final_series.index
        final_aligned = final_series.copy()
        final_aligned.index = f_idx
        final_aligned = final_aligned.reindex(all_idx)

    for cname, s in aligned.items():
        if isinstance(s, pd.DataFrame):
            for col in s.columns[:4]:
                ax.plot(s.index, s[col],
                        linestyle=linestyles[ls_i % len(linestyles)],
                        marker=markers[mk_i % len(markers)],
                        linewidth=1, markersize=3,
                        label=f"{cname}.{col}")
                mk_i += 1
            ls_i += 1
        else:
            ax.plot(s.index, s,
                    linestyle=linestyles[ls_i % len(linestyles)],
                    marker=markers[mk_i % len(markers)],
                    linewidth=1, markersize=3,
                    label=cname)
            ls_i += 1
            mk_i += 1

    if final_aligned is not None:
        if isinstance(final_aligned, pd.DataFrame):
            for col in final_aligned.columns[:4]:
                ax.plot(final_aligned.index, final_aligned[col],
                        linestyle="-", linewidth=2,
                        label=f"{name}.{col}")
        else:
            ax.plot(final_aligned.index, final_aligned,
                    linestyle="-", linewidth=2,
                    label=f"{name} (final)")

    # Add scenario start/end vertical lines
    if scenario_start is not None:
        ax.axvline(scenario_start, color="red", linestyle="--", linewidth=1.5)
        ax.text(scenario_start, ax.get_ylim()[1], "Scenario Start", color="red",
                rotation=90, verticalalignment="top", horizontalalignment="right", fontsize=9)
    if scenario_end is not None:
        ax.axvline(scenario_end, color="blue", linestyle="--", linewidth=1.5)
        ax.text(scenario_end, ax.get_ylim()[1], "Scenario End", color="blue",
                rotation=90, verticalalignment="top", horizontalalignment="right", fontsize=9)

    ax.set_title(f"Series '{name}' components and final splice")
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.grid(True, which="both", linestyle="--", linewidth=0.5)
    ax.legend(ncol=2, fontsize=8)


def _collect_effectives(sspec, sc):
    """Resolve each component's effective timestamp (or None)."""
    effectives = {}
    for comp in sspec.components:
        eff = comp.effective
        if isinstance(eff, (str, dict)):
            eff = _substitute_scalars(eff, sc.defines, sc.workspace)
        try:
            effectives[comp.name] = (
                pd.Timestamp(eff) if eff not in (None, "", "start", "{start}") else None
            )
        except Exception:
            effectives[comp.name] = None
    return effectives
