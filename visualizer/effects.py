from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from matplotlib import colormaps


def _safe_float(value, default: float, low: float, high: float) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = default
    if not math.isfinite(number):
        number = default
    return max(low, min(number, high))


def _safe_int(value, default: int, low: int, high: int) -> int:
    try:
        number = float(value)
        integer = int(number) if math.isfinite(number) else default
    except (TypeError, ValueError, OverflowError):
        integer = default
    return max(low, min(integer, high))


@dataclass(slots=True, frozen=True)
class VisualPreset:
    name: str
    background: str
    cmap: str
    glow: float
    trails: int
    warp: float
    bass_punch: float
    particles: int
    rainbow_speed: float
    background_dim: float
    psychedelic: bool
    star_rain: bool


PRESETS: dict[str, VisualPreset] = {
    "Neon Abyss": VisualPreset("Neon Abyss", "#05040b", "cool", 1.15, 5, 0.85, 1.05, 150, 0.35, 0.82, False, True),
    "Rainbow Warp": VisualPreset("Rainbow Warp", "#03030a", "rainbow", 1.45, 8, 1.65, 1.45, 240, 1.15, 0.70, True, True),
    "Toxic Dream": VisualPreset("Toxic Dream", "#020805", "turbo", 1.35, 6, 1.15, 1.25, 190, 0.70, 0.76, True, True),
    "BlackMamba Trip": VisualPreset("BlackMamba Trip", "#020307", "hsv", 1.70, 10, 1.45, 1.70, 280, 0.82, 0.67, True, True),
}


@dataclass(slots=True)
class VisualConfig:
    preset: str = "BlackMamba Trip"
    glow: float = 1.70
    trails: int = 10
    warp: float = 1.45
    bass_punch: float = 1.70
    particles: int = 280
    rainbow_speed: float = 0.82
    background_dim: float = 0.67
    psychedelic: bool = True
    star_rain: bool = True

    @classmethod
    def from_preset(cls, name: str) -> "VisualConfig":
        p = PRESETS.get(name, PRESETS["BlackMamba Trip"])
        return cls(
            preset=p.name,
            glow=p.glow,
            trails=p.trails,
            warp=p.warp,
            bass_punch=p.bass_punch,
            particles=p.particles,
            rainbow_speed=p.rainbow_speed,
            background_dim=p.background_dim,
            psychedelic=p.psychedelic,
            star_rain=p.star_rain,
        )

    def validated(self) -> "VisualConfig":
        preset = self.preset if self.preset in PRESETS else "BlackMamba Trip"
        return VisualConfig(
            preset=preset,
            glow=_safe_float(self.glow, 1.70, 0.0, 2.5),
            trails=_safe_int(self.trails, 10, 0, 12),
            warp=_safe_float(self.warp, 1.45, 0.0, 2.5),
            bass_punch=_safe_float(self.bass_punch, 1.70, 0.0, 2.5),
            particles=_safe_int(self.particles, 280, 0, 320),
            rainbow_speed=_safe_float(self.rainbow_speed, 0.82, 0.0, 2.0),
            background_dim=_safe_float(self.background_dim, 0.67, 0.35, 1.0),
            psychedelic=bool(self.psychedelic),
            star_rain=bool(self.star_rain),
        )


class StarRain:
    """Preallocated neon particle field; updates artist data without recreating it."""

    MAX_PARTICLES = 320

    def __init__(self, ax, seed: int = 88) -> None:
        self.ax = ax
        self.rng = np.random.default_rng(seed)
        self.x = self.rng.uniform(0.0, 4.0 * np.pi, self.MAX_PARTICLES)
        self.y = self.rng.uniform(-1.7, 1.9, self.MAX_PARTICLES)
        self.speed = self.rng.uniform(0.006, 0.030, self.MAX_PARTICLES)
        self.depth = self.rng.uniform(0.25, 1.0, self.MAX_PARTICLES)
        self.phase = self.rng.uniform(0.0, 2.0 * np.pi, self.MAX_PARTICLES)
        self.artist = ax.scatter([], [], s=[], alpha=0.0, linewidths=0, zorder=1)

    def update(self, config: VisualConfig, seconds: float, energy: float, bass: float, cmap_name: str) -> None:
        cfg = config.validated()
        count = cfg.particles if cfg.star_rain else 0
        if count <= 0:
            self.artist.set_offsets(np.empty((0, 2)))
            self.artist.set_sizes(np.empty(0))
            self.artist.set_alpha(0.0)
            return

        idx = slice(0, count)
        safe_seconds = _safe_float(seconds, 0.0, 0.0, 10**9)
        safe_energy = _safe_float(energy, 0.0, 0.0, 1.0)
        safe_bass = _safe_float(bass, 0.0, 0.0, 1.0)
        drive = 0.45 + cfg.warp * 0.95 + safe_energy * 1.25 + safe_bass * 0.65
        self.y[idx] -= self.speed[idx] * drive
        self.x[idx] += np.sin(safe_seconds * 0.45 + self.phase[idx]) * 0.0008 * (1.0 + cfg.warp)

        reset = self.y[idx] < -1.85
        if np.any(reset):
            local = np.flatnonzero(reset)
            self.y[local] = self.rng.uniform(1.65, 1.95, len(local))
            self.x[local] = self.rng.uniform(0.0, 4.0 * np.pi, len(local))
            self.depth[local] = self.rng.uniform(0.25, 1.0, len(local))

        offsets = np.column_stack((self.x[idx], self.y[idx]))
        sizes = 2.0 + self.depth[idx] * (9.0 + cfg.warp * 8.0) + safe_energy * 6.0
        hue = (self.depth[idx] * 0.55 + safe_seconds * 0.035 * cfg.rainbow_speed) % 1.0
        colors = colormaps[cmap_name](hue)
        colors[:, 3] = np.clip(0.18 + self.depth[idx] * 0.58 + safe_energy * 0.15, 0.0, 0.92)

        self.artist.set_offsets(offsets)
        self.artist.set_sizes(sizes)
        self.artist.set_facecolors(colors)
        self.artist.set_alpha(1.0)
