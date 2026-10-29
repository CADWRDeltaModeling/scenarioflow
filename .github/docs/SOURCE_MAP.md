# Source map

Read these first, in order:

1. [design/design.rst](../../design/design.rst) — architecture, terminology, roadmap.
2. [examples/sac_sjr_flux/scenario.yml](../../examples/sac_sjr_flux/scenario.yml) — a complete scenario: history, transition, forecast, climatology/extrapolation.
3. [src/scenarioflow/scenario.py](../../src/scenarioflow/scenario.py) — `Scenario.from_config` maps YAML to objects.
4. [src/scenarioflow/series.py](../../src/scenarioflow/series.py) — run order, workspace publication, effective resolution.
5. [src/scenarioflow/component.py](../../src/scenarioflow/component.py) — reader/transform/function invocation.
6. [src/scenarioflow/expressions.py](../../src/scenarioflow/expressions.py) — `${}` and `$!{}`.
7. [src/scenarioflow/stitch.py](../../src/scenarioflow/stitch.py) — how effective times become splice transitions.
8. [src/scenarioflow/plot_scenario.py](../../src/scenarioflow/plot_scenario.py) — CLI pattern to copy for new commands.
9. [tests/conftest.py](../../tests/conftest.py) — synthetic scenario fixture.
