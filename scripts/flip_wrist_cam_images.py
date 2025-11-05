#!/usr/bin/env python3
"""
Script to flip vertically all images in folders ending with .wrist_cam
"""

from pathlib import Path
from PIL import Image

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    def tqdm(iterable, **kwargs):
        return iterable

def find_wrist_cam_folders(base_path):
    """Find all folders ending with .wrist_cam"""
    base = Path(base_path)
    wrist_cam_folders = []
    
    for item in base.rglob("*"):
        if item.is_dir() and item.name.endswith(".wrist_cam"):
            wrist_cam_folders.append(item)
    
    return wrist_cam_folders

def flip_images_in_folder(folder_path):
    """Flip all images vertically in the given folder"""
    folder = Path(folder_path)
    image_files = list(folder.glob("*.png")) + list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg"))
    
    print(f"\nProcessing folder: {folder}")
    print(f"Found {len(image_files)} images")
    
    for img_path in tqdm(image_files, desc=f"Flipping images in {folder.name}"):
        try:
            # Open image
            img = Image.open(img_path)
            
            # Flip vertically
            flipped_img = img.transpose(Image.FLIP_TOP_BOTTOM)
            
            # Save back (overwrite original)
            flipped_img.save(img_path)
            
        except Exception as e:
            print(f"Error processing {img_path}: {e}")

def main():
    # Base path to recordings folder
    base_path = Path(__file__).parent.parent / "recordings"
    
    print(f"Searching for wrist_cam folders in: {base_path}")
    
    # Find all wrist_cam folders
    wrist_cam_folders = find_wrist_cam_folders(base_path)
    
    print(f"\nFound {len(wrist_cam_folders)} wrist_cam folders:")
    for folder in wrist_cam_folders:
        print(f"  - {folder.relative_to(base_path)}")
    
    if not wrist_cam_folders:
        print("No wrist_cam folders found!")
        return
    
    # Process each folder
    for folder in wrist_cam_folders:
        flip_images_in_folder(folder)
    
    print("\n✓ All wrist_cam images have been flipped vertically!")

if __name__ == "__main__":
    main()
