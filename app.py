from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pygame

from analysis import ReactiveAnalyzer, ReactiveState
from player import AudioPlayer
from visualizer import RainbowVisualizer


AUDIO_TYPES = [
    ("Audio files", "*.mp3 *.wav *.ogg *.flac"),
    ("MP3", "*.mp3"),
    ("WAV", "*.wav"),
    ("OGG", "*.ogg"),
    ("FLAC", "*.flac"),
    ("All files", "*.*"),
]


def format_time(seconds: float) -> str:
    seconds = max(0, int(seconds))
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


class ReactiveMusicApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Vianey Reproductor xD 🌈")
        self.root.geometry("1050x720")
        self.root.minsize(760, 560)
        self.root.configure(bg="#08090d")

        self.player = AudioPlayer()
        self.analyzer = ReactiveAnalyzer()
        self._seeking = False

        self.song_var = tk.StringVar(value="No song loaded")
        self.status_var = tk.StringVar(value="Open a song and let it breathe.")
        self.time_var = tk.StringVar(value="00:00 / 00:00")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.volume_var = tk.DoubleVar(value=80.0)

        self._configure_style()
        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(33, self._tick)

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Black.TFrame", background="#08090d")
        style.configure(
            "Title.TLabel",
            background="#08090d",
            foreground="#f4f4f8",
            font=("Helvetica", 18, "bold"),
        )
        style.configure(
            "Muted.TLabel",
            background="#08090d",
            foreground="#9da1ad",
            font=("Helvetica", 10),
        )
        style.configure(
            "Player.TButton",
            padding=(16, 10),
            font=("Helvetica", 11, "bold"),
        )

    def _build_ui(self) -> None:
        shell = ttk.Frame(self.root, style="Black.TFrame", padding=22)
        shell.pack(fill="both", expand=True)

        header = ttk.Frame(shell, style="Black.TFrame")
        header.pack(fill="x", pady=(0, 10))
        ttk.Label(header, textvariable=self.song_var, style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, textvariable=self.status_var, style="Muted.TLabel").pack(anchor="w", pady=(4, 0))

        visual_frame = ttk.Frame(shell, style="Black.TFrame")
        visual_frame.pack(fill="both", expand=True)
        self.visualizer = RainbowVisualizer(visual_frame)
        self.visualizer.pack(fill="both", expand=True)

        timeline = ttk.Frame(shell, style="Black.TFrame")
        timeline.pack(fill="x", pady=(12, 0))
        self.progress = ttk.Scale(
            timeline,
            from_=0.0,
            to=1.0,
            variable=self.progress_var,
            orient="horizontal",
        )
        self.progress.pack(fill="x", expand=True)
        self.progress.bind("<ButtonPress-1>", self._begin_seek)
        self.progress.bind("<ButtonRelease-1>", self._end_seek)
        ttk.Label(timeline, textvariable=self.time_var, style="Muted.TLabel").pack(anchor="e", pady=(3, 0))

        controls = ttk.Frame(shell, style="Black.TFrame")
        controls.pack(fill="x", pady=(12, 0))

        ttk.Button(
            controls,
            text="Open song",
            command=self.open_song,
            style="Player.TButton",
        ).pack(side="left")

        self.play_button = ttk.Button(
            controls,
            text="▶ Play",
            command=self.toggle_play,
            style="Player.TButton",
        )
        self.play_button.pack(side="left", padx=(10, 0))

        ttk.Button(
            controls,
            text="■ Stop",
            command=self.stop,
            style="Player.TButton",
        ).pack(side="left", padx=(10, 0))

        volume_box = ttk.Frame(controls, style="Black.TFrame")
        volume_box.pack(side="right")
        ttk.Label(volume_box, text="Volume", style="Muted.TLabel").pack(anchor="e")
        self.volume = ttk.Scale(
            volume_box,
            from_=0,
            to=100,
            variable=self.volume_var,
            command=self._set_volume,
            orient="horizontal",
            length=180,
        )
        self.volume.pack()

    def open_song(self) -> None:
        selected = filedialog.askopenfilename(title="Choose a song", filetypes=AUDIO_TYPES)
        if not selected:
            return

        path = Path(selected)
        self.status_var.set("Analyzing waveform, RMS and FFT…")
        self.root.update_idletasks()

        try:
            self.analyzer.load(path)
            self.player.load(path, self.analyzer.duration)
        except Exception as exc:
            self.status_var.set("Could not load the selected song.")
            messagebox.showerror("Audio error", str(exc))
            return

        self.song_var.set(path.stem)
        self.status_var.set("Ready — press Play.")
        self.progress.configure(to=max(self.analyzer.duration, 0.001))
        self.progress_var.set(0.0)
        self.time_var.set(f"00:00 / {format_time(self.analyzer.duration)}")

    def toggle_play(self) -> None:
        if not self.player.loaded:
            self.open_song()
            if not self.player.loaded:
                return
        self.player.play_pause()
        self._sync_button_text()
        self.status_var.set("Reactive playback active." if not self.player.paused else "Paused.")

    def stop(self) -> None:
        self.player.stop()
        self.progress_var.set(0.0)
        self._sync_button_text()
        if self.player.loaded:
            self.status_var.set("Stopped.")

    def _begin_seek(self, _event) -> None:
        self._seeking = True

    def _end_seek(self, _event) -> None:
        if self.player.loaded:
            self.player.seek(self.progress_var.get())
        self._seeking = False

    def _set_volume(self, value: str) -> None:
        self.player.set_volume(float(value) / 100.0)

    def _sync_button_text(self) -> None:
        active = self.player.playing and not self.player.paused
        self.play_button.configure(text="❚❚ Pause" if active else "▶ Play")

    def _tick(self) -> None:
        try:
            position = self.player.position
            if not self._seeking:
                self.progress_var.set(position)

            duration = self.player.duration
            self.time_var.set(f"{format_time(position)} / {format_time(duration)}")

            state = self.analyzer.state_at(position) if self.analyzer.path else ReactiveState()
            active = self.player.playing and not self.player.paused
            self.visualizer.render(state, position, active=active)

            if self.player.update_finished_state():
                self.status_var.set("Track finished.")
                self._sync_button_text()
        finally:
            self.root.after(33, self._tick)

    def close(self) -> None:
        self.player.close()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    try:
        ReactiveMusicApp(root)
    except pygame.error as exc:
        messagebox.showerror(
            "Audio device error",
            f"Could not initialize the audio device:\n\n{exc}",
        )
        root.destroy()
        return
    root.mainloop()


if __name__ == "__main__":
    main()
