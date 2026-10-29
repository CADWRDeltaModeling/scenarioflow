---
name: assembly-viewer
description: "Use when working on scenarioflow visual inspection: the matplotlib Assembly Preview mock (TrackTimeline), sflow plot --gui, static component plots, and the planned Panel/Bokeh GUI with Final/Components modes, assembly track, group views and registered viewers."
---

# Assembly viewer

## Current implementation

- `src/scenarioflow/plot.py` — `_plot_one_series` draws components and the final series; `_collect_effectives` resolves effective times for display.
- `src/scenarioflow/gui/timeline.py` — `TrackTimeline`, a matplotlib-widgets mock:
  - top panel: components or final series, toggled by a button (`mode` is `"component"` or `"final"`);
  - bottom ribbon: one region per component, ordered by effective time; boundaries are draggable (`_set_boundary`);
  - `_table_text()` reports region extents and is logged on mouse release.
- `sflow plot CONFIG --gui` opens one timeline per series.
- Dragging boundaries is **display only**; it does not change the scenario or write YAML.

Testing: use the `Agg` backend and drive the object directly (`_set_boundary`, `_on_toggle`), as in `tests/test_cli.py::test_track_timeline`. `design/gui_smoke.py` is a manual script against the repository example.

## Planned GUI (see design/design.rst, "Inspection and GUI design")

- Panel/Bokeh frontend; editor and inspector for the same YAML, not a separate configuration system.
- Layout: navigation (group → conceptual input → component), one active viewer, inspector.
- Standard time-series assembly viewer with **Final** and **Components** modes, both showing the assembly track and transition windows.
- Group views show coverage and validation status, not every member plotted at once.
- Registered viewers attach to conceptual input types or groups (e.g. mixed-type structure viewer, source/sink navigator), not to readers.
- Show construction lineage, never a claim of pointwise provenance.

## Rules

- Keep Panel/Bokeh imports inside `gui/` so the core does not require them; adding them as dependencies is a decision for the user.
- Do not put domain-specific visualization logic in the core.
- Do not use `print`; log through `logging.getLogger(__name__)`.
