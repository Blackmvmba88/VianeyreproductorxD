# 🌈 Vianey Reproductor xD

Reproductor de música local con una interfaz que **respira con la canción**: RMS + FFT alimentan una onda sinusoidal reactiva, trails, glow, lluvia de estrellas y presets neón en tiempo real.

> **Idea:** reproducir → analizar → transformar → visualizar.

## Estado

**v0.2 — Neon Trip Engine**

- MP3 / WAV / OGG / FLAC.
- Play / pause / stop.
- Seek y timeline.
- Volumen validado.
- RMS + FFT: bass / mid / high / centroid.
- `ReactiveState` desacoplado.
- NumPy + Matplotlib.
- Glow multicapa.
- Trails preasignados.
- Lluvia de hasta 320 estrellas/partículas preasignadas.
- Warp, bass punch y velocidad cromática.
- Mirror psicodélico.
- Fullscreen con `F11`.
- Presets `Neon Abyss`, `Rainbow Warp`, `Toxic Dream` y `BlackMamba Trip`.
- Configuración local por `.env`.
- Validación automática con pytest + GitHub Actions.

## Arquitectura

```text
                    AUDIO
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
     pygame.mixer             librosa
          │                       │
       playback               NumPy / FFT
                                  │
                                  ▼
                            ReactiveState
                                  │
                                  ▼
                             VisualConfig
                                  │
             ┌────────────────────┼────────────────────┐
             ▼                    ▼                    ▼
          sine/glow             trails             star rain
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  ▼
                          Matplotlib canvas
```

`ReactiveState` describe la música. `VisualConfig` describe el viaje visual. Las dos capas están separadas para poder evolucionar posteriormente a GPU, karaoke, MIDI o DMX sin reescribir el núcleo.

## Instalación aislada — máquina administrada

El proyecto está pensado para **no instalar paquetes Python globalmente**.

Todo queda dentro del repositorio:

```text
VianeyreproductorxD/
├── .venv/      ← dependencias locales, ignoradas por Git
├── .env        ← configuración local, ignorada por Git
└── ...
```

### macOS / Linux

```bash
git clone https://github.com/Blackmvmba88/VianeyreproductorxD.git
cd VianeyreproductorxD
bash scripts/bootstrap.sh
.venv/bin/python app.py
```

El bootstrap solamente hace:

```text
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.env.example → .env   (solo si .env todavía no existe)
```

No requiere `pip install` global.

### Instalación manual

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python app.py
```

## `.env`

`.env.example` contiene todos los parámetros soportados:

```dotenv
VIANEY_PRESET=BlackMamba Trip
VIANEY_STAR_RAIN=true
VIANEY_PSYCHEDELIC=true
VIANEY_GLOW=1.70
VIANEY_TRAILS=10
VIANEY_WARP=1.45
VIANEY_BASS_PUNCH=1.70
VIANEY_PARTICLES=280
VIANEY_RAINBOW_SPEED=0.82
VIANEY_BACKGROUND_DIM=0.67
VIANEY_VOLUME=0.80
VIANEY_FPS=30
```

Los valores son validados antes de entrar al motor. Ejemplos:

```text
Glow             0.00 → 2.50
Trails               0 → 12
Warp              0.00 → 2.50
Bass punch        0.00 → 2.50
Particles            0 → 320
Rainbow speed     0.00 → 2.00
Background dim    0.35 → 1.00
Volume            0.00 → 1.00
FPS                 15 → 60
```

Si el `.env` contiene texto inválido o números fuera de rango, el programa usa un valor seguro o aplica clamp en vez de fallar.

## Controles

- **Open song** / `Ctrl+O` — carga audio compatible.
- **Play / Pause** / `Space` — controla reproducción.
- **Stop** — vuelve al inicio.
- **Progress** — seek validado entre 0 y duración.
- **Volume** — siempre limitado a 0–100%.
- **Fullscreen** / `F11` — modo visual ampliado.
- `Esc` — salir de fullscreen.

## Presets visuales

### Neon Abyss

Más atmosférico: cyan/magenta, glow profundo, estrellas lentas y trails moderados.

### Rainbow Warp

Rainbow agresivo, warp alto, trails largos y respuesta fuerte al beat/energía.

### Toxic Dream

Paleta eléctrica tipo `turbo`, partículas densas y deformación psicodélica.

### BlackMamba Trip

Preset máximo inicial: fondo casi negro, color cycling, mirror psicodélico, lluvia densa, 10 trails y bass punch fuerte.

## Qué controla la canción

```text
energy    → amplitud + glow
bass      → grosor + punch + velocidad de estrellas
mid       → armónicos + deformación
high      → detalle + velocidad de fase
centroid  → posición dentro de la paleta
```

La onda no intenta copiar literalmente el waveform. Es una **forma generativa conducida por características reales de la canción**.

## Optimización actual

Los efectos persistentes se crean una sola vez:

- las líneas de trail se preasignan;
- el campo de estrellas tiene un máximo fijo de 320 partículas;
- por frame solo se actualizan arrays y propiedades de artistas;
- no se crean cientos de objetos Python nuevos para cada frame;
- el FPS se puede limitar desde `.env` entre 15 y 60.

Esto mantiene Matplotlib usable mientras el proyecto todavía está en fase prototipo. Cuando el visual llegue al límite de Matplotlib, `ReactiveState` permitirá migrar el renderer a ModernGL sin reescribir el análisis de audio.

## Validación

Local:

```bash
.venv/bin/python -m compileall -q app.py analysis player visualizer settings.py tests
.venv/bin/python -m pytest -q
```

GitHub Actions ejecuta esas validaciones automáticamente en push y pull request.

## Estructura

```text
VianeyreproductorxD/
├── app.py
├── settings.py
├── .env.example
├── scripts/
│   └── bootstrap.sh
├── analysis/
│   ├── __init__.py
│   └── reactive.py
├── player/
│   ├── __init__.py
│   └── audio.py
├── visualizer/
│   ├── __init__.py
│   ├── effects.py
│   └── rainbow.py
├── tests/
│   ├── test_settings.py
│   └── test_visual_config.py
├── requirements.txt
├── ROADMAP.md
└── .github/workflows/ci.yml
```

## Filosofía

No es un reproductor con un visualizador pegado encima.

Es un reproductor cuya interfaz **respira, pulsa y alucina con la canción**.

```text
sonido + movimiento + color + forma + luz + profundidad
```

Consulta [`ROADMAP.md`](ROADMAP.md) para la siguiente evolución.
