# Narrador IA — Comentarista Automático de Valorant

Aplicación de escritorio que analiza clips de Valorant fotograma a fotograma, genera comentarios narrativos con un modelo de lenguaje multimodal, y los narra en voz alta en español sincronizados con la reproducción del video.

## Integrantes
* Cynthia Urias Beltran
* Angel Amaury Arredondo González
* Cesar Yovanni Inzunza Aguilar
* Erick David Hermosillo Flores

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                              │
│              Punto de entrada — lanza QApplication          │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      mainwindow.py                          │
│                   Ventana principal (PyQt6)                 │
│                                                             │
│  ┌─────────────────┐   ┌──────────────┐   ┌──────────────┐  │
│  │   TTSLoader     │   │ QMediaPlayer │   │  CommentBox  │  │
│  │  (QThread)      │   │  (video)     │   │  (QTextEdit) │  │
│  │ Carga el modelo │   └──────┬───────┘   └──────┬───────┘  │
│  │ MMS-TTS en BG   │          │ positionChanged  │ append   │
│  └────────┬────────┘          └──────────────────┘          │
│           │ ready signal                                    │
│  ┌────────▼────────┐                                        │
│  │ TTSAudioThread  │  ← hilo persistente con queue.Queue    │
│  │  (QThread)      │    sin solapamiento de audio           │
│  │ speak(text)     │    velocidad ajustable en tiempo real  │
│  └─────────────────┘                                        │
└───────────────────────────┬─────────────────────────────────┘
                            │ start_analysis()
┌───────────────────────────▼─────────────────────────────────┐
│                      analyzer.py                            │
│              VideoAnalyzerSignals (QThread)                 │
│                                                             │
│  1. Abre el video con OpenCV                                │
│  2. Extrae frames cada N segundos                           │
│  3. Los comprime a JPEG 80% / 1280×720                      │
│  4. Los envía al modelo LLM elegido:                        │
│     • Ollama  (local, vía HTTP)                             │
│     • Gemini  (API cloud)                                   │
│     • OpenAI  (API cloud)                                   │
│  5. Filtra respuestas "SKIP"                                │
│  6. Guarda los comentarios en <video>_comments.json         │
│                                                             │
│  Signals: progress(int) · log(str) · finished(str) · error  │
└─────────────────────────────────────────────────────────────┘
```

### Flujo de datos

```
Video (.mp4)
    │
    ▼ OpenCV
Frames JPEG (base64)
    │
    ▼ API (Ollama / Gemini / OpenAI)
Comentarios texto  →  _comments.json
    │
    ▼ QMediaPlayer positionChanged
Comentario visible en pantalla
    │
    ▼ TTSAudioThread (facebook/mms-tts-spa)
Audio WAV en español (velocidad ajustable)
    │
    ▼ sounddevice / winsound
Narración sincronizada
```

---

## Uso

### Iniciar la aplicación

```bash
python main.py
```

Al arrancar, la app carga automáticamente el modelo TTS (`facebook/mms-tts-spa`) en segundo plano. La barra de estado mostrará "Narración de voz activada ✔" cuando esté listo.

### Flujo de uso

1. **Selecciona un video** — haz clic en "Selecciona un video" y elige un `.mp4`, `.avi` o `.mkv`
2. **Elige el modelo LLM** — selecciona `ollama`, `gemini` u `openai` en el desplegable
3. **Ajusta la tasa de muestra** — define cada cuántos segundos se analiza un frame (por defecto 2s)
4. **Comienza el análisis** — haz clic en "Comenzar Análisis" y espera a que termine
5. **Ajusta la velocidad de voz** — usa el spinner "Vel. voz:" (1.0 = normal, 1.4 = 40% más rápido)
6. **Reproduce el video** — los comentarios aparecen en el panel derecho y se narran en voz alta


### Opciones avanzadas

| Control | Descripción |
|---|---|
| Forzar nuevo análisis | Borra el JSON cacheado y re-analiza el video desde cero |
| Narración de voz | Activa o desactiva el TTS sin reiniciar |
| Vel. voz | Ajusta la velocidad de habla en tiempo real (0.5 – 3.0) |

> Los comentarios se guardan en `<nombre_video>_comments.json` junto al archivo de video. Si ya existe, la app lo reutiliza automáticamente para no gastar créditos de API.

---

## Estructura del proyecto
```
NarradorAI/
├── main.py                          # Punto de entrada
├── .gitignore
├── requirements.txt
├── README.md
├── __init__.py
│
├── AnalisisModelo/                  # Extracción de frames y consulta al LLM
│   ├── __init__.py
│   ├── .env                         # API keys
│   └── analyzer.py
│
├── Interfaz/                        # UI PyQt6
│   ├── __init__.py
│   └── mainwindow.py
│
├── TTS/                             # Síntesis de voz
│   ├── __init__.py
│   ├── TTS_Controller.py            # Mixin TTS + TTSLoader + TTSAudioThread
│   └── video_player.py              # Mixin reproducción y sincronización de comentarios
│
└── examples/                        # Videos y JSONs de prueba
    ├── Sin título.mp4
    ├── Sin título_comments.json
    ├── Timeline 1.mp4
    └── Timeline 1_comments.json
```
## Modelos utilizados

| Componente | Modelo | Proveedor |
|---|---|---|
| Visión (local) | `gemma4:e4b` | Ollama / Google |
| Visión (cloud) | `gemini-3.5-flash` | Google |
| Visión (cloud) | `gpt-4o-mini` | OpenAI |
| Texto a voz | `facebook/mms-tts-spa` | HuggingFace |

---