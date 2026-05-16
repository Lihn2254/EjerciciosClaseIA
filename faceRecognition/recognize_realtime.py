import cv2
import numpy as np
import joblib
from keras_facenet import FaceNet

def start_recognition():
    model_path = "face_recognition_model.pkl"
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    
    # Load required classifiers and model
    try:
        saved_data = joblib.load(model_path)
        svm_model = saved_data["model"]
        label_encoder = saved_data["encoder"]
    except FileNotFoundError:
        print(f"Error: Model '{model_path}' not found. Please train first.")
        return

    face_cascade = cv2.CascadeClassifier(cascade_path)
    if face_cascade.empty():
        print("Error: Could not load the Haar Cascade XML file.")
        return

    embedder = FaceNet()
    
    # Threshold for deciding if a person is "Unknown"
    confidence_threshold = 0.50

    cap = cv2.VideoCapture(0)
    window_name = 'Real-Time Face Recognition (Press "Q" to quit)'
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    if hasattr(cv2, "WND_PROP_TOPMOST"):
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

    print("Opening webcam...")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
        
        # Detect if the window was closed via the 'X' button
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

        # Haar Cascades require grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100)
        )

        for (x, y, w, h) in faces:
            # Extract the actual face segment and color from original camera frame
            face_img = frame[y:y+h, x:x+w]
            
            # Prepare image matching the training data constraints:
            # 1. Convert BGR to RGB
            # 2. Resize to 160x160
            face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            face_resized = cv2.resize(face_rgb, (160, 160))
            
            # Embeddings expect a batch, so we wrap the single frame in an array
            img_batch = np.expand_dims(face_resized, axis=0)
            
            # Get the embedding representation for this face
            embedding = embedder.embeddings(img_batch)
            
            # Predict who it is
            predictions = svm_model.predict_proba(embedding)
            max_prob_index = np.argmax(predictions[0])
            confidence = predictions[0][max_prob_index]
            predicted_class = svm_model.predict(embedding)
            
            name = "Unknown"
            if confidence >= confidence_threshold:
                name = label_encoder.inverse_transform(predicted_class)[0]

            # Construct drawing overlay
            text = f"{name} ({confidence*100:.1f}%)"
            box_color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            
            # Draw box around face
            cv2.rectangle(frame, (x, y), (x+w, y+h), box_color, 2)
            
            # Draw name and confidence text
            cv2.putText(
                frame, text, (x, max(10, y - 10)), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, box_color, 2
            )

        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_recognition()
