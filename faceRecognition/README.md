Celebrity Dataset
-
https://www.kaggle.com/datasets/vishesh1412/celebrity-face-image-dataset

## Instrucciones de Ejecución

### 1. Preparación inicial
Instala las dependencias necesarias (asegúrate de usar tu entorno virtual si tienes uno):
```bash
pip install -r requirements.txt
```

Luego, divide el dataset original en datos de entrenamiento y prueba:
```bash
python split_data.py
```

### 2. Entrenar el modelo
Para procesar las imágenes con FaceNet y entrenar el clasificador SVM, ejecuta:
```bash
python train_model.py
```
*(Opcional)* Una vez finalizado el entrenamiento, puedes evaluar la precisión del modelo con:
```bash
python evaluate_model.py
```

### 3. Ejecutar la aplicación en tiempo real
Si ya entrenaste el modelo anteriormente (es decir, ya tienes el archivo `face_recognition_model.pkl` generado), no es necesario volver a entrenar. Simplemente inicia la aplicación de la cámara directamente con:
```bash
python recognize_realtime.py
```