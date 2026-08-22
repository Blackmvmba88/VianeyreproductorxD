from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import librosa
import numpy as np


@dataclass(slots=True)
class ReactiveState:
    energy: float = 0.0
    bass: float = 0.0
    mid: float = 0.0
    high: float = 0.0
    centroid: float = 0.0


class ReactiveAnalyzer:
    """Precomputes lightweight audio features for reactive visuals."""

    def __init__(self, hop_length: int = 1024, n_fft: int = 2048) -> None:
        self.hop_length = hop_length
        self.n_fft = n_fft
        self.path: Path | None = None
        self.duration: float = 0.0
        self.sample_rate: int = 0
        self.times = np.array([0.0], dtype=np.float32)
        self.energy = np.array([0.0], dtype=np.float32)
        self.bass = np.array([0.0], dtype=np.float32)
        self.mid = np.array([0.0], dtype=np.float32)
        self.high = np.array([0.0], dtype=np.float32)
        self.centroid = np.array([0.0], dtype=np.float32)

    @staticmethod
    def _normalize(values: np.ndarray) -> np.ndarray:
        values = np.nan_to_num(values.astype(np.float32), copy=False)
        if not values.size:
            return np.array([0.0], dtype=np.float32)
        ceiling = float(np.percentile(values, 95))
        if ceiling <= 1e-12:
            ceiling = float(np.max(values))
        if ceiling <= 1e-12:
            return np.zeros_like(values, dtype=np.float32)
        return np.clip(values / ceiling, 0.0, 1.0).astype(np.float32)

    @staticmethod
    def _smooth(values: np.ndarray, size: int = 5) -> np.ndarray:
        if values.size < 3:
            return values
        size = min(size, values.size)
        kernel = np.ones(size, dtype=np.float32) / size
        return np.convolve(values, kernel, mode="same").astype(np.float32)

    def load(self, path: str | Path) -> None:
        self.path = Path(path)
        y, sr = librosa.load(self.path, sr=None, mono=True)
        self.sample_rate = int(sr)
        self.duration = float(librosa.get_duration(y=y, sr=sr))

        if y.size == 0:
            raise ValueError("The selected audio file contains no samples.")

        magnitude = np.abs(
            librosa.stft(
                y,
                n_fft=self.n_fft,
                hop_length=self.hop_length,
                center=True,
            )
        )
        freqs = librosa.fft_frequencies(sr=sr, n_fft=self.n_fft)

        rms = librosa.feature.rms(
            y=y,
            frame_length=self.n_fft,
            hop_length=self.hop_length,
            center=True,
        )[0]

        def band_energy(low: float, high: float) -> np.ndarray:
            mask = (freqs >= low) & (freqs < high)
            if not np.any(mask):
                return np.zeros(magnitude.shape[1], dtype=np.float32)
            return np.mean(magnitude[mask], axis=0)

        bass = band_energy(20.0, 250.0)
        mid = band_energy(250.0, 4000.0)
        high = band_energy(4000.0, min(18000.0, sr / 2.0))
        centroid_hz = librosa.feature.spectral_centroid(S=magnitude, sr=sr)[0]

        frame_count = min(
            len(rms), len(bass), len(mid), len(high), len(centroid_hz)
        )
        if frame_count <= 0:
            raise ValueError("Could not extract audio features from this file.")

        self.times = librosa.frames_to_time(
            np.arange(frame_count), sr=sr, hop_length=self.hop_length
        ).astype(np.float32)
        self.energy = self._smooth(self._normalize(rms[:frame_count]))
        self.bass = self._smooth(self._normalize(bass[:frame_count]))
        self.mid = self._smooth(self._normalize(mid[:frame_count]))
        self.high = self._smooth(self._normalize(high[:frame_count]))
        nyquist = max(float(sr) / 2.0, 1.0)
        self.centroid = np.clip(
            centroid_hz[:frame_count] / nyquist, 0.0, 1.0
        ).astype(np.float32)

    def state_at(self, seconds: float) -> ReactiveState:
        if self.times.size == 0:
            return ReactiveState()

        idx = int(np.searchsorted(self.times, max(0.0, seconds), side="right") - 1)
        idx = max(0, min(idx, self.times.size - 1))
        return ReactiveState(
            energy=float(self.energy[idx]),
            bass=float(self.bass[idx]),
            mid=float(self.mid[idx]),
            high=float(self.high[idx]),
            centroid=float(self.centroid[idx]),
        )
