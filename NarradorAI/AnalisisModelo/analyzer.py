import cv2
import base64
import requests
import json
import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from google import genai
from google.genai import types
from PyQt6.QtCore import QThread, pyqtSignal


class VideoAnalyzerSignals(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(str)  # Contains path to the resulting JSON
    error = pyqtSignal(str)

    def __init__(
        self,
        video_path,
        interval=2.0,
        api_type="ollama",
        ollama_url="http://localhost:11434",
        force_reanalyze=False
    ):
        super().__init__()
        self.video_path = video_path
        self.interval = interval
        self.api_type = api_type
        self.ollama_url = ollama_url
        self.force_reanalyze = force_reanalyze

        current_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = os.path.join(current_dir, '.env')
        load_dotenv(dotenv_path=env_path)
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY", "")

        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

        self.openai_client = None
        if self.openai_api_key:
            self.openai_client = OpenAI(api_key=self.openai_api_key)

        self.json_path = f"{os.path.splitext(self.video_path)[0]}_comments.json"

    def run(self):
        try:
            if os.path.exists(self.json_path):
                if self.force_reanalyze:
                    self.log.emit("Forzando nuevo análisis. Borrando historial anterior...")
                    os.remove(self.json_path) # Borra el archivo viejo
                else:
                    self.log.emit("Comments JSON already exists. Skipping analysis.")
                    self.finished.emit(self.json_path)
                    return

            self.log.emit(f"Starting video analysis using {self.api_type}...")

            self.model = None
            if self.api_type == "gemini":
                if self.api_key == "":
                    self.error.emit(
                        "Gemini API key is not set. Please provide an API key."
                    )
                    return
            elif self.api_type == "openai":
                if self.openai_api_key == "":
                    self.error.emit(
                        "OpenAI API key is not set. Please provide an OPENAI_API_KEY."
                    )
                    return

            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                self.error.emit("Could not open video file.")
                return

            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.log.emit(f"Video stats: FPS={fps}, Total Frames={total_frames}")

            frame_interval = int(fps * self.interval)
            current_frame = 0

            comments = []

            prompt = (
                "Actúa como un comentarista profesional de esports de Valorant (estilo VCT). "
                "Tu objetivo es narrar la acción con lenguaje técnico, variado y preciso. "
                "Prohibido usar muletillas repetitivas como 'increíble', 'wow' o 'espectacular'. "
                "Analiza este frame enfocándote en estos detalles: "
                "1. Lee el Killfeed (arriba a la derecha) para mencionar nombres de jugadores o el arma utilizada si hay una baja (recuerda que los muertos aparecen a la derecha y los vivos aparecen a la izquierda del killfeed). "
                "2. Si hay un enfrentamiento, usa jerga del juego (ej. 'tradeo', 'clutch', 'entry', 'pikeando'). "
                "Reglas de formato: Escribe un comentario de máximo 20 palabras. Texto plano, sin emojis. "
                "Si es que hubo alguna kill (o multikill), menciona unicamente el suceso. "
                "Si la pantalla está tranquila (fase de barreras, solo caminando por el mapa o campeando sin enemigos cerca), responde ÚNICAMENTE con la palabra 'SKIP'."
            )

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if current_frame % frame_interval == 0:
                    timestamp = current_frame / fps

                    self.log.emit(f"Analyzing frame at {timestamp:.2f}s...")

                    # 1. Redimensionar el frame para evitar el colapso de RAM/VRAM
                    frame_resized = cv2.resize(frame, (1280, 720))

                    # 2. Convertir a jpg con un poco de compresión (ej. 80% de calidad)
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
                    _, buffer = cv2.imencode(".jpg", frame_resized, encode_param)

                    frame_base64 = base64.b64encode(buffer).decode("utf-8")

                    if self.api_type == "gemini":
                        comment = self._analyze_frame_with_gemini(prompt, frame_base64)
                    elif self.api_type == "openai":
                        comment = self._analyze_frame_with_openai(prompt, frame_base64)
                    else:
                        comment = self._analyze_frame_with_ollama(frame_base64, prompt)
                    print(f"Raw comment: {comment.strip()}")
                    if (
                        comment
                        and comment.strip().upper() != "SKIP"
                        and "SKIP" not in comment.strip().upper()
                    ):
                        # Filter out non-notable frames
                        print(f"Generated comment: {comment.strip()}")
                        comments.append(
                            {"timestamp": timestamp, "comment": comment.strip()}
                        )
                        self.log.emit(f"Comment generated: {comment.strip()}")
                    
                    if self.api_type in ["gemini", "openai"]:
                        time.sleep(5)  # Pequeña pausa para evitar saturar la API

                current_frame += 1
                progress_pct = int((current_frame / total_frames) * 100)
                self.progress.emit(progress_pct)

            cap.release()

            # Save to JSON
            with open(self.json_path, "w", encoding="utf-8") as f:
                json.dump(comments, f, indent=4, ensure_ascii=False)

            self.log.emit("Analysis finished.")
            self.finished.emit(self.json_path)

        except Exception as e:
            self.error.emit(str(e))

    def _analyze_frame_with_gemini(self, prompt, base64_image):
        try:
            if self.client is None:
                return "SKIP"

            response = self.client.models.generate_content(
                model='gemini-3.5-flash',
                contents=[
                    types.Content(
                        parts=[
                            types.Part(text=prompt),
                            types.Part(
                                inline_data=types.Blob(
                                    mime_type="image/jpeg",
                                    data=base64_image
                                )
                            )
                        ]
                    )
                ]
                #contents=[prompt, image_part]
            )
            return response.text
        except Exception as e:
            print(f"Gemini API error: {e}")
            return "SKIP"

    def _analyze_frame_with_openai(self, prompt, base64_image):
        try:
            if self.openai_client is None:
                return "SKIP"

            # OpenAI requiere que el base64 lleve el prefijo del tipo de dato
            image_data_uri = f"data:image/jpeg;base64,{base64_image}"

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "Eres un comentarista enérgico y creativo del videojuego Valorant."
                    },
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data_uri
                                }
                            }
                        ]
                    }
                ],
                max_tokens=50, # Reducido a 50 para forzar respuestas cortas y ahorrar tokens
                temperature=0.8,
            )
            
            if response.choices:
                return response.choices[0].message.content.strip()
            return "SKIP"
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return "SKIP"

    def _analyze_frame_with_ollama(self, base64_image, prompt):
        payload = {
            "model": "gemma4:e4b",
            "prompt": prompt,
            "images": [base64_image],
            "stream": False,
        }
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate", json=payload, timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "SKIP")
        except Exception as e:
            print(f"Ollama API error: {e}")
            return "SKIP"
