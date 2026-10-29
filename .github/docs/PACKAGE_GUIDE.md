# Package guide

## Layout

`src` layout; the importable package is `src/scenarioflow/`.

| Module | Role |
| --- | --- |
| `__init__.py` | Public API: `Scenario`, `SeriesSpec`, `Component`, `load_yaml`, `__version__` |
| `__main__.py` | `sflow` Click group |
| `config.py` | `load_yaml` (OmegaConf, interpolation not resolved) |
| `expressions.py` | `${...}` / `$!{...}` substitution and restricted `eval` |
| `scenario.py` | `Scenario`: series list, shared defines/workspace, `from_config` |
| `series.py` | `SeriesSpec`: runs components and stitches them |
| `component.py` | `Component`: `data` (reader + transforms) or `function` |
| `stitch.py` | `_stitch_ts`: `ts_splice` / `ts_merge` dispatch |
| `builtins/readers.py` | `DEFAULT_READERS` |
| `builtins/transforms.py` | `DEFAULT_TRANSFORMS` |
| `builtins/functions.py` | `DEFAULT_FUNCTIONS` |
| `plot.py` | Static matplotlib plot helpers, `_collect_effectives` |
| `gui/timeline.py` | `TrackTimeline` Assembly Preview mock (matplotlib widgets) |
| `plot_scenario.py` | `sflow plot` CLI and `plot_scenario()` work function |
| `cli_common.py` | Shared logging options and setup |
| `logging_config.py` | Copy of `dms_datastore.logging_config` |

## Execution flow

```text
load_yaml(path)
  -> Scenario.from_config(cfg, extra_namespace=None)
       define -> defines; scenario.series -> SeriesSpec[Component]
  -> Scenario.run()
       for each SeriesSpec:
         data components (listed order)     -> reader(**args) -> transforms -> DataFrame
         function components (listed order) -> function(**args)
         each output -> workspace["<comp>"] and workspace["<series>.<comp>"]
         resolve each component's effective (${}/$!{})
         _stitch_ts(outputs in listed order, stitcher, effective points)
  -> {series_name: final DataFrame}
```

Substitution happens per component, immediately before it runs, so `$!{...}` can only see outputs already in the workspace.

## Extension points (current)

Readers, transforms and functions are dictionaries on `Scenario`. Add entries through `Scenario.from_config(cfg, extra_namespace={"readers": {...}, "transforms": {...}, "functions": {...}})`.

## Planned (see design/design.rst)

Plugin registry with entry-point discovery, model porters with `validate()/group()/write()`, canonical conceptual-input contract, construction lineage, Panel GUI with registered viewers.
