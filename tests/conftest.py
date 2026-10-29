import shutil
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import pytest

matplotlib.use("Agg")

DATA = Path(__file__).parent / "data"
EXAMPLE = Path(__file__).parents[1] / "examples" / "sac_sjr_flux"


def _write_hist(path):
    idx = pd.date_range("2025-03-01", "2025-06-15", freq="15min")
    t = np.arange(len(idx))
    df = pd.DataFrame({"sac": 20000 + 5000 * np.sin(t / 400.0),
                       "sjr": 1500 + 300 * np.cos(t / 300.0)}, index=idx)
    df.index.name = "datetime"
    df.to_csv(path, float_format="%.4f")


@pytest.fixture
def synthetic_dir(tmp_path, monkeypatch):
    """Working directory holding the synthetic scenario and its inputs.

    Scenario paths are relative, so the test runs from this directory.
    """
    for name in ("synthetic_scenario.yml", "forecast.csv", "sac_climate.csv"):
        shutil.copy(DATA / name, tmp_path / name)
    _write_hist(tmp_path / "hist.csv")
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def example_dir(monkeypatch):
    monkeypatch.chdir(EXAMPLE)
    return EXAMPLE
