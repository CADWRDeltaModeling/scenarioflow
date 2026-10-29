# scenarioflow agent guidance

`scenarioflow` assembles time-dependent model inputs from ordered components — historical archives, real-time or provisional data, forecasts, climatology and planning assumptions — spliced in time at explicit effective dates.

The architecture and its direction are described in [design/design.rst](design/design.rst). Read it before structural work.

## Current focus

- **Transforms are being refactored extensively.** Expect changes to transform names, signatures and the transform contract. Treat the current `builtins/transforms.py` interface as provisional, not as a compatibility constraint, unless the user says otherwise.
- **The GUI is dormant.** Do not modify, extend or refactor `src/scenarioflow/gui/`, the `--gui` option, or GUI-oriented design unless the user explicitly asks. Keep it importable and its existing test passing when other changes touch shared code (e.g. `plot.py`).

## Package role

The core rule from the design:

> Readers know sources. Transforms know data operations. Scenario assembly knows time and precedence. Porters know models.

- `scenarioflow` is not a SCHISM or DSM2 package. Model-specific knowledge belongs in porters, which are planned for downstream packages.
- Keep YAML the durable, reviewable representation. A GUI or CLI edits and inspects that representation; it is not a separate configuration system.

## Dependency policy

- Depends on `vtools` and `dms_datastore`.
- Assume the established scientific Python stack is available.
- Do not program indirect dependencies on HEC-DSS.
- Do not add spatial or plotting dependencies without a specific need. Plotting uses matplotlib.

## Coding practice

- Plan before coding.
- Keep functions single-purpose.
- Keep functions testable.
- Do not refactor outside the scope of the requested work. Alert the user if broader refactoring appears warranted.
- Do not contract existing documentation.
- Preserve NumPy-style documentation; repair it when interfaces change.
- Prefer explicit errors such as `ValueError` over elaborate recovery from invalid arguments.
- Prefer failure to robustification and silent passes.
- Avoid making inference from surrounding files the only way to use an API. Important inputs should also be supplyable explicitly.
- Assume the established tool stack exists; do not add elaborate defensive discovery for expected dependencies.
- Preserve the behavior of scenario assembly unless the change is the point of the task. The package was lifted from a prototype without behavior change; tests in `tests/test_scenario.py` pin it. When a transform refactor changes results intentionally, update those tests deliberately and record the change in `CHANGELOG.rst`.

## Time-series dependencies

Use `vtools` rather than reimplementing:

- `ts_splice` / `ts_merge` for stitching
- `transition_ts` for transitions
- `rhistinterp` for mean-preserving interpolation of period averages
- `apply_climatology`
- `convert_units`

Use lower-case frequency strings: `min`, `h`, `d`, `s`.

Repository data is read through `dms_datastore` (`read_ts`, `read_ts_repo`). Do not turn off `force_regular` to make an error go away.

## Command-line interfaces

When creating, modifying, reviewing, or documenting a command-line interface, follow [.github/docs/CLI_GUIDE.md](.github/docs/CLI_GUIDE.md).

- Commands are Click subcommands of the `sflow` group in `src/scenarioflow/__main__.py`.
- Each command module has a `<tool>_cli()` entry point and a work function with explicit named arguments.
- Use the shared `logging_options` decorator and `setup_logging()` from `cli_common.py`.

## Logging

- Every module: `logger = logging.getLogger(__name__)`. No `print` in library code.
- Configure logging only at CLI entry points, via `scenarioflow.logging_config` (same machinery as `dms_datastore.logging_config`).
- The package adds a `NullHandler`; library users configure logging themselves.

## Testing

- Use `pytest`.
- Mark tests requiring network access or the `dms_datastore` repository as `integration`.
- GitHub Actions excludes `integration`; user-launched runs may include it.
- Use `tmp_path` and `monkeypatch.chdir`; scenario paths are relative to the working directory.

See [.github/docs/TESTING_GUIDE.md](.github/docs/TESTING_GUIDE.md).

## Specialized knowledge

| Topic | Where |
| --- | --- |
| Module map and execution flow | [.github/docs/PACKAGE_GUIDE.md](.github/docs/PACKAGE_GUIDE.md) |
| Key files to read first | [.github/docs/SOURCE_MAP.md](.github/docs/SOURCE_MAP.md) |
| Test layout and invocation | [.github/docs/TESTING_GUIDE.md](.github/docs/TESTING_GUIDE.md) |
| CLI conventions | [.github/docs/CLI_GUIDE.md](.github/docs/CLI_GUIDE.md) |
| Writing or debugging scenario YAML | `scenario-authoring` skill |
| Adding readers, transforms, functions or stitchers | `plugin-authoring` skill |
| Model porters (planned) | `porter-authoring` skill |
| Assembly Preview and GUI viewers (dormant; only on explicit request) | `assembly-viewer` skill |
| Sphinx documentation | `documentation` skill |
