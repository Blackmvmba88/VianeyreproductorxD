from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pygame

from analysis import ReactiveAnalyzer, ReactiveState
from player import AudioPlayer
from settings import load_settings
from visualizer import PRESETS, RainbowVisualizer, VisualConfig


SUPPORTED_SUFFIXES = {".mp3", ".wav", ".ogg", ".flac"}
AUDIO_TYPES = [
    ("Audio files", "*.mp3 *.wav *.ogg *.flac"),
    ("MP3", "*.mp3"),
    ("WAV", "*.wav"),
    ("OGG", "*.ogg"),
    ("FLAC", "*.flac"),
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
        self.runtime = load_settings()
        self.root.title("Vianey Reproductor xD — Neon Reactive Engine")
        self.root.geometry("1180x820")
        self.root.minsize(900, 680)
        self.root.configure(bg="#05040b")

        self.player = AudioPlayer()
        self.player.set_volume(self.runtime.volume)
        self.analyzer = ReactiveAnalyzer()
        self._seeking = False
        self._fullscreen = False
        self._render_error_reported = False
        self._tick_ms = max(16, round(1000 / self.runtime.target_fps))

        initial_preset = self.runtime.preset if self.runtime.preset in PRESETS else "BlackMamba Trip"
        self.song_var = tk.StringVar(value="No song loaded")
        self.status_var = tk.StringVar(value="Open a song and let the neon breathe.")
        self.time_var = tk.StringVar(value="00:00 / 00:00")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.volume_var = tk.DoubleVar(value=self.runtime.volume * 100.0)
        self.preset_var = tk.StringVar(value=initial_preset)
        self.star_var = tk.BooleanVar(value=self.runtime.star_rain)
        self.psychedelic_var = tk.BooleanVar(value=self.runtime.psychedelic)
        self.glow_var = tk.DoubleVar(value=self.runtime.glow * 100.0)
        self.trails_var = tk.DoubleVar(value=float(self.runtime.trails))
        self.warp_var = tk.DoubleVar(value=self.runtime.warp * 100.0)
        self.bass_var = tk.DoubleVar(value=self.runtime.bass_punch * 100.0)
        self.particles_var = tk.DoubleVar(value=float(self.runtime.particles))
        self.rainbow_var = tk.DoubleVar(value=self.runtime.rainbow_speed * 100.0)
        self.dim_var = tk.DoubleVar(value=self.runtime.background_dim * 100.0)
        self.fx_summary_var = tk.StringVar(value="")

        self._configure_style()
        self._build_ui()
        self._bind_keys()
        self._apply_fx_config()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(self._tick_ms, self._tick)

    def _configure_style(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        bg = "#05040b"
        panel = "#0a0b14"
        fg = "#f6f3ff"
        muted = "#a9a5bb"
        neon = "#d66bff"

        style.configure("Black.TFrame", background=bg)
        style.configure("Panel.TFrame", background=panel)
        style.configure("Title.TLabel", background=bg, foreground=fg, font=("Helvetica", 18, "bold"))
        style.configure("Muted.TLabel", background=bg, foreground=muted, font=("Helvetica", 10))
        style.configure("Panel.TLabel", background=panel, foreground=fg, font=("Helvetica", 9))
        style.configure("Neon.TLabel", background=panel, foreground=neon, font=("Helvetica", 10, "bold"))
        style.configure("Player.TButton", padding=(14, 9), font=("Helvetica", 10, "bold"))
        style.configure("FX.TLabelframe", background=panel, foreground=neon)
        style.configure("FX.TLabelframe.Label", background=panel, foreground=neon, font=("Helvetica", 10, "bold"))
        style.configure("FX.TCheckbutton", background=panel, foreground=fg)
        style.map("FX.TCheckbutton", background=[("active", panel)], foreground=[("active", neon)])

    def _bind_keys(self) -> None:
        self.root.bind("<space>", lambda _event: self.toggle_play())
        self.root.bind("<Control-o>", lambda _event: self.open_song())
        self.root.bind("<F11>", lambda _event: self.toggle_fullscreen())
        self.root.bind("<Escape>", lambda _event: self._leave_fullscreen())

    def _build_ui(self) -> None:
        shell = ttk.Frame(self.root, style="Black.TFrame", padding=18)
        shell.pack(fill="both", expand=True)

        header = ttk.Frame(shell, style="Black.TFrame")
        header.pack(fill="x", pady=(0, 8))
        ttk.Label(header, textvariable=self.song_var, style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, textvariable=self.status_var, style="Muted.TLabel").pack(anchor="w", pady=(4, 0))

        visual_frame = ttk.Frame(shell, style="Black.TFrame")
        visual_frame.pack(fill="both", expand=True)
        self.visualizer = RainbowVisualizer(visual_frame)
        self.visualizer.pack(fill="both", expand=True)

        timeline = ttk.Frame(shell, style="Black.TFrame")
        timeline.pack(fill="x", pady=(8, 0))
        self.progress = ttk.Scale(timeline, from_=0.0, to=1.0, variable=self.progress_var, orient="horizontal")
        self.progress.pack(fill="x", expand=True)
        self.progress.bind("<ButtonPress-1>", self._begin_seek)
        self.progress.bind("<ButtonRelease-1>", self._end_seek)
        ttk.Label(timeline, textvariable=self.time_var, style="Muted.TLabel").pack(anchor="e", pady=(3, 0))

        transport = ttk.Frame(shell, style="Black.TFrame")
        transport.pack(fill="x", pady=(8, 0))
        ttk.Button(transport, text="Open song", command=self.open_song, style="Player.TButton").pack(side="left")
        self.play_button = ttk.Button(transport, text="▶ Play", command=self.toggle_play, style="Player.TButton")
        self.play_button.pack(side="left", padx=(8, 0))
        ttk.Button(transport, text="■ Stop", command=self.stop, style="Player.TButton").pack(side="left", padx=(8, 0))
        ttk.Button(transport, text="⛶ Fullscreen", command=self.toggle_fullscreen, style="Player.TButton").pack(side="left", padx=(8, 0))

        volume_box = ttk.Frame(transport, style="Black.TFrame")
        volume_box.pack(side="right")
        ttk.Label(volume_box, text="Volume", style="Muted.TLabel").pack(anchor="e")
        ttk.Scale(volume_box, from_=0, to=100, variable=self.volume_var, command=self._set_volume, orient="horizontal", length=170).pack()

        self.fx_panel = ttk.LabelFrame(shell, text="NEON / STAR FX", style="FX.TLabelframe", padding=10)
        self.fx_panel.pack(fill="x", pady=(10, 0))

        left = ttk.Frame(self.fx_panel, style="Panel.TFrame")
        left.pack(side="left", fill="both", expand=True)
        middle = ttk.Frame(self.fx_panel, style="Panel.TFrame")
        middle.pack(side="left", fill="both", expand=True, padx=14)
        right = ttk.Frame(self.fx_panel, style="Panel.TFrame")
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="Preset", style="Neon.TLabel").pack(anchor="w")
        preset = ttk.Combobox(left, textvariable=self.preset_var, values=list(PRESETS), state="readonly", width=22)
        preset.pack(anchor="w", fill="x", pady=(2, 7))
        preset.bind("<<ComboboxSelected>>", self._on_preset_selected)
        ttk.Checkbutton(left, text="Star rain", variable=self.star_var, command=self._apply_fx_config, style="FX.TCheckbutton").pack(anchor="w")
        ttk.Checkbutton(left, text="Psychedelic mirror", variable=self.psychedelic_var, command=self._apply_fx_config, style="FX.TCheckbutton").pack(anchor="w")

        self._fx_slider(middle, "Glow", self.glow_var, 0, 250)
        self._fx_slider(middle, "Warp speed", self.warp_var, 0, 250)
        self._fx_slider(middle, "Bass punch", self.bass_var, 0, 250)
        self._fx_slider(middle, "Rainbow speed", self.rainbow_var, 0, 200)

        self._fx_slider(right, "Trails", self.trails_var, 0, 12)
        self._fx_slider(right, "Particles", self.particles_var, 0, 320)
        self._fx_slider(right, "Background dim", self.dim_var, 35, 100)
        ttk.Label(right, textvariable=self.fx_summary_var, style="Panel.TLabel").pack(anchor="w", pady=(5, 0))

    def _fx_slider(self, parent, label: str, variable: tk.DoubleVar, low: float, high: float) -> None:
        ttk.Label(parent, text=label, style="Panel.TLabel").pack(anchor="w")
        slider = ttk.Scale(parent, from_=low, to=high, variable=variable, orient="horizontal", command=lambda _value: self._apply_fx_config())
        slider.pack(fill="x", pady=(0, 4))

    def _current_visual_config(self) -> VisualConfig:
        return VisualConfig(
            preset=self.preset_var.get(),
            glow=self.glow_var.get() / 100.0,
            trails=round(self.trails_var.get()),
            warp=self.warp_var.get() / 100.0,
            bass_punch=self.bass_var.get() / 100.0,
            particles=round(self.particles_var.get()),
            rainbow_speed=self.rainbow_var.get() / 100.0,
            background_dim=self.dim_var.get() / 100.0,
            psychedelic=self.psychedelic_var.get(),
            star_rain=self.star_var.get(),
        ).validated()

    def _apply_fx_config(self) -> None:
        cfg = self.visualizer.set_config(self._current_visual_config())
        self.glow_var.set(cfg.glow * 100.0)
        self.trails_var.set(float(cfg.trails))
        self.warp_var.set(cfg.warp * 100.0)
        self.bass_var.set(cfg.bass_punch * 100.0)
        self.particles_var.set(float(cfg.particles))
        self.rainbow_var.set(cfg.rainbow_speed * 100.0)
        self.dim_var.set(cfg.background_dim * 100.0)
        self.fx_summary_var.set(f"{cfg.particles} stars · {cfg.trails} trails · {self.runtime.target_fps} FPS")

    def _on_preset_selected(self, _event=None) -> None:
        cfg = VisualConfig.from_preset(self.preset_var.get()).validated()
        self.star_var.set(cfg.star_rain)
        self.psychedelic_var.set(cfg.psychedelic)
        self.glow_var.set(cfg.glow * 100.0)
        self.trails_var.set(float(cfg.trails))
        self.warp_var.set(cfg.warp * 100.0)
        self.bass_var.set(cfg.bass_punch * 100.0)
        self.particles_var.set(float(cfg.particles))
        self.rainbow_var.set(cfg.rainbow_speed * 100.0)
        self.dim_var.set(cfg.background_dim * 100.0)
        self._apply_fx_config()
        self.status_var.set(f"Visual preset: {cfg.preset}")

    def open_song(self) -> None:
        selected = filedialog.askopenfilename(title="Choose a song", filetypes=AUDIO_TYPES)
        if not selected:
            return

        path = Path(selected).expanduser()
        if not path.is_file():
            messagebox.showerror("Audio error", "The selected file does not exist or is not readable.")
            return
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            messagebox.showerror("Audio error", f"Unsupported file type: {path.suffix or 'unknown'}")
            return

        self.status_var.set("Analyzing RMS / FFT…")
        self.root.update_idletasks()
        try:
            self.analyzer.load(path)
            self.player.load(path, self.analyzer.duration)
        except Exception as exc:
            self.status_var.set("Could not load the selected song.")
            messagebox.showerror("Audio error", str(exc))
            return

        self.song_var.set(path.stem)
        self.status_var.set("Ready — press Play. Neon engine armed.")
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
        self.status_var.set("Reactive playback active." if self.player.playing and not self.player.paused else "Paused.")

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
        try:
            normalized = max(0.0, min(float(value) / 100.0, 1.0))
        except (TypeError, ValueError):
            normalized = self.runtime.volume
        self.player.set_volume(normalized)

    def toggle_fullscreen(self) -> None:
        self._fullscreen = not self._fullscreen
        self.root.attributes("-fullscreen", self._fullscreen)

    def _leave_fullscreen(self) -> None:
        if self._fullscreen:
            self._fullscreen = False
            self.root.attributes("-fullscreen", False)

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
                self.status_var.set("Track finished — Play restarts from zero.")
                self._sync_button_text()
        except Exception as exc:
            if not self._render_error_reported:
                self._render_error_reported = True
                self.status_var.set(f"Visual engine recovered from an error: {exc}")
        finally:
            self.root.after(self._tick_ms, self._tick)

    def close(self) -> None:
        self.player.close()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    try:
        ReactiveMusicApp(root)
    except pygame.error as exc:
        messagebox.showerror("Audio device error", f"Could not initialize the audio device:\n\n{exc}")
        root.destroy()
        return
    root.mainloop()


if __name__ == "__main__":
    main()
