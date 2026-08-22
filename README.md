# 🌈 Vianey Reproductor xD

Reproductor de música sencillo con visualización reactiva: la canción controla una onda sinusoidal, su amplitud, grosor y color en tiempo real.

> **Idea:** reproducir → analizar → transformar → visualizar.

## Estado

**v0.1 — MVP funcional**

- Carga MP3, WAV, OGG y FLAC.
- Play / pause / stop.
- Seek sobre la barra de progreso.
- Volumen.
- Duración y tiempo actual.
- Análisis de energía RMS.
- FFT con bandas bass / mid / high.
- Onda sinusoidal reactiva con NumPy.
- Render con Matplotlib.
- Color dinámico con `matplotlib.cm.rainbow`.
- Glow y pulso visual según energía y graves.

## Arquitectura

```text
AUDIO
  │
  ├── pygame.mixer ───────────────► playback
  │
  └── librosa + NumPy
          │
          ▼
      FFT / RMS
          │
          ▼
    ReactiveState
          │
          ▼
  Matplotlib Rainbow
```

El corazón del proyecto es `ReactiveState`: desacopla el análisis de audio del visualizador para que después podamos conectar partículas, karaoke, MIDI, DMX, shaders o cualquier otra salida sin rehacer el reproductor.

## Estructura

```text
VianeyreproductorxD/
├── app.py
├── analysis/
│   ├── __init__.py
│   └── reactive.py
├── player/
│   ├── __init__.py
│   └── audio.py
├── visualizer/
│   ├── __init__.py
│   └── rainbow.py
├── requirements.txt
├── ROADMAP.md
└── .gitignore
```

## Requisitos

- Python 3.10+
- Tkinter (incluido normalmente con Python)

Instala dependencias:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

En Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecutar

```bash
python app.py
```

Después pulsa **Open song** y selecciona un archivo.

## Controles

- **Open song**: abre una canción.
- **Play / Pause**: reproducción.
- **Stop**: vuelve al inicio.
- **Progress**: haz click o arrastra para buscar dentro de la canción.
- **Volume**: volumen de salida.

## Visual reactivo

Cada frame usa la posición actual de reproducción para consultar una ventana de análisis precalculada:

```text
energy  → amplitud + glow
bass    → grosor + pulso
mid     → deformación secundaria
high    → detalle / velocidad
centroid→ color rainbow
```

La onda no es el waveform literal del archivo: es una **onda sinusoidal estilizada y conducida por características reales de la música**.

## Filosofía

No es un reproductor con un visualizador pegado encima.

Es un reproductor cuya interfaz **respira con la canción**.

```text
sonido + movimiento + color + forma + luz
```

## Próximo paso

Consulta [`ROADMAP.md`](ROADMAP.md). La siguiente evolución natural es waveform completo con seek visual, playlist, beat detection y visuales GPU.
