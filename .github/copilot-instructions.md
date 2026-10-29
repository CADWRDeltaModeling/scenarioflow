# scenarioflow — Workspace Instructions

Local project rules in [AGENTS.md](../AGENTS.md) take precedence. Read it first.

Organization defaults are in BayDeltaSCHISM https://raw.githubusercontent.com/CADWRDeltaModeling/BayDeltaSCHISM/refs/heads/master/AGENTS.md and apply only where AGENTS.md is silent.

Deeper material is split out of AGENTS.md:

- [docs/PACKAGE_GUIDE.md](docs/PACKAGE_GUIDE.md) — module map and execution flow
- [docs/SOURCE_MAP.md](docs/SOURCE_MAP.md) — key files to read first
- [docs/TESTING_GUIDE.md](docs/TESTING_GUIDE.md) — test layout and invocation
- [docs/CLI_GUIDE.md](docs/CLI_GUIDE.md) — CLI conventions shared across the DMS ecosystem
- `skills/` — `scenario-authoring`, `plugin-authoring` (transforms under active refactoring), `porter-authoring`, `assembly-viewer` (dormant), `documentation`

# Build and Test

The `scenarioflow` conda environment is assumed to exist. Always activate it before running any tests or install commands.

```bash
conda activate scenarioflow
pip install --no-deps -e .
pytest -m "not integration"
```

pytest is configured in `pyproject.toml` (`[tool.pytest.ini_options]`): strict markers, JUnit XML output, `testpaths = ["tests"]`.
