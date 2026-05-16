import os
import cv2

# Configuraciones
nombre_persona = input("Ingresa el nombre de la persona: ").strip()
while not nombre_persona:
    nombre_persona = input("El nombre no puede estar vacío. Ingresa el nombre de la persona: ").strip()

cantidad_fotos = int(input("Número de imágenes a capturar (max. 500): "))
while cantidad_fotos > 500 or cantidad_fotos < 1:
    cantidad_fotos = input("Ingrese un número válido: ")

carpeta_dest = f"dataset/{nombre_persona}"
if not os.path.exists(carpeta_dest):
    os.makedirs(carpeta_dest)

prefijo_archivo = f"{nombre_persona}_"
max_indice_existente = -1
for nombre_archivo in os.listdir(carpeta_dest):
    if not nombre_archivo.lower().endswith(".jpg"):
        continue
    if not nombre_archivo.startswith(prefijo_archivo):
        continue

    parte_numerica = os.path.splitext(nombre_archivo)[0][len(prefijo_archivo):]
    if parte_numerica.isdigit():
        max_indice_existente = max(max_indice_existente, int(parte_numerica))

indice_inicial = max_indice_existente + 1

# Cargar el detector de rostros (Haar Cascade es el más rápido para esto)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)
count = 0
window_name = 'Capturando Dataset - Presiona Q para salir'

cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
# Intenta mantener la ventana al frente en sistemas compatibles.
if hasattr(cv2, "WND_PROP_TOPMOST"):
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

print("Iniciando captura... Muévete un poco, cambia de expresión y ángulo.")

while count < cantidad_fotos: # Capturará 100 fotos
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        # Recortar solo el rostro
        rostro_recortado = frame[y:y+h, x:x+w]
        rostro_resize = cv2.resize(rostro_recortado, (160, 160)) # El tamaño que pide tu tarea
        
        # Guardar imagen
        indice_actual = indice_inicial + count
        cv2.imwrite(f"{carpeta_dest}/{nombre_persona}_{indice_actual}.jpg", rostro_resize)
        
        # Dibujar rectángulo en pantalla para que veas qué captura
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        count += 1

    cv2.imshow(window_name, frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print(f"¡Listo! Se guardaron {count} fotos en {carpeta_dest}")
