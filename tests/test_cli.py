import matplotlib.dates as md
import pandas as pd
from click.testing import CliRunner

from scenarioflow import Scenario, load_yaml
from scenarioflow.__main__ import cli
from scenarioflow.gui.timeline import TrackTimeline
from scenarioflow.plot import _collect_effectives


def test_help_without_arguments():
    runner = CliRunner()
    for args in (["-h"], ["plot", "-h"], ["plot", "--help"]):
        result = runner.invoke(cli, args)
        assert result.exit_code == 0, result.output
        assert "Usage" in result.output


def test_version():
    result = CliRunner().invoke(cli, ["-V"])
    assert result.exit_code == 0
    assert "version" in result.output


def test_quiet_verbose_conflict(synthetic_dir):
    result = CliRunner().invoke(cli, ["plot", "synthetic_scenario.yml", "-q", "-v"])
    assert result.exit_code != 0
    assert "mutually exclusive" in result.output


def test_plot_writes_one_file_per_series(synthetic_dir):
    result = CliRunner().invoke(cli, ["plot", "synthetic_scenario.yml", "-o", "figs", "-q"])
    assert result.exit_code == 0, result.output
    assert sorted(p.name for p in (synthetic_dir / "figs").iterdir()) == ["sac.png", "sjr.png"]


def test_plot_selected_series(synthetic_dir):
    result = CliRunner().invoke(cli, ["plot", "synthetic_scenario.yml", "--series", "sjr",
                                      "-o", "one.png", "-q"])
    assert result.exit_code == 0, result.output
    assert (synthetic_dir / "one.png").exists()


def test_track_timeline(synthetic_dir):
    """Non-interactive exercise of the Assembly Preview mock (design/gui_smoke.py)."""
    cfg = load_yaml("synthetic_scenario.yml")
    sc = Scenario.from_config(cfg)
    res = sc.run()
    ss = sc.series[0]
    comps = {c.name: sc.workspace[f"{ss.name}.{c.name}"].iloc[:, 0] for c in ss.components}
    t = TrackTimeline(ss.name, comps, _collect_effectives(ss, sc), res[ss.name].iloc[:, 0],
                      pd.Timestamp(cfg["define"]["session_start"]),
                      pd.Timestamp(cfg["define"]["session_end"]))
    assert "track regions" in t._table_text()
    t._set_boundary(1, md.date2num(pd.Timestamp("2025-05-15")))
    assert "2025-05-15" in t._table_text()
    t._on_toggle(None)
    assert t.mode == "final"
    t._on_toggle(None)
    assert t.mode == "component"
