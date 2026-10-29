"""Plot scenario series, or open the interactive Assembly Preview mock."""

from __future__ import annotations

import logging
from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas as pd

from scenarioflow.cli_common import logging_options, setup_logging
from scenarioflow.config import load_yaml
from scenarioflow.plot import _collect_effectives, _normalize_output_path, _plot_one_series
from scenarioflow.scenario import Scenario

logger = logging.getLogger(__name__)


def _component_dict(sspec, sc):
    comp_dict = {}
    for comp in sspec.components:
        # Prefer namespaced value; fall back to global. Avoid `or` on DataFrames.
        ns_key = f"{sspec.name}.{comp.name}"
        out = sc.workspace.get(ns_key, None)
        if out is None:
            out = sc.workspace.get(comp.name, None)
        if out is None:
            continue
        if isinstance(out, pd.DataFrame) and out.shape[1] == 1:
            comp_dict[comp.name] = out.iloc[:, 0]
        else:
            comp_dict[comp.name] = out
    return comp_dict


def plot_scenario(config, series=None, output=None, show=False, gui=False):
    """Run a scenario and plot its components and assembled series.

    Steps:

    1. Load the scenario YAML and run every series.
    2. Select the requested series (default: all).
    3. With ``gui``, open one interactive Assembly Preview per series and
       block until closed. Otherwise draw one static figure per series,
       saving to ``output`` and/or showing it.

    Parameters
    ----------
    config : str or pathlib.Path
        Scenario YAML.
    series : list of str, optional
        Series names to plot. Unknown names are logged and skipped.
    output : str or pathlib.Path, optional
        Output file (single series), file stem with image suffix (one file per
        series, ``<stem>_<series><suffix>``) or directory (``<series>.png``).
    show : bool
        Show each static figure interactively.
    gui : bool
        Open the interactive Assembly Preview mock instead of static plots.
    """
    cfg = load_yaml(str(config))
    sc = Scenario.from_config(cfg)
    results = sc.run()  # dict: {series_name: final_ts}
    scenario_start = pd.to_datetime(cfg.get("define", {}).get("session_start", None))
    scenario_end = pd.to_datetime(cfg.get("define", {}).get("session_end", None))

    available = [ss.name for ss in sc.series]
    if series:
        selected = [s for s in series if s in results]
        missing = [s for s in series if s not in results]
        if missing:
            logger.warning("Series not found and will be skipped: %s", missing)
    else:
        selected = available

    if gui:
        from scenarioflow.gui.timeline import TrackTimeline

        _timelines = []  # keep references alive so callbacks survive
        for sname in selected:
            sspec = next((ss for ss in sc.series if ss.name == sname), None)
            if sspec is None:
                continue
            comp_dict = _component_dict(sspec, sc)
            if not comp_dict:
                logger.warning("Series '%s' has no component data to show; skipping.", sname)
                continue
            effectives = _collect_effectives(sspec, sc)
            final_ts = results.get(sname)
            if isinstance(final_ts, pd.DataFrame) and final_ts.shape[1] == 1:
                final_ts = final_ts.iloc[:, 0]
            _timelines.append(
                TrackTimeline(sname, comp_dict, effectives, final_ts,
                              scenario_start, scenario_end)
            )
        if _timelines:
            plt.show()
        return

    out_paths = _normalize_output_path(output, selected)

    for sname in selected:
        sspec = next((ss for ss in sc.series if ss.name == sname), None)
        if sspec is None:
            continue
        comp_dict = _component_dict(sspec, sc)

        final_ts = results.get(sname)
        if isinstance(final_ts, pd.DataFrame) and final_ts.shape[1] == 1:
            final_ts = final_ts.iloc[:, 0]

        fig, ax = plt.subplots(figsize=(12, 5))
        _plot_one_series(ax, sname, comp_dict, final_ts, scenario_start, scenario_end)
        fig.tight_layout()

        outp = out_paths.get(sname)
        if outp:
            outp.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(outp, dpi=150)
            logger.info("Saved figure to %s", outp)
        if show:
            plt.show()
        plt.close(fig)


@click.command(name="plot")
@click.argument("config", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--series", multiple=True, metavar="NAME",
              help="Series to plot (repeatable). Default: all.")
@click.option("-o", "--output", "--out", "output", type=click.Path(path_type=Path), default=None,
              help="Output file or directory.")
@click.option("--show", is_flag=True, help="Show interactive window.")
@click.option("--gui", is_flag=True, help="Open the interactive Assembly Preview timeline mock.")
@logging_options
@click.help_option("-h", "--help")
def plot_scenario_cli(config, series, output, show, gui, logdir, debug, verbose, quiet):
    """Run scenario CONFIG and plot components with the assembled series."""
    setup_logging(logdir=logdir, debug=debug, verbose=verbose, quiet=quiet, prefix="sflow_plot")
    plot_scenario(config=config, series=list(series) or None, output=output, show=show, gui=gui)


if __name__ == "__main__":
    plot_scenario_cli()
