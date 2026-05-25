from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtWidgets import QSlider
from PyQt6.QtCore import QUrl, Qt


class VideoPlayer:
    """
    Mixin de reproducción de video y sincronización de comentarios.
    Se usa junto con QMainWindow y TTS_Controller en herencia múltiple.

    Cambios respecto a la versión original:
      • _on_slider_moved limpia text_comments al instante, evitando
        que los comentarios se acumulen al retroceder/adelantar.
      • on_position_changed maneja correctamente los tres casos:
          1. Avance normal         → append nuevos comentarios
          2. Retroceso (seek)      → clear + repintar hasta posición actual
          3. Sin cambio de índice  → no-op
      • _append_comment ya no recibe speak=bool; en su lugar acepta
        comment_index para que _speak() use el caché WAV si está disponible.
    """

    # ------------------------------------------------------------------
    # Inicialización — llamar desde _init_ui de MainWindow
    # ------------------------------------------------------------------
    def _init_video_player(self, left_layout):
        self.video_widget = QVideoWidget()
        self.video_widget.setMinimumSize(640, 480)
        self.video_widget.setMaximumSize(1280, 720)
        left_layout.addWidget(self.video_widget)

        self.position_slider = QSlider(Qt.Orientation.Horizontal)
        left_layout.addWidget(self.position_slider)

        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setVideoOutput(self.video_widget)

        self.media_player.positionChanged.connect(self.on_position_changed)
        self.media_player.durationChanged.connect(self._on_duration_changed)
        self.position_slider.sliderMoved.connect(self._on_slider_moved)

        # Estado de comentarios
        self.comments_data            = []
        self.last_shown_comment_index = -1
        self._seeking                 = False   # bandera para detectar saltos de slider

    # ------------------------------------------------------------------
    # Slots de reproducción
    # ------------------------------------------------------------------
    def play_video(self):
        self.media_player.play()

    def pause_video(self):
        self.media_player.pause()

    def _on_duration_changed(self, duration: int):
        self.position_slider.setRange(0, duration)

    def _on_slider_moved(self, position: int):
        """
        El usuario movió el slider manualmente.
        Limpiamos el panel y reseteamos el índice ANTES de que
        on_position_changed reciba el nuevo tiempo, para que la
        lógica de repintado entre por la rama correcta (retroceso/seek).
        """
        self.text_comments.clear()
        self.last_shown_comment_index = -1
        self._seeking = True
        self.media_player.setPosition(position)

    def load_video(self, file_path: str):
        """Carga un archivo de video y resetea el estado de comentarios."""
        self.media_player.setSource(QUrl.fromLocalFile(file_path))
        self.text_comments.clear()
        self.comments_data            = []
        self.last_shown_comment_index = -1
        self._seeking                 = False
        self.position_slider.setValue(0)
        self.btn_play.setEnabled(False)
        self.btn_pause.setEnabled(False)

    def load_comments(self, comments: list):
        """
        Recibe la lista de comentarios ya ordenada desde MainWindow.
        Lanza la pre-síntesis de audio en background (TTS_Controller).
        """
        self.comments_data            = comments
        self.last_shown_comment_index = -1
        self.text_comments.clear()
        # Dispara pre-síntesis si TTS_Controller lo expone
        if hasattr(self, "presynthesize_comments"):
            self.presynthesize_comments(comments)

    # ------------------------------------------------------------------
    # Sincronización de comentarios con el tiempo del video
    # ------------------------------------------------------------------
    def on_position_changed(self, position_ms: int):
        self.position_slider.setValue(position_ms)
        if not self.comments_data:
            return

        current_time_s = position_ms / 1000.0

        # Calcula cuántos comentarios deberían estar visibles en este instante
        desired_index = -1
        for i, c in enumerate(self.comments_data):
            if current_time_s >= c["timestamp"]:
                desired_index = i
            else:
                break

        if desired_index == self.last_shown_comment_index:
            # Sin cambio: nada que hacer
            self._seeking = False
            return

        if desired_index < self.last_shown_comment_index or self._seeking:
            # Retroceso o seek manual: limpiar y repintar sin narrar
            self.text_comments.clear()
            for i in range(desired_index + 1):
                self._append_comment(self.comments_data[i], comment_index=i, speak=False)
            self.last_shown_comment_index = desired_index
            self._seeking = False

        else:
            # Avance normal: agregar solo los comentarios nuevos
            latest_index = -1
            for i in range(self.last_shown_comment_index + 1, desired_index + 1):
                self._append_comment(self.comments_data[i], comment_index=i, speak=False)
                latest_index = i
            self.last_shown_comment_index = desired_index

            # Narrar únicamente el comentario más reciente
            if latest_index >= 0:
                self._speak(
                    self.comments_data[latest_index]["comment"],
                    comment_index=latest_index,
                )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _append_comment(self, comment_dict: dict, comment_index: int = -1, speak: bool = False):
        time_fmt = self._format_time(comment_dict["timestamp"])
        html     = f"<b>[{time_fmt}]</b>: {comment_dict['comment']}<br><br>"
        self.text_comments.append(html)
        if speak:
            self._speak(comment_dict["comment"], comment_index=comment_index)

    @staticmethod
    def _format_time(seconds: float) -> str:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
