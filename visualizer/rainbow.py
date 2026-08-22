from __future__ import annotations

from collections import deque

import numpy as np
from matplotlib import colormaps
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from analysis import ReactiveState
from .effects import PRESETS, StarRain, VisualConfig


class RainbowVisualizer:
    """Reactive neon visualizer with validated presets, trails and star rain."""

    MAX_TRAILS = 12

    def __init__(self, master) -> None:
        self.config = VisualConfig.from_preset("BlackMamba Trip").validated()
        preset = PRESETS[self.config.preset]

        self.figure = Figure(figsize=(9, 4.8), dpi=100, facecolor=preset.background)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(preset.background)
        self.ax.set_xlim(0.0, 4.0 * np.pi)
        self.ax.set_ylim(-1.75, 1.75)
        self.ax.axis("off")

        self.x = np.linspace(0.0, 4.0 * np.pi, 900, dtype=np.float32)
        zeros = np.zeros_like(self.x)

        self.star_rain = StarRain(self.ax)
        self.trail_history: deque[np.ndarray] = deque(maxlen=self.MAX_TRAILS)
        self.trail_lines = []
        for i in range(self.MAX_TRAILS):
            line, = self.ax.plot(self.x, zeros, linewidth=1.3, alpha=0.0, zorder=2 + i * 0.01)
            self.trail_lines.append(line)

        self.glow_far, = self.ax.plot(self.x, zeros, alpha=0.05, linewidth=18, zorder=4)
        self.glow_near, = self.ax.plot(self.x, zeros, alpha=0.12, linewidth=9, zorder=5)
        self.line, = self.ax.plot(self.x, zeros, linewidth=2.4, zorder=6)
        self.secondary, = self.ax.plot(self.x, zeros, linewidth=1.0, alpha=0.0, zorder=3)

        self.phase = 0.0
        self.canvas = FigureCanvasTkAgg(self.figure, master=master)
        self.widget = self.canvas.get_tk_widget()
        self.canvas.draw_idle()

    def pack(self, **kwargs) -> None:
        self.widget.pack(**kwargs)

    def grid(self, **kwargs) -> None:
        self.widget.grid(**kwargs)

    def set_config(self, config: VisualConfig) -> VisualConfig:
        self.config = config.validated()
        preset = PRESETS[self.config.preset]
        self.figure.set_facecolor(preset.background)
        self.ax.set_facecolor(preset.background)
        return self.config

    def apply_preset(self, name: str) -> VisualConfig:
        return self.set_config(VisualConfig.from_preset(name))

    def render(self, state: ReactiveState, seconds: float, active: bool = True) -> None:
        cfg = self.config.validated()
        preset = PRESETS[cfg.preset]
        drive = 1.0 if active else 0.22

        energy = float(np.clip(state.energy, 0.0, 1.0))
        bass = float(np.clip(state.bass, 0.0, 1.0))
        mid = float(np.clip(state.mid, 0.0, 1.0))
        high = float(np.clip(state.high, 0.0, 1.0))
        centroid = float(np.clip(state.centroid, 0.0, 1.0))

        punch = bass * cfg.bass_punch
        amplitude = 0.10 + energy * (0.78 + 0.28 * cfg.bass_punch) * drive
        carrier = 1.0 + punch * 0.42
        harmonic = 0.06 + mid * 0.28
        detail = 0.015 + high * 0.14

        speed = 0.026 + high * 0.105 + energy * 0.035 + cfg.warp * 0.025
        self.phase += speed * drive

        y = (
            np.sin(self.x * carrier + self.phase) * amplitude
            + np.sin(self.x * 2.0 - self.phase * 0.65) * harmonic
            + np.sin(self.x * 5.0 + self.phase * 1.65) * detail
        )

        if cfg.psychedelic:
            bend = 0.07 + energy * 0.12
            y += np.sin(self.x * 0.35 + self.phase * 0.28) * bend
            y *= 1.0 + np.sin(self.x * 0.18 - self.phase * 0.45) * (0.06 + mid * 0.08)

        self.trail_history.appendleft(y.copy())
        visible_trails = min(cfg.trails, len(self.trail_history), self.MAX_TRAILS)
        for i, trail_line in enumerate(self.trail_lines):
            if i < visible_trails:
                trail_y = self.trail_history[i]
                age = (i + 1) / max(visible_trails, 1)
                trail_hue = (
                    centroid * 0.55
                    + mid * 0.17
                    + seconds * 0.018 * cfg.rainbow_speed
                    - age * 0.18
                ) % 1.0
                trail_line.set_ydata(trail_y)
                trail_line.set_color(colormaps[preset.cmap](trail_hue))
                trail_line.set_alpha((1.0 - age) * 0.24 * cfg.glow)
                trail_line.set_linewidth(max(0.5, 2.0 - age * 1.4))
            else:
                trail_line.set_alpha(0.0)

        hue = (
            centroid * 0.58
            + mid * 0.15
            + seconds * 0.025 * cfg.rainbow_speed
            + np.sin(self.phase * 0.35) * 0.035
        ) % 1.0
        color = colormaps[preset.cmap](hue)
        alt_color = colormaps[preset.cmap]((hue + 0.34 + high * 0.1) % 1.0)

        main_width = 1.6 + punch * 3.8
        self.line.set_ydata(y)
        self.line.set_color(color)
        self.line.set_linewidth(main_width)

        glow = cfg.glow
        self.glow_near.set_ydata(y)
        self.glow_near.set_color(color)
        self.glow_near.set_linewidth(main_width + 4.0 + energy * 5.0 * glow)
        self.glow_near.set_alpha(np.clip((0.08 + energy * 0.13) * glow, 0.0, 0.48))

        self.glow_far.set_ydata(y)
        self.glow_far.set_color(color)
        self.glow_far.set_linewidth(main_width + 10.0 + punch * 7.0 + glow * 5.0)
        self.glow_far.set_alpha(np.clip((0.025 + energy * 0.055) * glow, 0.0, 0.28))

        if cfg.psychedelic:
            secondary_y = -y * (0.60 + mid * 0.28) + np.sin(self.x * 3.0 + self.phase) * high * 0.07
            self.secondary.set_ydata(secondary_y)
            self.secondary.set_color(alt_color)
            self.secondary.set_alpha(np.clip(0.12 + energy * 0.20, 0.0, 0.45))
            self.secondary.set_linewidth(0.8 + high * 1.8)
        else:
            self.secondary.set_alpha(0.0)

        self.star_rain.update(cfg, seconds, energy, bass, preset.cmap)

        dim = cfg.background_dim
        self.ax.patch.set_alpha(np.clip(dim, 0.35, 1.0))
        self.canvas.draw_idle()
