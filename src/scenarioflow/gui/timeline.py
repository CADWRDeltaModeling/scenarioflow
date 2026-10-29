"""Interactive "Assembly Preview" mock (matplotlib).

A single audio-track style ribbon shows which component is used at each time,
with draggable boundaries between regions. A toggle switches the time-series
panel between the assembled final series and the individual component series.
"""

import logging

import matplotlib.pyplot as plt
import pandas as pd

from scenarioflow.plot import _plot_one_series

logger = logging.getLogger(__name__)


def _extent(s):
    """First/last timestamp of a component series (handles PeriodIndex)."""
    idx = s.index
    if isinstance(idx, pd.PeriodIndex):
        idx = idx.to_timestamp()
    return pd.Timestamp(idx.min()), pd.Timestamp(idx.max())


class TrackTimeline:
    """Audio-track style assembly preview (GUI mock).

    A single ribbon shows which component is in use over time. Adjacent regions
    share a boundary (the effective/transition time of the right-hand
    component); dragging a boundary adjusts that transition and the two regions
    stay snapped together. A toggle switches the time-series panel between the
    assembled ``final`` series and the individual ``component`` series.
    """

    MIN_WIDTH_FRAC = 0.005  # smallest allowed region width, as a fraction of span

    def __init__(self, sname, comp_series, effectives, final_series,
                 scenario_start, scenario_end):
        import matplotlib.dates as mdates
        from matplotlib.widgets import Button
        from matplotlib.patches import Rectangle
        self._mdates = mdates
        self._Rectangle = Rectangle

        self.sname = sname
        self.comp_series = comp_series
        self.final_series = final_series
        self.scenario_start = scenario_start
        self.scenario_end = scenario_end
        self.mode = "component"          # or "final"
        self._drag = None                # index of boundary being dragged

        cmap = plt.get_cmap("tab10")

        # Order components chronologically by effective time (fallback: data start).
        items = []
        for i, (nm, s) in enumerate(comp_series.items()):
            s0, s1 = _extent(s)
            eff = effectives.get(nm)
            eff_num = mdates.date2num(pd.Timestamp(eff)) if eff is not None else mdates.date2num(s0)
            items.append((eff_num, nm, mdates.date2num(s0), mdates.date2num(s1), cmap(i % 10)))
        items.sort(key=lambda t: t[0])

        self.names = [it[1] for it in items]
        self.colors = [it[4] for it in items]
        n = len(items)

        # Track extent from the scenario window (fallback to data span).
        starts = [it[2] for it in items]
        ends = [it[3] for it in items]
        t_start = (mdates.date2num(pd.Timestamp(scenario_start))
                   if scenario_start is not None else min(starts))
        t_end = (mdates.date2num(pd.Timestamp(scenario_end))
                 if scenario_end is not None else max(ends))

        # boundaries[0]=track start, boundaries[i]=effective of region i, boundaries[n]=track end
        self.boundaries = [t_start]
        for k in range(1, n):
            self.boundaries.append(items[k][0])
        self.boundaries.append(t_end)
        # Keep boundaries sorted and inside the track window.
        for k in range(1, n):
            self.boundaries[k] = min(max(self.boundaries[k], t_start), t_end)
        self.boundaries[1:n] = sorted(self.boundaries[1:n])

        # --- Figure layout: time series (top), track ribbon (bottom) ---
        self.fig = plt.figure(figsize=(14, 7))
        self.fig.subplots_adjust(left=0.07, right=0.98, top=0.94, bottom=0.16, hspace=0.30)
        gs = self.fig.add_gridspec(2, 1, height_ratios=[4, 1])
        self.ax_data = self.fig.add_subplot(gs[0])
        self.ax_track = self.fig.add_subplot(gs[1], sharex=self.ax_data)

        # Track ribbon.
        self.ax_track.set_ylim(0, 1)
        self.ax_track.set_yticks([])
        self.ax_track.set_xlabel("Time")
        self.ax_track.set_title("Assembly track — drag the boundaries between regions")
        self.ax_track.xaxis_date()

        self.regions = []       # Rectangle per region
        self.labels = []        # Text per region
        for r in range(n):
            rect = self._Rectangle(
                (self.boundaries[r], 0.0), self.boundaries[r + 1] - self.boundaries[r], 1.0,
                facecolor=self.colors[r], edgecolor="black", linewidth=1.2, alpha=0.75,
            )
            self.ax_track.add_patch(rect)
            self.regions.append(rect)
            txt = self.ax_track.text(
                0.5 * (self.boundaries[r] + self.boundaries[r + 1]), 0.5, self.names[r],
                ha="center", va="center", fontsize=9, clip_on=True)
            self.labels.append(txt)

        # Boundary handle lines on the ribbon and on the data panel.
        self._bound_lines_track = []
        self._bound_lines_top = []
        for k in range(1, n):
            self._bound_lines_track.append(
                self.ax_track.axvline(self.boundaries[k], color="black", linewidth=1.5))

        # Draw the top panel and its boundary lines.
        self._draw_top()

        # Toggle button.
        ax_btn = self.fig.add_axes([0.07, 0.02, 0.16, 0.06])
        self._btn_toggle = Button(ax_btn, "Show: component")
        self._btn_toggle.on_clicked(self._on_toggle)

        # Events.
        self.fig.canvas.mpl_connect("button_press_event", self._on_press)
        self.fig.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self.fig.canvas.mpl_connect("button_release_event", self._on_release)

    # ---- helpers ----
    def _num_to_ts(self, x):
        return pd.Timestamp(self._mdates.num2date(x)).tz_convert(None)

    def _draw_top(self):
        """(Re)draw the time-series panel for the current mode, keeping x-lims."""
        try:
            xlim = self.ax_data.get_xlim()
        except Exception:
            xlim = None
        self.ax_data.clear()
        if self.mode == "final":
            if self.final_series is not None:
                fs = self.final_series
                idx = fs.index.to_timestamp() if isinstance(fs.index, pd.PeriodIndex) else fs.index
                self.ax_data.plot(idx, fs.values, "-", linewidth=2, color="black",
                                  label=f"{self.sname} (final)")
            self.ax_data.set_title(f"Series '{self.sname}' — assembled final")
            self.ax_data.set_ylabel("Value")
            self.ax_data.grid(True, linestyle="--", linewidth=0.5)
            self.ax_data.legend(fontsize=8)
        else:
            _plot_one_series(self.ax_data, self.sname, self.comp_series, None,
                             self.scenario_start, self.scenario_end)
        # Boundary lines on top, colour-matched to the region on their right.
        self._bound_lines_top = []
        for k in range(1, len(self.regions)):
            self._bound_lines_top.append(
                self.ax_data.axvline(self.boundaries[k], color=self.colors[k],
                                     linestyle=":", linewidth=1.2, alpha=0.8))
        if xlim is not None:
            self.ax_data.set_xlim(xlim)

    def _nearest_boundary(self, x):
        lo, hi = self.ax_track.get_xlim()
        thresh = (hi - lo) * 0.01
        best, bestd = None, thresh
        for k in range(1, len(self.regions)):
            d = abs(self.boundaries[k] - x)
            if d < bestd:
                bestd, best = d, k
        return best

    def _set_boundary(self, k, x):
        lo, hi = self.boundaries[0], self.boundaries[-1]
        min_w = (hi - lo) * self.MIN_WIDTH_FRAC
        x = min(max(x, self.boundaries[k - 1] + min_w), self.boundaries[k + 1] - min_w)
        self.boundaries[k] = x
        # Left region (k-1) new right edge; right region (k) new left edge.
        left = self.regions[k - 1]
        left.set_width(self.boundaries[k] - self.boundaries[k - 1])
        right = self.regions[k]
        right.set_x(self.boundaries[k])
        right.set_width(self.boundaries[k + 1] - self.boundaries[k])
        for idx in (k - 1, k):
            self.labels[idx].set_x(0.5 * (self.boundaries[idx] + self.boundaries[idx + 1]))
        self._bound_lines_track[k - 1].set_xdata([x, x])
        if k - 1 < len(self._bound_lines_top):
            self._bound_lines_top[k - 1].set_xdata([x, x])

    # ---- event handlers ----
    def _on_press(self, event):
        if event.inaxes is not self.ax_track or event.xdata is None:
            return
        self._drag = self._nearest_boundary(event.xdata)

    def _on_motion(self, event):
        if self._drag is None or event.inaxes is not self.ax_track or event.xdata is None:
            return
        self._set_boundary(self._drag, event.xdata)
        self.fig.canvas.draw_idle()

    def _on_release(self, _event):
        if self._drag is not None:
            logger.info(self._table_text())
        self._drag = None

    def _on_toggle(self, _evt):
        self.mode = "final" if self.mode == "component" else "component"
        self._btn_toggle.label.set_text(f"Show: {self.mode}")
        self._draw_top()
        self.fig.canvas.draw_idle()

    # ---- reporting ----
    def _fmt(self, num):
        return self._num_to_ts(num).strftime("%Y-%m-%d %H:%M")

    def _table_text(self):
        lines = [f"[{self.sname}] track regions:"]
        for r, nm in enumerate(self.names):
            lines.append(f"  {nm}: {self._fmt(self.boundaries[r])} -> "
                         f"{self._fmt(self.boundaries[r + 1])}")
        return "\n".join(lines)
