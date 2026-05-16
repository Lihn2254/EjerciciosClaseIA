import os
import cv2
import numpy as np
import joblib
from keras_facenet import FaceNet
from sklearn.metrics import accuracy_score, classification_report
from train_model import load_images_from_folder

def evaluate():
    test_dir = os.path.join("dataset_split", "test")
    model_path = "face_recognition_model.pkl"
    
    if not os.path.exists(test_dir):
        print(f"Test directory '{test_dir}' not found. Please run split_data.py first.")
        return
        
    if not os.path.exists(model_path):
        print(f"Model file '{model_path}' not found. Please run train_model.py first.")
        return

    print("Loading the saved model and encoder...")
    saved_data = joblib.load(model_path)
    svm_model = saved_data["model"]
    label_encoder = saved_data["encoder"]

    print("Loading validation dataset...")
    X_test_images, y_test_labels = load_images_from_folder(test_dir)
    print(f"Loaded {len(X_test_images)} testing images.")
    
    if len(X_test_images) == 0:
        print("No test images found.")
        return

    print("Loading FaceNet model...")
    embedder = FaceNet()

    print("Extracting testing embeddings...")
    test_embeddings = embedder.embeddings(X_test_images)

    print("Predicting classes on test set...")
    # Get predictions as numerical classes
    y_pred_encoded = svm_model.predict(test_embeddings)
    
    # Decode numerical predictions back to actual names
    y_pred_labels = label_encoder.inverse_transform(y_pred_encoded)
    
    # Calculate accuracy
    accuracy = accuracy_score(y_test_labels, y_pred_labels)
    print("\n" + "="*40)
    print(f"Overall Model Accuracy: {accuracy * 100:.2f}%")
    print("="*40)
    
    print("\nClassification Report:")
    # This report shows Precision, Recall, and F1-score for each person separately
    print(classification_report(y_test_labels, y_pred_labels))

if __name__ == "__main__":
    evaluate()
