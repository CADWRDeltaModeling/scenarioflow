---
name: plugin-authoring
description: "Use when adding or changing a scenarioflow reader, transform, function (transition/extrapolation), or stitcher: call signatures, where built-ins live, registering through extra_namespace, tests, and documentation. Also use when planning the entry-point plugin registry described in the design."
---

# Plugin authoring

> **Transforms are under active, extensive refactoring.** The transform table and call contract below describe the current code, not a target design. Before changing transforms, confirm the intended contract with the user. Don't treat existing transform names or signatures as compatibility constraints unless the user says so. When results change on purpose, update `tests/test_scenario.py` and `CHANGELOG.rst` together.

## Current mechanism

Built-ins are dictionaries:

| Kind | Table | Call signature |
| --- | --- | --- |
| Reader | `builtins/readers.py` `DEFAULT_READERS` | `reader(**load.args)`, plus `source=` or `fpath=` (see below) |
| Transform | `builtins/transforms.py` `DEFAULT_TRANSFORMS` | `fn(ts, **args)` returns the transformed data |
| Function | `builtins/functions.py` `DEFAULT_FUNCTIONS` | `fn(**args)`, keyword-only |
| Stitcher | `stitch.py` `_stitch_ts` | `ts_splice` / `ts_merge` only; other names raise `ValueError` |

`load.source` is passed as `source=` to `read_csv` and `read_climatology` and as `fpath=` to all other readers (see `Component.run`). A new file reader whose path argument is `fpath` needs no special handling.

Data component output is passed through `vtools.data.timeseries.to_dataframe`, so readers and transforms may return a Series or a DataFrame.

User code adds implementations without modifying the package:

```python
sc = Scenario.from_config(cfg, extra_namespace={
    "readers": {"read_mine": read_mine},
    "transforms": {"my_transform": my_transform},
    "functions": {"my_function": my_function},
})
```

## Adding a built-in

1. Implement with a NumPy-style docstring. Delegate to `vtools` or `dms_datastore` rather than reimplementing algorithms.
2. Accept and ignore extra keyword arguments (`**_`) only when the existing built-ins of that kind do.
3. Add it to the `DEFAULT_*` table.
4. Add a test on synthetic data in `tests/`.
5. Document it under the matching "Built-in ..." heading in `docsrc/scenario_yaml.rst`.

Do not add model-specific (SCHISM, DSM2) logic to readers or transforms; that belongs to porters.

## Planned registry

[design/design.rst](../../../design/design.rst) ("Extension model", "Plugin metadata") proposes registries for readers, transforms, functions/stitchers, porters and viewers, discovered through entry-point groups such as `scenarioflow.readers`, with metadata (name, callable, parameter schema, description, output type, viewer). Implementing it is a separate task. Confirm scope with the user, and keep `extra_namespace` working or provide a migration path.
