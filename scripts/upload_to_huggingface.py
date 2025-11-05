#!/usr/bin/env python3
"""
Script to upload robotic teaching episodes to Hugging Face Hub
Uses the datasets library for efficient upload with Git LFS support
"""

import os
from pathlib import Path
from huggingface_hub import HfApi, create_repo, login

def setup_huggingface():
    """Login to Hugging Face (interactive or use token)"""
    print("=" * 60)
    print("HUGGING FACE SETUP")
    print("=" * 60)
    
    # Check if already logged in
    token = os.environ.get("HF_TOKEN")
    if token:
        print("✓ Using HF_TOKEN from environment")
        login(token=token)
    else:
        print("\nPlease login to Hugging Face:")
        print("Option 1: Run 'huggingface-cli login' in terminal first")
        print("Option 2: Set HF_TOKEN environment variable")
        print("Option 3: Enter token when prompted below")
        try:
            login()
            print("✓ Login successful!")
        except Exception as e:
            print(f"✗ Login failed: {e}")
            print("\nRun this first: huggingface-cli login")
            return False
    return True

def create_dataset_card(repo_id, recordings_path):
    """Create a README.md dataset card"""
    recordings = Path(recordings_path)
    
    # Count episodes and files
    hdf5_files = list(recordings.glob("*.hdf5"))
    json_files = list(recordings.glob("*.json"))
    image_dirs = [d for d in recordings.iterdir() if d.is_dir() and d.name.endswith("_images")]
    
    # Get episode names
    episodes = set()
    for f in hdf5_files:
        # Extract episode name (everything before timestamp)
        parts = f.stem.split("_")
        if len(parts) >= 3:
            episode_name = "_".join(parts[:-2])
            episodes.add(episode_name)
    
    card_content = f"""---
license: mit
task_categories:
  - robotics
  - imitation-learning
tags:
  - robotics
  - teleoperation
  - manipulation
  - robot-learning
  - demonstration-data
size_categories:
  - 1K<n<10K
---

# PiPER Robot Teaching Episodes Dataset

This dataset contains teleoperation demonstrations recorded using the PiPER robotic system.

## Dataset Description

- **Total Episodes**: {len(hdf5_files)}
- **Unique Tasks**: {len(episodes)}
- **Total Size**: ~6.2 GB
- **Cameras**: Dual camera setup (table_cam + wrist_cam)
- **Recording Date**: November 2024

## Tasks Included

{chr(10).join([f"- {episode}" for episode in sorted(episodes)])}

## Dataset Structure

```
dataset/
├── {{episode_name}}_{{timestamp}}.hdf5  # Robot state, action, and compressed image data
├── {{episode_name}}_{{timestamp}}.json  # Episode metadata
└── {{episode_name}}_images/
    ├── observation.images.table_cam/    # Table view images (800x720, cropped)
    │   └── frame_XXXXXX.png
    └── observation.images.wrist_cam/    # Wrist view images (vertically flipped)
        └── frame_XXXXXX.png
```

## Data Format

### HDF5 Files
Each `.hdf5` file contains:
- `observations/state`: Robot joint states (7-DOF)
- `observations/images/table_cam`: Compressed table camera images
- `observations/images/wrist_cam`: Compressed wrist camera images  
- `actions`: Robot actions/commands
- `timestamps`: Frame timestamps

### JSON Metadata
Each `.json` file contains:
- Episode name and duration
- Number of frames and FPS
- State dimension and statistics (mean, std, min, max)
- Recording timestamp
- Camera configuration

### Image Folders
Extracted and processed images:
- **table_cam**: Cropped to 800x720 pixels (offset 300,0)
- **wrist_cam**: Vertically flipped for correct orientation

## Usage

```python
from pathlib import Path
import h5py
import json
from PIL import Image

# Load episode
episode_path = "screwdriver_20251104_203022.hdf5"
with h5py.File(episode_path, 'r') as f:
    states = f['observations/state'][:]
    actions = f['actions'][:]
    timestamps = f['timestamps'][:]

# Load metadata
with open(episode_path.replace('.hdf5', '.json'), 'r') as f:
    metadata = json.load(f)
    print(f"Episode: {{metadata['episode_name']}}")
    print(f"Frames: {{metadata['n_frames']}}, Duration: {{metadata['duration_seconds']:.2f}}s")

# Load images
image_dir = Path(f"{{metadata['episode_name']}}_images")
frame_0_table = Image.open(image_dir / "observation.images.table_cam" / "frame_000000.png")
frame_0_wrist = Image.open(image_dir / "observation.images.wrist_cam" / "frame_000000.png")
```

## Citation

If you use this dataset, please cite:

```bibtex
@dataset{{piper_teaching_episodes_2024,
  title={{PiPER Robot Teaching Episodes Dataset}},
  author={{Your Name}},
  year={{2024}},
  publisher={{Hugging Face}},
  howpublished={{\\url{{https://huggingface.co/datasets/{repo_id}}}}}
}}
```

## License

MIT License - See LICENSE file for details.

## Additional Information

- **Robot Platform**: PiPER (link to robot documentation if available)
- **Control Interface**: Teleoperation with human demonstrations
- **Processing**: Images have been preprocessed (cropping, flipping) for ML training

For questions or issues, please open an issue in the repository.
"""
    
    return card_content

