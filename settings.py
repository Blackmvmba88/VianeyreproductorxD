from __future__ import annotations

from dataclasses import dataclass
import math
import os
from pathlib import Path

from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env", override=False)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "on", "y"}:
        return True
    if value in {"0", "false", "no", "off", "n"}:
        return False
    return default


def _env_float(name: str, default: float, low: float, high: float) -> float:
    try:
        value = float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        value = default
    if not math.isfinite(value):
        value = default
    return max(low, min(value, high))


def _env_int(name: str, default: int, low: int, high: int) -> int:
    try:
        raw = float(os.getenv(name, str(default)))
        value = int(raw) if math.isfinite(raw) else default
    except (TypeError, ValueError, OverflowError):
        value = default
    return max(low, min(value, high))


@dataclass(slots=True, frozen=True)
class RuntimeSettings:
    preset: str
    star_rain: bool
    psychedelic: bool
    glow: float
    trails: int
    warp: float
    bass_punch: float
    particles: int
    rainbow_speed: float
    background_dim: float
    volume: float
    target_fps: int


def load_settings() -> RuntimeSettings:
    return RuntimeSettings(
        preset=os.getenv("VIANEY_PRESET", "BlackMamba Trip").strip() or "BlackMamba Trip",
        star_rain=_env_bool("VIANEY_STAR_RAIN", True),
        psychedelic=_env_bool("VIANEY_PSYCHEDELIC", True),
        glow=_env_float("VIANEY_GLOW", 1.70, 0.0, 2.5),
        trails=_env_int("VIANEY_TRAILS", 10, 0, 12),
        warp=_env_float("VIANEY_WARP", 1.45, 0.0, 2.5),
        bass_punch=_env_float("VIANEY_BASS_PUNCH", 1.70, 0.0, 2.5),
        particles=_env_int("VIANEY_PARTICLES", 280, 0, 320),
        rainbow_speed=_env_float("VIANEY_RAINBOW_SPEED", 0.82, 0.0, 2.0),
        background_dim=_env_float("VIANEY_BACKGROUND_DIM", 0.67, 0.35, 1.0),
        volume=_env_float("VIANEY_VOLUME", 0.80, 0.0, 1.0),
        target_fps=_env_int("VIANEY_FPS", 30, 15, 60),
    )
