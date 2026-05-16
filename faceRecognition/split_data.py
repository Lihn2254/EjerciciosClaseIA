import os
import shutil
import random

def split_dataset(src_dir="dataset", dest_dir="dataset_split", split_ratio=0.8):
    """
    Reads the original dataset and copies images into train and test folders.
    Leaves the original dataset folder intact.
    """
    if not os.path.exists(src_dir):
        print(f"Source directory '{src_dir}' not found.")
        return

    train_dir = os.path.join(dest_dir, "train")
    test_dir = os.path.join(dest_dir, "test")

    # Create destination directories if they don't exist
    for d in [train_dir, test_dir]:
        if not os.path.exists(d):
            os.makedirs(d)

    # Iterate over every person in the dataset
    for person_name in os.listdir(src_dir):
        person_path = os.path.join(src_dir, person_name)
        
        # Skip if it's not a directory
        if not os.path.isdir(person_path):
            continue
            
        # Collect all image files for this person
        images = [f for f in os.listdir(person_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not images:
            continue
            
        # Shuffle images for randomness
        random.shuffle(images)
        
        # Calculate split index
        split_idx = int(len(images) * split_ratio)
        train_images = images[:split_idx]
        test_images = images[split_idx:]
        
        # Create person folders in train and test directories
        person_train_dir = os.path.join(train_dir, person_name)
        person_test_dir = os.path.join(test_dir, person_name)
        
        os.makedirs(person_train_dir, exist_ok=True)
        os.makedirs(person_test_dir, exist_ok=True)
        
        # Copy files to train directory
        for img in train_images:
            src_img = os.path.join(person_path, img)
            dest_img = os.path.join(person_train_dir, img)
            shutil.copy2(src_img, dest_img)
            
        # Copy files to test directory
        for img in test_images:
            src_img = os.path.join(person_path, img)
            dest_img = os.path.join(person_test_dir, img)
            shutil.copy2(src_img, dest_img)
            
        print(f"Processed '{person_name}': {len(train_images)} train, {len(test_images)} test images.")
        
    print(f"\nDataset successfully split into '{dest_dir}/train' and '{dest_dir}/test'!")

if __name__ == "__main__":
    # Splitting 80% for training and 20% for testing
    split_dataset("dataset", "dataset_split", split_ratio=0.8)
