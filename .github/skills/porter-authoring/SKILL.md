---
name: porter-authoring
description: "Use when designing or implementing a scenarioflow model porter (SCHISM, DSM2, or another model): mapping conceptual inputs to model names, grouping, completeness and compatibility validation, rendering model input files, pass-through inputs, and where porter code should live."
---

# Porter authoring

Porters are **planned, not yet implemented**. The authoritative design is [design/design.rst](../../../design/design.rst), sections "Port the scenario to a model", "Model-independent does not mean lowest common denominator", "Group views and model grouping" and "Near-term implementation priorities". Read them before starting.

## Responsibilities (from the design)

A porter consumes completed conceptual inputs (`Scenario.run()` output) and owns all model knowledge:

- map conceptual inputs to model-specific names and locations;
- group inputs where the model needs grouped output (e.g. all SCHISM flux boundaries together);
- check that required group members are present;
- reject incompatible units, shapes or resolutions that escaped normalization;
- apply model defaults only where intentional and documented;
- write the model input representation.

Proposed interface: `validate()`, `group()`, `write()`.

## Rules

- No model knowledge upstream of the porter. Do not add SCHISM or DSM2 conventions to readers, transforms, `SeriesSpec` or `Scenario`.
- Model-to-concept mapping should live outside the series definitions (e.g. a separate mapping file), so a scenario can be reused by several models.
- Pass-through inputs must be explicit; they are not an escape hatch from validation.
- SCHISM and DSM2 porters are expected to live in downstream packages and be discovered as plugins. Only a trivial reference porter belongs in this package.
- Writing output follows the CLI guide: `--force` to overwrite and `--dry-run` with no side effects.

## Before implementing

The canonical conceptual-input contract (units, resolution, shape, metadata, missing-data rules) is a prerequisite and is not formalized yet. Raise this with the user rather than inventing it inside a porter.
