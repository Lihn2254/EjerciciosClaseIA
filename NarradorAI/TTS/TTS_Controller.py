"""
TTS/TTS_Controller.py
---------------------
Mixin que añade toda la lógica de Text-To-Speech a MainWindow.

Cambios respecto a la versión original:
  • TTSPreSynthThread  — sintetiza en background TODOS los comentarios
    en cuanto se carga el JSON, guardando el audio como bytes PCM en un dict.
  • TTSAudioThread     — acepta tanto texto (síntesis en el momento) como
    bytes pre-sintetizados (reproducción inmediata), eliminando el lag.
  • TTS_Controller     — expone presynthesize_comments() para que
    MainWindow/VideoPlayer lo llame al cargar comentarios.
"""

import queue
import wave
import tempfile
import io
import os
from typing import Dict, Optional

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal


# ---------------------------------------------------------------------------
# Hilo que carga el modelo TTS
# ---------------------------------------------------------------------------
class TTSLoader(QThread):
    ready  = pyqtSignal(object)
    failed = pyqtSignal(str)

    def run(self):
        try:
            from transformers import pipeline
            tts = pipeline("text-to-speech", model="facebook/mms-tts-spa")
            self.ready.emit(tts)
        except Exception as e:
            self.failed.emit(str(e))


# ---------------------------------------------------------------------------
# Hilo de pre-síntesis: convierte todos los comentarios a WAV en background
# ---------------------------------------------------------------------------
class TTSPreSynthThread(QThread):
    """
    Recibe una lista de (index, text) y sintetiza cada uno con el pipeline TTS.
    Emite progress(int 0-100) y finished(dict[int, bytes]) con el audio PCM
    de cada comentario indexado.
    """
    progress = pyqtSignal(int)           # 0-100
    finished = pyqtSignal(object)        # dict[int, bytes]  (WAV en memoria)
    failed   = pyqtSignal(str)

    def __init__(self, tts_pipeline, comments: list, speed_factor: float):
        super().__init__()
        self.tts_pipeline = tts_pipeline
        self.comments     = comments      # lista de {"timestamp":…, "comment":…}
        self.speed_factor = speed_factor
        self._cancelled   = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        cache: Dict[int, bytes] = {}
        total = len(self.comments)
        if total == 0:
            self.finished.emit(cache)
            return
        try:
            for i, item in enumerate(self.comments):
                if self._cancelled:
                    break
                wav_bytes = self._synth(item["comment"])
                if wav_bytes is not None:
                    cache[i] = wav_bytes
                self.progress.emit(int((i + 1) / total * 100))
            self.finished.emit(cache)
        except Exception as e:
            self.failed.emit(str(e))

    def _synth(self, text: str) -> Optional[bytes]:
        try:
            output  = self.tts_pipeline(text)
            audio   = np.array(output["audio"])
            if audio.ndim > 1:
                audio = audio.squeeze()
            audio = audio.astype(np.float32)
            max_val = np.abs(audio).max()
            if max_val > 1.0:
                audio /= max_val

            sr          = int(output["sampling_rate"])
            playback_sr = int(sr * self.speed_factor)
            pcm         = (audio * 32767).astype(np.int16)

            buf = io.BytesIO()
            with wave.open(buf, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(playback_sr)
                wf.writeframes(pcm.tobytes())
            return buf.getvalue()
        except Exception as e:
            print(f"[PreSynth] Error sintetizando '{text[:30]}': {e}")
            return None


# ---------------------------------------------------------------------------
# Hilo de reproducción de audio
# ---------------------------------------------------------------------------
class TTSAudioThread(QThread):
    """
    Cola de reproducción que acepta:
      • str   → sintetiza en el momento (fallback si pre-síntesis no está lista)
      • bytes → WAV ya sintetizado, reproducción casi inmediata
    """
    def __init__(self, tts_pipeline, speed_factor: float = 1.4):
        super().__init__()
        self.tts_pipeline = tts_pipeline
        self.speed_factor = speed_factor
        self._queue: queue.Queue = queue.Queue(maxsize=1)

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------
    def speak_wav(self, wav_bytes: bytes):
        """Encola bytes WAV pre-sintetizados (reproducción inmediata)."""
        self._enqueue(("wav", wav_bytes))

    def speak(self, text: str):
        """Encola texto para síntesis en el momento (fallback)."""
        self._enqueue(("text", text))

    def stop(self):
        self._enqueue(None)

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------
    def _enqueue(self, item):
        # Descarta lo que haya pendiente para no acumular comentarios viejos
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break
        try:
            self._queue.put_nowait(item)
        except queue.Full:
            pass

    def run(self):
        while True:
            item = self._queue.get()
            if item is None:
                break
            kind, payload = item
            if kind == "wav":
                self._play_wav_bytes(payload)
            else:
                self._synthesize_and_play(payload)

    def _play_wav_bytes(self, wav_bytes: bytes):
        """Reproduce bytes WAV directamente, sin síntesis."""
        try:
            buf = io.BytesIO(wav_bytes)
            with wave.open(buf, "rb") as wf:
                sr     = wf.getframerate()
                frames = wf.readframes(wf.getnframes())
                audio  = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32767.0

            try:
                import sounddevice as sd
                sd.play(audio, samplerate=sr, blocking=True)
                return
            except Exception:
                pass

            # Fallback: escribir a disco y usar winsound/aplay/afplay
            self._play_pcm_fallback(audio, sr)
        except Exception as e:
            print(f"[TTS] Error reproduciendo WAV pre-sintetizado: {e}")

    def _synthesize_and_play(self, text: str):
        """Sintetiza en el momento (fallback cuando no hay caché)."""
        tmp_path = None
        try:
            output = self.tts_pipeline(text)
            audio  = np.array(output["audio"])
            if audio.ndim > 1:
                audio = audio.squeeze()
            audio = audio.astype(np.float32)
            max_val = np.abs(audio).max()
            if max_val > 1.0:
                audio /= max_val

            sr          = int(output["sampling_rate"])
            playback_sr = int(sr * self.speed_factor)

            try:
                import sounddevice as sd
                sd.play(audio, samplerate=playback_sr, blocking=True)
                return
            except Exception:
                pass

            self._play_pcm_fallback(audio, playback_sr)
        except Exception as e:
            print(f"[TTS] Error sintetizando en tiempo real: {e}")

    def _play_pcm_fallback(self, audio: np.ndarray, sr: int):
        tmp_path = None
        try:
            pcm = (audio * 32767).astype(np.int16)
            fd, tmp_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            with wave.open(tmp_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sr)
                wf.writeframes(pcm.tobytes())
            try:
                import winsound
                winsound.PlaySound(tmp_path, winsound.SND_FILENAME)
            except ImportError:
                os.system(f'aplay "{tmp_path}" 2>/dev/null || afplay "{tmp_path}" 2>/dev/null')
        except Exception as e:
            print(f"[TTS] Error en fallback de reproducción: {e}")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass


# Importación tardía para el tipo de IO
import io


# ---------------------------------------------------------------------------
# Mixin TTS_Controller
# ---------------------------------------------------------------------------
class TTS_Controller:
    """Mixin de TTS para MainWindow."""

    def _init_tts_state(self):
        self.tts_pipeline      = None
        self.tts_enabled       = True
        self._audio_thread: Optional[TTSAudioThread]       = None
        self._presynth_thread: Optional[TTSPreSynthThread] = None
        self._audio_cache: Dict[int, bytes]                = {}   # index → WAV bytes

    def _load_tts(self):
        self.status_label.setText("Cargando modelo TTS… (esto puede tomar un momento)")
        self._tts_loader = TTSLoader()
        self._tts_loader.ready.connect(self._on_tts_ready)
        self._tts_loader.failed.connect(self._on_tts_failed)
        self._tts_loader.start()

    def _on_tts_ready(self, pipeline):
        self.tts_pipeline  = pipeline
        self._audio_thread = TTSAudioThread(pipeline, speed_factor=self.spin_tts_speed.value())
        self._audio_thread.start()
        self.status_label.setText("Listo  ·  Narración de voz activada ✔")

    def _on_tts_failed(self, err: str):
        self.tts_pipeline = None
        self.tts_enabled  = False
        self.check_tts.setChecked(False)
        self.check_tts.setEnabled(False)
        self.status_label.setText(f"TTS no disponible: {err}")

    # ------------------------------------------------------------------
    # Pre-síntesis (llamar tras cargar comentarios)
    # ------------------------------------------------------------------
    def presynthesize_comments(self, comments: list):
        """
        Lanza la pre-síntesis de todos los comentarios en background.
        Cancela cualquier pre-síntesis anterior.
        """
        if self.tts_pipeline is None:
            return

        # Cancelar pre-síntesis anterior si sigue corriendo
        if self._presynth_thread and self._presynth_thread.isRunning():
            self._presynth_thread.cancel()
            self._presynth_thread.wait(3000)

        self._audio_cache = {}
        self._presynth_thread = TTSPreSynthThread(
            self.tts_pipeline, comments, self.spin_tts_speed.value()
        )
        self._presynth_thread.progress.connect(self._on_presynth_progress)
        self._presynth_thread.finished.connect(self._on_presynth_finished)
        self._presynth_thread.failed.connect(lambda e: print(f"[PreSynth] {e}"))
        self._presynth_thread.start()
        self.status_label.setText("Pre-sintetizando narración… ⏳")

    def _on_presynth_progress(self, pct: int):
        self.status_label.setText(f"Pre-sintetizando narración… {pct}%")

    def _on_presynth_finished(self, cache: dict):
        self._audio_cache = cache
        n = len(cache)
        self.status_label.setText(f"Narración lista — {n} comentario(s) pre-sintetizados ✔")

    # ------------------------------------------------------------------
    # Reproducción
    # ------------------------------------------------------------------
    def _speak(self, text: str, comment_index: int = -1):
        """
        Reproduce el comentario en el índice dado.
        Si el audio ya está en caché, usa el WAV pre-sintetizado;
        de lo contrario sintetiza en tiempo real (fallback).
        """
        if not self.tts_enabled or self._audio_thread is None:
            return
        if comment_index >= 0 and comment_index in self._audio_cache:
            self._audio_thread.speak_wav(self._audio_cache[comment_index])
        else:
            self._audio_thread.speak(text)

    def _on_tts_toggle(self, state: int):
        self.tts_enabled = bool(state)

    def _on_speed_changed(self, value: float):
        if self._audio_thread is not None:
            self._audio_thread.speed_factor = value

    def _stop_tts(self):
        if self._presynth_thread and self._presynth_thread.isRunning():
            self._presynth_thread.cancel()
            self._presynth_thread.wait(2000)
        if self._audio_thread and self._audio_thread.isRunning():
            self._audio_thread.stop()
            self._audio_thread.wait(2000)
