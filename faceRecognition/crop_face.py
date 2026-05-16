import os
import glob
import cv2


def crop_faces_in_batch(input_directory, output_directory):
    """
    Processes a batch of images, crops out human faces,
    and outputs one image per detected face. Discards images with 0 faces.
    """

    # Create the output directory if it does not exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Load the pre-trained Haar Cascade for frontal faces included with OpenCV
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)

    if face_cascade.empty():
        print("Error: Could not load the Haar Cascade XML file.")
        return

    # Gather all standard image files from the input directory
    supported_extensions = ("*.jpg", "*.jpeg", "*.png")
    image_paths = []
    for ext in supported_extensions:
        image_paths.extend(glob.glob(os.path.join(input_directory, ext)))
        # Also check for uppercase extensions
        image_paths.extend(glob.glob(os.path.join(input_directory, ext.upper())))

    successful_crops = 0
    discarded_images = 0

    print(f"Found {len(image_paths)} images in '{input_directory}'. Processing...")

    for img_path in image_paths:
        # Read the image
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Could not read {img_path}. Skipping.")
            continue

        # Convert the image to grayscale (Haar cascades require grayscale)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect faces
        # scaleFactor, minNeighbors, and minSize can be adjusted depending on your dataset
        faces = face_cascade.detectMultiScale(
            gray_img, scaleFactor=1.1, minNeighbors=6, minSize=(160, 160)
        )

        # Discard images with no faces
        if len(faces) == 0:
            discarded_images += 1
            continue

        # Get the base filename and extension
        filename = os.path.basename(img_path)
        name_without_ext, ext = os.path.splitext(filename)

        # Process each detected face
        for face_idx, (x, y, w, h) in enumerate(faces, start=1):
            # Crop the original color image to the face's bounding box
            cropped_face = img[y : y + h, x : x + w]

            # Construct the output file path
            # If only one face, keep the simple naming; if multiple, add face number
            if len(faces) == 1:
                output_filename = f"cropped_{filename}"
            else:
                output_filename = f"cropped_{name_without_ext}_face{face_idx}{ext}"

            output_path = os.path.join(output_directory, output_filename)
            cv2.imwrite(output_path, cropped_face)
            successful_crops += 1

    # Print summary statistics
    print("-" * 30)
    print("Batch Processing Complete")
    print(f"Successfully Cropped Faces: {successful_crops}")
    print(f"Images Discarded (0 faces): {discarded_images}")


# ==========================================
# Example Usage
# ==========================================
if __name__ == "__main__":
    # Define your folder paths here
    INPUT_FOLDER = "input_images"
    OUTPUT_FOLDER = "cropped_faces"

    crop_faces_in_batch(INPUT_FOLDER, OUTPUT_FOLDER)
