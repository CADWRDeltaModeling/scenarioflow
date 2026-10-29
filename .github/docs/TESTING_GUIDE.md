# Testing guide

## Environment

The `scenarioflow` conda environment is assumed to exist. Activate it before installing or testing.

```bash
conda activate scenarioflow
pip install --no-deps -e .
```

## Suites

| File | Covers |
| --- | --- |
| `tests/test_expressions.py` | `${}` / `$!{}` substitution, restricted eval |
| `tests/test_scenario.py` | Scenario assembly on synthetic data; repository example (`integration`) |
| `tests/test_cli.py` | `sflow` help/version, `sflow plot` output, Assembly Preview mock (non-interactive) |

```bash
pytest -m "not integration"   # CI subset
pytest                        # includes repository-backed example
```

## Fixtures

- `synthetic_dir` copies `tests/data/synthetic_scenario.yml`, `forecast.csv` and `sac_climate.csv` to `tmp_path`, generates a 15-minute `hist.csv`, and `chdir`s there. Scenario paths are relative to the working directory.
- `example_dir` `chdir`s to `examples/sac_sjr_flux` (repository access required).

## Conventions

- Use `tmp_path` and `monkeypatch`; do not write into the source tree.
- Mark tests that require web connectivity or the `dms_datastore` repository as `integration`.
- matplotlib uses the `Agg` backend (set in `conftest.py`).
- `design/gui_smoke.py` is a manual script, not part of the suite.

## pytest configuration

Configured in `[tool.pytest.ini_options]` of [pyproject.toml](../../pyproject.toml): strict markers, JUnit XML output, `testpaths = ["tests"]`.
