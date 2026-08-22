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

## v0.2 — Neon Trip Engine ✅

- [x] Presets visuales configurables.
- [x] Neon Abyss.
- [x] Rainbow Warp.
- [x] Toxic Dream.
- [x] BlackMamba Trip.
- [x] Lluvia de estrellas/partículas.
- [x] Trails preasignados.
- [x] Mirror psicodélico.
- [x] Warp speed.
- [x] Bass punch.
- [x] Rainbow speed.
- [x] Fullscreen.
- [x] Configuración local `.env`.
- [x] `.venv` como instalación recomendada.
- [x] Clamp/validación de parámetros visuales.
- [x] Clamp/validación del transporte de audio.
- [x] Tests de configuración.
- [x] CI compile + pytest.

## v0.3 — Timeline visual

- [ ] Dibujar waveform real de toda la canción.
- [ ] Seek directamente sobre waveform.
- [ ] Marcadores de picos.
- [ ] Zoom horizontal.
- [ ] Cachear análisis para no recalcular canciones conocidas.

## v0.4 — Beat engine

- [ ] Onset detection.
- [ ] Beat detection.
- [ ] BPM estimado.
- [ ] Pulso visual sincronizado.
- [ ] Eventos `on_beat` / `on_bar`.
- [ ] Sensibilidad configurable.
- [ ] Explosión de estrellas en beats fuertes.
- [ ] Flash/zoom opcional con protección de intensidad.

## v0.5 — Playlist

- [ ] Cola de reproducción.
- [ ] Drag & drop.
- [ ] Previous / next.
- [ ] Shuffle.
- [ ] Repeat one / repeat all.
- [ ] Metadata y portada.

## v0.6 — Visual modes

- [x] Sine.
- [x] Mirror.
- [x] Particles / star rain.
- [ ] Double sine.
- [ ] Spectrum.
- [ ] Circular.
- [ ] Pulse tunnel.
- [ ] Hyperspace.
- [ ] Nebula field.
- [ ] Chromatic aberration simulation.
- [ ] Visual preset save/load.

## v0.7 — Fullscreen / VJ

- [x] Fullscreen básico.
- [ ] Ocultar UI automáticamente.
- [ ] Segundo monitor / proyector.
- [ ] Resoluciones 16:9, 1:1 y 9:16.
- [ ] Captura/render de visuales.
- [ ] VJ safe mode para mantener FPS estable.

## v0.8 — Karaoke

- [ ] Lyrics `.lrc`.
- [ ] Editor de timestamps.
- [ ] Línea actual y próxima línea.
- [ ] Ajuste fino de sincronía.
- [ ] Importar/exportar letras sincronizadas.

## v0.9 — Control externo

- [ ] MIDI input.
- [ ] Gamepad/controller mapping.
- [ ] OSC.
- [ ] Hotkeys configurables.
- [ ] DMX bridge usando `ReactiveState`.

## v0.10 — GPU

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
- [ ] Feedback framebuffer / trails reales.
- [ ] Nebulosas y túneles shader.

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
│ waveform │ neon FX  │ karaoke  │   DMX    │
└──────────┴──────────┴──────────┴──────────┘
```

La regla arquitectónica sigue siendo simple: **las futuras salidas escuchan `ReactiveState`; el núcleo de audio no se reescribe.**