def upload_to_huggingface(recordings_path, repo_id, private=False):
    """
    Upload recordings to Hugging Face Hub
    
    Args:
        recordings_path: Path to recordings directory
        repo_id: Repository ID (username/dataset-name)
        private: Whether to make the repository private
    """
    recordings_path = Path(recordings_path)
    
    print("\n" + "=" * 60)
    print(f"UPLOADING DATASET: {repo_id}")
    print("=" * 60)
    
    api = HfApi()
    
    # Create repository
    print(f"\n1. Creating repository: {repo_id}")
    try:
        create_repo(
            repo_id=repo_id,
            repo_type="dataset",
            private=private,
            exist_ok=True
        )
        print(f"✓ Repository created/found: https://huggingface.co/datasets/{repo_id}")
    except Exception as e:
        print(f"✗ Error creating repository: {e}")
        return False
    
    # Create and upload README
    print("\n2. Creating dataset card (README.md)")
    readme_content = create_dataset_card(repo_id, recordings_path)
    readme_path = recordings_path / "README.md"
    readme_path.write_text(readme_content)
    print("✓ Dataset card created")
    
    # Upload folder
    print("\n3. Uploading files (this may take a while for 6.2GB)...")
    print("   Using upload_large_folder for better handling of large datasets")
    print("   Git LFS will handle large files automatically")
    print("   Progress will be shown every 60 seconds...")
    
    try:
        api.upload_large_folder(
            repo_id=repo_id,
            folder_path=str(recordings_path),
            repo_type="dataset",
            num_workers=4,  # Parallel uploads
            allow_patterns=None,  # Upload everything
            ignore_patterns=[".git/*", "*.pyc", "__pycache__/*", "*_cropped_sample.png"],  # Skip git and temp files
            print_report=True,
            print_report_every=60
        )
        print("\n✓ Upload complete!")
        print(f"\n🎉 Dataset available at: https://huggingface.co/datasets/{repo_id}")
        return True
        
    except Exception as e:
        print(f"\n✗ Upload failed: {e}")
        print("\nTroubleshooting:")
        print("- Check your internet connection")
        print("- Verify your HF token has write permissions")
        print("- The upload may have partially completed - check the repo")
        print(f"- Visit: https://huggingface.co/datasets/{repo_id}")
        return False

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("PIPER DATASET UPLOAD TO HUGGING FACE")
    print("=" * 60)
    
    # Configuration
    recordings_path = Path(__file__).parent.parent / "recordings"
    
    print("\nConfiguration:")
    print(f"  Source: {recordings_path}")
    print(f"  Size: ~6.2 GB")
    
    # Get repository ID
    print("\n" + "-" * 60)
    repo_id = input("Enter repository ID (username/dataset-name): ").strip()
    if not repo_id or "/" not in repo_id:
        print("✗ Invalid repository ID. Format: username/dataset-name")
        return
    
    # Ask if private
    private = input("Make repository private? (y/N): ").strip().lower() == 'y'
    
    # Setup and login
    if not setup_huggingface():
        return
    
    # Confirm upload
    print("\n" + "-" * 60)
    print("Ready to upload:")
    print(f"  Repository: {repo_id}")
    print(f"  Private: {private}")
    print(f"  Source: {recordings_path}")
    print("-" * 60)
    
    confirm = input("Proceed with upload? (y/N): ").strip().lower()
    if confirm != 'y':
        print("✗ Upload cancelled")
        return
    
    # Upload
    success = upload_to_huggingface(recordings_path, repo_id, private)
    
    if success:
        print("\n" + "=" * 60)
        print("NEXT STEPS")
        print("=" * 60)
        print(f"1. Visit: https://huggingface.co/datasets/{repo_id}")
        print("2. Edit the dataset card if needed")
        print("3. Add tags and update metadata")
        print("4. Share with the community!")
        print("\nTo load the dataset:")
        print(f"  from huggingface_hub import hf_hub_download")
        print(f"  hf_hub_download(repo_id='{repo_id}', filename='screwdriver_20251104_203022.hdf5')")

if __name__ == "__main__":
    main()
