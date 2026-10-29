---
name: scenario-authoring
description: "Use when writing, reviewing, or debugging a scenarioflow scenario YAML: define block, ${} parameters vs $!{} workspace expressions, data vs function components, load/source/args, transformations, effective dates, stitcher (ts_splice/ts_merge), run order, and recipes such as extending a hindcast to tomorrow or appending a forecast."
---

# Scenario authoring

The user-facing reference is [docsrc/scenario_yaml.rst](../../../docsrc/scenario_yaml.rst). The worked example is [examples/sac_sjr_flux/scenario.yml](../../../examples/sac_sjr_flux/scenario.yml). Read both before answering.

## Mental model

- A **series** is one conceptual input (e.g. `sac` flow). It has ordered **components**.
- `data` components read with a named reader and apply named transforms.
- `function` components build something from earlier outputs: a transition or an extrapolation.
- All `data` components run first, then all `function` components, each group in listed order.
- Outputs are stitched **in listed order**, not run order. List components chronologically.
- `effective` says when a component takes over. With `ts_splice`, the first component is clipped at its own effective time; the others' effective times become the splice `transition` points.

## Substitution

| Syntax | Resolved from | Result |
| --- | --- | --- |
| `${name}` | `define:` then environment | text |
| `$!{expr}` (whole value) | workspace + `days/hours/minutes/pd/math` | the object |
| `...$!{expr}...` (embedded) | same | text |

Workspace names: `<component>` (latest run, may be from another series) and `<series>.<component>` (unambiguous). Prefer the qualified form when a name repeats across series.

`$!{...}` is evaluated when the component runs, so it can only see components that already ran. A data component cannot refer to a function component.

## Recipes

Extend lightly to tomorrow (hold last value):

```yaml
- name: hold
  type: function
  method: extrapolate_ts
  args: {ts: $!{hist}, start: $!{hist.last_valid_index()}, end: ${session_end}, method: ffill}
  effective: $!{hist.last_valid_index()}
```

Append a forecast with a smooth hand-off: a `data` forecast component plus a `transition_ts` function component whose `window` brackets the hand-off; give the transition `effective: <window start>` and the forecast `effective: <window end>`.

Fill beyond a forecast with climatology: `read_climatology` + `apply_climatology(start, end, freq)` with `effective: $!{forecast.last_valid_index()}`.

## Debugging

- Run `sflow plot scenario.yml --series NAME -o out.png -v` and read the INFO log.
- `KeyError: Undefined variable` — a `${}` name is missing from `define:` and the environment.
- `NameError` inside `$!{}` — the referenced component has not run yet or is misspelled.
- A segment missing from the result — check its `effective` and its position in the list.
- `extrapolate_ts` "Cannot infer frequency" — the input series is irregular.

## Keys

- Use `load:`; `load_method:` is accepted as an alias in existing files.
- `load.source` is passed as `source=` to `read_csv`/`read_climatology` and as `fpath=` to other readers.
