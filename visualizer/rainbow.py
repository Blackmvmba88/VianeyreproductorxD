from __future__ import annotations

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from analysis import ReactiveState


class RainbowVisualizer:
    """Matplotlib sine visualizer driven by ReactiveState values."""

    def __init__(self, master) -> None:
        self.figure = Figure(figsize=(9, 4.8), dpi=100, facecolor="#08090d")
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor("#08090d")
        self.ax.set_xlim(0.0, 4.0 * np.pi)
        self.ax.set_ylim(-1.6, 1.6)
        self.ax.axis("off")

        self.x = np.linspace(0.0, 4.0 * np.pi, 1000, dtype=np.float32)
        zeros = np.zeros_like(self.x)

        self.glow_far, = self.ax.plot(self.x, zeros, alpha=0.08, linewidth=14)
        self.glow_near, = self.ax.plot(self.x, zeros, alpha=0.18, linewidth=7)
        self.line, = self.ax.plot(self.x, zeros, linewidth=2.2)

        self.phase = 0.0
        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.widget = self.canvas.get_tk_widget()
        self.canvas.draw_idle()

    def pack(self, **kwargs) -> None:
        self.widget.pack(**kwargs)

    def grid(self, **kwargs) -> None:
        self.widget.grid(**kwargs)

    def render(self, state: ReactiveState, seconds: float, active: bool = True) -> None:
        drive = 1.0 if active else 0.28
        amplitude = 0.12 + state.energy * 0.98 * drive
        carrier = 1.0 + state.bass * 0.55
        harmonic = 0.08 + state.mid * 0.32
        detail = 0.02 + state.high * 0.16

        self.phase += (0.035 + state.high * 0.12 + state.energy * 0.035) * drive

        y = (
            np.sin(self.x * carrier + self.phase) * amplitude
            + np.sin(self.x * 2.0 - self.phase * 0.7) * harmonic
            + np.sin(self.x * 5.0 + self.phase * 1.8) * detail
        )

        hue = (state.centroid * 0.72 + state.mid * 0.18 + seconds * 0.025) % 1.0
        color = self.figure.get_cmap("rainbow")(hue)

        main_width = 1.7 + state.bass * 4.4
        self.line.set_ydata(y)
        self.line.set_color(color)
        self.line.set_linewidth(main_width)

        self.glow_near.set_ydata(y)
        self.glow_near.set_color(color)
        self.glow_near.set_linewidth(main_width + 5.0 + state.energy * 4.0)
        self.glow_near.set_alpha(0.10 + state.energy * 0.14)

        self.glow_far.set_ydata(y)
        self.glow_far.set_color(color)
        self.glow_far.set_linewidth(main_width + 12.0 + state.bass * 8.0)
        self.glow_far.set_alpha(0.035 + state.energy * 0.06)

        self.canvas.draw_idle()
