from __future__ import annotations

import time
from pathlib import Path

import pygame


class AudioPlayer:
    """Small pygame-backed music transport with explicit timeline tracking."""

    def __init__(self) -> None:
        pygame.mixer.init()
        self.path: Path | None = None
        self.duration: float = 0.0
        self.volume: float = 0.8
        self.offset: float = 0.0
        self.started_at: float = 0.0
        self.playing: bool = False
        self.paused: bool = False
        pygame.mixer.music.set_volume(self.volume)

    @property
    def loaded(self) -> bool:
        return self.path is not None

    def load(self, path: str | Path, duration: float) -> None:
        self.stop()
        self.path = Path(path)
        self.duration = max(0.0, float(duration))
        pygame.mixer.music.load(str(self.path))
        self.offset = 0.0

    def _start_at(self, seconds: float) -> None:
        target = max(0.0, min(float(seconds), self.duration or float(seconds)))
        try:
            pygame.mixer.music.play(loops=0, start=target)
        except pygame.error:
            pygame.mixer.music.play(loops=0)
            if target > 0:
                try:
                    pygame.mixer.music.set_pos(target)
                except pygame.error:
                    target = 0.0
        self.offset = target
        self.started_at = time.monotonic()
        self.playing = True
        self.paused = False

    def play_pause(self) -> None:
        if not self.loaded:
            return
        if self.playing and not self.paused:
            self.pause()
        elif self.paused:
            self.resume()
        else:
            if self.duration > 0 and self.offset >= self.duration - 0.05:
                self.offset = 0.0
            self._start_at(self.offset)

    def play(self) -> None:
        if self.loaded:
            if self.duration > 0 and self.offset >= self.duration - 0.05:
                self.offset = 0.0
            self._start_at(self.offset)

    def pause(self) -> None:
        if not self.playing or self.paused:
            return
        self.offset = self.position
        pygame.mixer.music.pause()
        self.paused = True

    def resume(self) -> None:
        if not self.playing or not self.paused:
            return
        pygame.mixer.music.unpause()
        self.started_at = time.monotonic()
        self.paused = False

    def stop(self) -> None:
        pygame.mixer.music.stop()
        self.offset = 0.0
        self.started_at = 0.0
        self.playing = False
        self.paused = False

    def seek(self, seconds: float) -> None:
        if not self.loaded:
            return
        target = max(0.0, min(float(seconds), self.duration))
        was_paused = self.paused
        self._start_at(target)
        if was_paused:
            self.pause()

    def set_volume(self, value: float) -> None:
        self.volume = max(0.0, min(float(value), 1.0))
        pygame.mixer.music.set_volume(self.volume)

    @property
    def position(self) -> float:
        if not self.loaded:
            return 0.0
        if self.paused or not self.playing:
            return max(0.0, min(self.offset, self.duration))
        pos = self.offset + (time.monotonic() - self.started_at)
        return max(0.0, min(pos, self.duration))

    def update_finished_state(self) -> bool:
        """Returns True once when playback naturally reaches the end."""
        if not self.playing or self.paused:
            return False
        if self.duration > 0 and self.position >= self.duration - 0.03:
            self.offset = self.duration
            self.playing = False
            return True
        if not pygame.mixer.music.get_busy() and self.position > 0.1:
            self.offset = min(self.position, self.duration)
            self.playing = False
            return True
        return False

    def close(self) -> None:
        self.stop()
        pygame.mixer.quit()
