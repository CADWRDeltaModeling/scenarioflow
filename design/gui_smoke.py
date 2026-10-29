"""Manual smoke check of the Assembly Preview mock; writes gui_track_test.png.

Run from examples/sac_sjr_flux (requires repository access):

    python ../../design/gui_smoke.py
"""
import matplotlib
matplotlib.use("Agg")
import pandas as pd
import matplotlib.dates as md

from scenarioflow import Scenario, load_yaml
from scenarioflow.gui.timeline import TrackTimeline
from scenarioflow.plot import _collect_effectives

cfg = load_yaml("scenario.yml")
sc = Scenario.from_config(cfg)
res = sc.run()
ss = sc.series[0]

cd = {}
for c in ss.components:
    out = sc.workspace.get(f"{ss.name}.{c.name}")
    if out is None:
        out = sc.workspace.get(c.name)
    if out is None:
        continue
    if hasattr(out, "shape") and getattr(out, "ndim", 1) == 2 and out.shape[1] == 1:
        out = out.iloc[:, 0]
    cd[c.name] = out

eff = _collect_effectives(ss, sc)
fin = res[ss.name]
if hasattr(fin, "shape") and getattr(fin, "ndim", 1) == 2 and fin.shape[1] == 1:
    fin = fin.iloc[:, 0]

t = TrackTimeline(
    ss.name, cd, eff, fin,
    pd.to_datetime(cfg["define"]["session_start"]),
    pd.to_datetime(cfg["define"]["session_end"]),
)
print(t._table_text())
t._set_boundary(1, md.date2num(pd.Timestamp("2025-05-15")))
print("after drag boundary 1:")
print(t._table_text())
t._on_toggle(None)
print("mode =", t.mode)
t._on_toggle(None)
print("mode =", t.mode)
t.fig.savefig("gui_track_test.png", dpi=80)
print("OK")
