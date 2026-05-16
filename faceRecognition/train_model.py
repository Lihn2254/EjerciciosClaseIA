import os
import cv2
import numpy as np
import joblib
from keras_facenet import FaceNet
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder

def load_images_from_folder(folder_path):
    """
    Reads all person subfolders inside folder_path.
    Returns:
        images: list of cropped loaded images (numpy arrays).
        labels: list of corresponding person names.
    """
    images = []
    labels = []
    
    for person_name in os.listdir(folder_path):
        person_dir = os.path.join(folder_path, person_name)
        if not os.path.isdir(person_dir):
            continue
            
        for img_name in os.listdir(person_dir):
            img_path = os.path.join(person_dir, img_name)
            img = cv2.imread(img_path)
            
            if img is None:
                continue
                
            # FaceNet requires RGB format instead of OpenCV's default BGR
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Ensure the image is 160x160 as expected by FaceNet
            img_resized = cv2.resize(img_rgb, (160, 160))
            
            images.append(img_resized)
            labels.append(person_name)
            
    return np.array(images), np.array(labels)

def train():
    train_dir = os.path.join("dataset", "train")
    if not os.path.exists(train_dir):
        print(f"Training directory '{train_dir}' not found. Please run split_data.py first.")
        return

    print("Loading training dataset...")
    X_images, y_labels = load_images_from_folder(train_dir)
    print(f"Loaded {len(X_images)} training images across {len(set(y_labels))} people.")
    
    # Encode string labels (names) to integer classes
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y_labels)

    # Load FaceNet Extractor
    print("Loading FaceNet model... this may take a moment.")
    embedder = FaceNet()
    
    # Extract Embeddings
    print("Extracting facial embeddings (can take a while)...")
    # FaceNet takes a batch of images and returns 512-dimensional embeddings
    embeddings = embedder.embeddings(X_images)
    
    # Train SVM Classifier
    print("Training the SVM classifier...")
    # probability=True allows us to get confidence scores later during real-time inference
    model = SVC(kernel='linear', probability=True)
    model.fit(embeddings, y_encoded)
    
    # Save the SVM model and the LabelEncoder
    print("Saving the trained model to 'face_recognition_model.pkl'...")
    joblib.dump({"model": model, "encoder": encoder}, "face_recognition_model.pkl")
    print("Training finished successfully.")

if __name__ == "__main__":
    train()
