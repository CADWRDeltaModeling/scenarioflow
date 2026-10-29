import pandas as pd
import pytest

from scenarioflow import Scenario, load_yaml
from scenarioflow.plot import _collect_effectives


@pytest.fixture
def ran(synthetic_dir):
    cfg = load_yaml("synthetic_scenario.yml")
    sc = Scenario.from_config(cfg)
    return cfg, sc, sc.run()


def test_series_produced(ran):
    cfg, sc, res = ran
    assert list(res) == ["sac", "sjr"]
    for name, final in res.items():
        assert isinstance(final, pd.DataFrame)
        assert final.index.freq == pd.Timedelta("15min")
        assert final.index[-1] == pd.Timestamp(cfg["define"]["session_end"])


def test_workspace_publishes_namespaced_components(ran):
    _, sc, _ = ran
    for ss in sc.series:
        for comp in ss.components:
            assert f"{ss.name}.{comp.name}" in sc.workspace


def test_history_used_before_transition(ran):
    _, sc, res = ran
    hist = sc.workspace["sac.hist"]
    window = slice("2025-04-01", "2025-04-30")
    pd.testing.assert_series_equal(res["sac"].loc[window].iloc[:, 0], hist.loc[window].iloc[:, 0],
                                   check_names=False)


def test_effectives(ran):
    _, sc, _ = ran
    effs = _collect_effectives(sc.series[0], sc)
    assert effs["hist"] == pd.Timestamp("2025-04-01")
    assert effs["hist_forecast_transition"] == pd.Timestamp("2025-05-01")
    assert effs["forecast"] == pd.Timestamp("2025-05-04")


def test_missing_scenario_block():
    with pytest.raises(ValueError, match="scenario"):
        Scenario.from_config({"define": {}})


def test_unknown_stitcher(synthetic_dir):
    cfg = load_yaml("synthetic_scenario.yml")
    cfg["scenario"]["series"][0]["stitcher"] = {"name": "nope"}
    with pytest.raises(ValueError, match="Unknown stitcher"):
        Scenario.from_config(cfg).run()


@pytest.mark.integration
def test_example_scenario_from_repository(example_dir):
    sc = Scenario.from_config(load_yaml("scenario.yml"))
    res = sc.run()
    assert set(res) == {"sac", "sjr"}
    assert all(len(v) > 0 for v in res.values())
