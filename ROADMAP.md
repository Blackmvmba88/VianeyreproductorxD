# 🗺️ Roadmap — Vianey Reproductor xD

## v0.1 — Reactive core ✅

- [x] Reproductor local.
- [x] MP3 / WAV / OGG / FLAC.
- [x] Play / pause / stop.
- [x] Seek y timeline.
- [x] Volumen.
- [x] NumPy como motor matemático.
- [x] Matplotlib embebido en Tkinter.
- [x] RMS para energía.
- [x] FFT por bandas.
- [x] `ReactiveState` desacoplado.
- [x] Onda sinusoidal reactiva.
- [x] Colormap Rainbow.
- [x] Glow reactivo.

## v0.2 — Timeline visual

- [ ] Dibujar waveform real de toda la canción.
- [ ] Seek directamente sobre waveform.
- [ ] Marcadores de picos.
- [ ] Zoom horizontal.
- [ ] Cachear análisis para no recalcular canciones conocidas.

## v0.3 — Beat engine

- [ ] Onset detection.
- [ ] Beat detection.
- [ ] BPM estimado.
- [ ] Pulso visual sincronizado.
- [ ] Eventos `on_beat` / `on_bar`.
- [ ] Sensibilidad configurable.

## v0.4 — Playlist

- [ ] Cola de reproducción.
- [ ] Drag & drop.
- [ ] Previous / next.
- [ ] Shuffle.
- [ ] Repeat one / repeat all.
- [ ] Metadata y portada.

## v0.5 — Visual modes

- [ ] Sine.
- [ ] Double sine.
- [ ] Mirror.
- [ ] Spectrum.
- [ ] Circular.
- [ ] Pulse.
- [ ] Particles.
- [ ] Presets configurables.

## v0.6 — Fullscreen / VJ

- [ ] Fullscreen limpio.
- [ ] Ocultar UI automáticamente.
- [ ] Segundo monitor / proyector.
- [ ] Resoluciones 16:9, 1:1 y 9:16.
- [ ] Captura/render de visuales.

## v0.7 — Karaoke

- [ ] Lyrics `.lrc`.
- [ ] Editor de timestamps.
- [ ] Línea actual y próxima línea.
- [ ] Ajuste fino de sincronía.
- [ ] Importar/exportar letras sincronizadas.

## v0.8 — Control externo

- [ ] MIDI input.
- [ ] Gamepad/controller mapping.
- [ ] OSC.
- [ ] Hotkeys configurables.
- [ ] DMX bridge usando `ReactiveState`.

## v0.9 — GPU

Cuando Matplotlib sea el cuello de botella:

```text
Matplotlib prototype
        ↓
ReactiveState stays
        ↓
ModernGL / OpenGL
        ↓
Shaders + bloom + particles + 60/120 FPS
```

- [ ] Backend ModernGL.
- [ ] Shaders.
- [ ] Bloom.
- [ ] Blur.
- [ ] Miles de partículas.
- [ ] Presets GPU.

## v1.0 — Reactive audiovisual engine

Meta:

```text
🎵 AUDIO
   ↓
🧮 ANALYSIS
   ↓
🧠 ReactiveState
   ↓
┌──────────┬──────────┬──────────┬──────────┐
│ waveform │ rainbow  │ karaoke  │   DMX    │
└──────────┴──────────┴──────────┴──────────┘
```

La regla arquitectónica es simple: **las futuras salidas escuchan `ReactiveState`; el núcleo de audio no se reescribe.**
