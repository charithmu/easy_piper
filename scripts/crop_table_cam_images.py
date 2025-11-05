#!/usr/bin/env python3
"""
Script to crop all images in folders ending with .table_cam
Crop size: 800x720+300+0 (800x720 pixels, offset by 300 pixels from left)
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

def find_table_cam_folders(base_path):
    """Find all folders ending with .table_cam"""
    base = Path(base_path)
    table_cam_folders = []
    
    for item in base.rglob("*"):
        if item.is_dir() and item.name.endswith(".table_cam"):
            table_cam_folders.append(item)
    
    return table_cam_folders

def crop_images_in_folder(folder_path, crop_box):
    """Crop all images in the given folder"""
    folder = Path(folder_path)
    image_files = list(folder.glob("*.png")) + list(folder.glob("*.jpg")) + list(folder.glob("*.jpeg"))
    
    print(f"\nProcessing folder: {folder}")
    print(f"Found {len(image_files)} images")
    
    for img_path in tqdm(image_files, desc=f"Cropping images in {folder.name}"):
        try:
            # Skip already processed sample files
            if "cropped_sample" in img_path.name:
                continue
                
            # Open image
            img = Image.open(img_path)
            
            # Crop image
            cropped_img = img.crop(crop_box)
            
            # Save back (overwrite original)
            cropped_img.save(img_path)
            
        except Exception as e:
            print(f"Error processing {img_path}: {e}")

def main():
    # Base path to recordings folder
    base_path = Path(__file__).parent.parent / "recordings"
    
    # Crop parameters: 800x720+300+0
    # Format: (left, top, right, bottom)
    # left=300, top=0, right=300+800=1100, bottom=0+720=720
    crop_box = (300, 0, 1100, 720)
    
    print(f"Searching for table_cam folders in: {base_path}")
    print(f"Crop settings: 800x720+300+0 -> box {crop_box}")
    
    # Find all table_cam folders
    table_cam_folders = find_table_cam_folders(base_path)
    
    print(f"\nFound {len(table_cam_folders)} table_cam folders:")
    for folder in table_cam_folders:
        print(f"  - {folder.relative_to(base_path)}")
    
    if not table_cam_folders:
        print("No table_cam folders found!")
        return
    
    # Process each folder
    for folder in table_cam_folders:
        crop_images_in_folder(folder, crop_box)
    
    print("\n✓ All table_cam images have been cropped!")

if __name__ == "__main__":
    main()
