"""
MainWindow — ventana principal de Narrador IA.
"""

import json

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QDoubleSpinBox,
    QTextEdit, QProgressBar, QMessageBox, QComboBox, QCheckBox,
)
from PyQt6.QtCore import Qt

from NarradorAI.AnalisisModelo.analyzer import VideoAnalyzerSignals
from NarradorAI.TTS.TTS_Controller import TTS_Controller
from NarradorAI.TTS.video_player   import VideoPlayer


class MainWindow(TTS_Controller, VideoPlayer, QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Narrador IA - Automated Valorant Commentary")
        self.resize(1000, 700)

        self.analyzer_thread    = None
        self.current_video_path = None

        self._init_tts_state()   # TTS_Controller
        self._init_ui()
        self._load_tts()         # TTS_Controller — arranca el loader en background

    # Construcción de la UI
    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # ── Columna izquierda: video + controles ──────────────────────
        left_layout = QVBoxLayout()

        self._init_video_player(left_layout)   # VideoPlayer — crea video_widget, slider y media_player

        controls_layout = QHBoxLayout()

        self.btn_select_video = QPushButton("Selecciona un video")
        self.btn_select_video.clicked.connect(self.select_video)
        controls_layout.addWidget(self.btn_select_video)

        self.btn_play = QPushButton("Reproducir")
        self.btn_play.clicked.connect(self.play_video)
        self.btn_play.setEnabled(False)
        controls_layout.addWidget(self.btn_play)

        self.btn_pause = QPushButton("Pausar")
        self.btn_pause.clicked.connect(self.pause_video)
        self.btn_pause.setEnabled(False)
        controls_layout.addWidget(self.btn_pause)

        controls_layout.addWidget(QLabel("Tasa de muestra (s):"))
        self.spin_rate = QDoubleSpinBox()
        self.spin_rate.setRange(0.5, 60.0)
        self.spin_rate.setValue(2.0)
        self.spin_rate.setSingleStep(0.5)
        controls_layout.addWidget(self.spin_rate)

        self.combo_model = QComboBox()
        self.combo_model.addItems(["ollama", "gemini", "openai"])
        controls_layout.addWidget(self.combo_model)

        self.check_force = QCheckBox("Forzar nuevo análisis")
        self.check_force.setToolTip("Ignora el análisis previo y vuelve a procesar el video desde cero.")
        controls_layout.addWidget(self.check_force)

        self.check_tts = QCheckBox("Narración de voz")
        self.check_tts.setChecked(True)
        self.check_tts.setToolTip("Activa/desactiva la síntesis de voz en español.")
        self.check_tts.stateChanged.connect(self._on_tts_toggle)   # TTSController
        controls_layout.addWidget(self.check_tts)

        controls_layout.addWidget(QLabel("Vel. voz:"))
        self.spin_tts_speed = QDoubleSpinBox()
        self.spin_tts_speed.setRange(0.5, 3.0)
        self.spin_tts_speed.setValue(1.4)
        self.spin_tts_speed.setSingleStep(0.1)
        self.spin_tts_speed.setDecimals(1)
        self.spin_tts_speed.setToolTip(
            "Velocidad de narración (1.0 = normal, 1.4 = 40% más rápido).\n"
            "Cambia en tiempo real; se aplica al siguiente comentario."
        )
        self.spin_tts_speed.valueChanged.connect(self._on_speed_changed)  # TTSController
        controls_layout.addWidget(self.spin_tts_speed)

        self.btn_analyze = QPushButton("Comenzar Análisis")
        self.btn_analyze.clicked.connect(self.start_analysis)
        self.btn_analyze.setEnabled(False)
        controls_layout.addWidget(self.btn_analyze)

        left_layout.addLayout(controls_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        left_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Listo")
        left_layout.addWidget(self.status_label)

        main_layout.addLayout(left_layout, stretch=2)

        # ── Columna derecha: panel de comentarios ─────────────────────
        right_layout = QVBoxLayout()
        lbl_comments = QLabel("Comentarios")
        lbl_comments.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(lbl_comments)

        self.text_comments = QTextEdit()
        self.text_comments.setReadOnly(True)
        right_layout.addWidget(self.text_comments)

        main_layout.addLayout(right_layout, stretch=1)

    # ------------------------------------------------------------------
    # Selección de video
    # ------------------------------------------------------------------
    def select_video(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Abrir Video", "", "Archivo de video (*.mp4 *.avi *.mkv)"
        )
        if file_path:
            self.current_video_path = file_path
            self.status_label.setText(f"Seleccionado: {file_path}")
            self.btn_analyze.setEnabled(True)
            self.progress_bar.setValue(0)
            self.load_video(file_path)   # VideoPlayer

    # ------------------------------------------------------------------
    # Análisis
    # ------------------------------------------------------------------
    def start_analysis(self):
        if not self.current_video_path:
            return
        self.media_player.stop()
        self.btn_analyze.setEnabled(False)
        self.btn_select_video.setEnabled(False)
        self.btn_play.setEnabled(False)
        self.btn_pause.setEnabled(False)
        self.text_comments.clear()

        self.analyzer_thread = VideoAnalyzerSignals(
            video_path      = self.current_video_path,
            interval        = self.spin_rate.value(),
            api_type        = self.combo_model.currentText(),
            force_reanalyze = self.check_force.isChecked(),
        )
        self.analyzer_thread.progress.connect(self.progress_bar.setValue)
        self.analyzer_thread.log.connect(self.status_label.setText)
        self.analyzer_thread.finished.connect(self._on_analysis_finished)
        self.analyzer_thread.error.connect(self._on_analysis_error)
        self.analyzer_thread.start()

    def _on_analysis_finished(self, json_path: str):
        self.btn_analyze.setEnabled(True)
        self.btn_select_video.setEnabled(True)
        self.btn_play.setEnabled(True)
        self.btn_pause.setEnabled(True)
        self.status_label.setText("Análisis completado. Listo para reproducir")
        self.progress_bar.setValue(100)
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                comments = json.load(f)
            comments.sort(key=lambda x: x["timestamp"])
            self.load_comments(comments)   # VideoPlayer
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load comments JSON:\n{e}")

    def _on_analysis_error(self, err_msg: str):
        self.btn_analyze.setEnabled(True)
        self.btn_select_video.setEnabled(True)
        QMessageBox.critical(self, "Analysis Error", f"An error occurred:\n{err_msg}")
        self.status_label.setText("Analysis failed.")

    # ------------------------------------------------------------------
    # Cierre de la app
    # ------------------------------------------------------------------
    def closeEvent(self, event):
        self._stop_tts()   # TTSController
        super().closeEvent(event)