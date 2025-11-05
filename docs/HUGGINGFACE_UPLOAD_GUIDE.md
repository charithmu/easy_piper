# Uploading PiPER Dataset to Hugging Face - Complete Guide

## Overview

You have **6.2 GB** of robotic teaching episodes to upload to Hugging Face. Here are the best methods ranked by recommendation:

---

## ✅ Method 1: Using `huggingface_hub` Python Library (RECOMMENDED)

**Best for**: Programmatic upload, automation, reproducibility

### Prerequisites
```bash
pip install huggingface_hub
```

### Login
```bash
# One-time setup
huggingface-cli login
```

### Upload Script
We've created `/home/charith/projects/PiPER/easy_piper/scripts/upload_to_huggingface.py`

**Usage**:
```bash
cd /home/charith/projects/PiPER/easy_piper
python3 scripts/upload_to_huggingface.py
```

**Advantages**:
- ✅ Handles Git LFS automatically for large files
- ✅ Creates professional dataset card (README.md)
- ✅ Supports resumable uploads
- ✅ Scriptable and reproducible
- ✅ Progress tracking

**Disadvantages**:
- Requires Python environment setup
- Need to install huggingface_hub

---

## Method 2: Using Hugging Face CLI

**Best for**: Command-line users, quick uploads

### Prerequisites
```bash
pip install huggingface_hub[cli]
huggingface-cli login
```

### Upload Commands
```bash
cd /home/charith/projects/PiPER/easy_piper

# Create repository
huggingface-cli repo create your-username/piper-teaching-episodes --type dataset

# Upload entire folder
huggingface-cli upload your-username/piper-teaching-episodes recordings/ . --repo-type dataset
```

**Advantages**:
- ✅ Simple command-line interface
- ✅ Handles Git LFS automatically
- ✅ Resume interrupted uploads

**Disadvantages**:
- Manual README creation
- Less control over upload process

---

## Method 3: Using Git with Git LFS

**Best for**: Git power users, version control enthusiasts

### Prerequisites
```bash
sudo apt-get install git-lfs
git lfs install
```

### Steps
```bash
# 1. Create repository on huggingface.co/new-dataset
# 2. Clone it
git clone https://huggingface.co/datasets/your-username/piper-teaching-episodes
cd piper-teaching-episodes

# 3. Configure Git LFS for large files
git lfs track "*.hdf5"
git lfs track "*.png"
git lfs track "*.jpg"
git add .gitattributes

# 4. Copy your data
cp -r /home/charith/projects/PiPER/easy_piper/recordings/* .

# 5. Commit and push
git add .
git commit -m "Add robot teaching episodes"
git push
```

**Advantages**:
- ✅ Full Git version control
- ✅ Familiar Git workflow
- ✅ Granular control over commits

**Disadvantages**:
- Manual Git LFS setup required
- Slower for very large datasets
- More complex for beginners

---

## Method 4: Using `datasets` Library (For ML Integration)

**Best for**: Creating a proper Hugging Face Dataset with metadata

### Prerequisites
```bash
pip install datasets
```

### Create Dataset Script
```python
from datasets import Dataset, DatasetDict, Features, Value, Image
import h5py
import json
from pathlib import Path

def load_episode(episode_path):
    """Load one episode"""
    with h5py.File(episode_path, 'r') as f:
        states = f['observations/state'][:]
        actions = f['actions'][:]
        
    json_path = episode_path.replace('.hdf5', '.json')
    with open(json_path) as f:
        metadata = json.load(f)
    
    return {
        'episode_name': metadata['episode_name'],
        'states': states.tolist(),
        'actions': actions.tolist(),
        'n_frames': metadata['n_frames'],
        'duration': metadata['duration_seconds']
    }

# Load all episodes
episodes = []
for hdf5_file in Path('recordings').glob('*.hdf5'):
    episodes.append(load_episode(str(hdf5_file)))

# Create dataset
dataset = Dataset.from_list(episodes)

# Push to hub
dataset.push_to_hub("your-username/piper-teaching-episodes")
```

**Advantages**:
- ✅ Native Hugging Face Dataset format
- ✅ Easy to load with `load_dataset()`
- ✅ Streamable for large datasets
- ✅ Built-in data processing

**Disadvantages**:
- Requires restructuring data
- May not preserve original file structure
- More setup code needed

---

## Method 5: Web UI Upload

**Best for**: Small files, quick tests (NOT recommended for 6.2GB)

### Steps
1. Go to https://huggingface.co/new-dataset
2. Create dataset repository
3. Use "Files" tab to drag-and-drop upload

**Advantages**:
- ✅ No setup required
- ✅ Visual interface

**Disadvantages**:
- ❌ Not suitable for 6.2 GB dataset
- ❌ Browser may crash/timeout
- ❌ No resume capability
- ❌ Very slow for many files

---

## 🏆 Recommendation

**For your 6.2GB dataset with 9,177 images + HDF5 files:**

### Use Method 1 (Python Script) - Here's why:

1. **Automated** - Runs unattended
2. **Professional** - Creates complete dataset card
3. **Reliable** - Git LFS handles large files
4. **Resumable** - Can recover from interruptions
5. **Fast** - Efficient multi-threaded upload

### Quick Start Guide

```bash
# 1. Install requirements
pip install huggingface_hub Pillow

# 2. Login (one-time)
huggingface-cli login
# Paste your token from: https://huggingface.co/settings/tokens

# 3. Run the upload script
cd /home/charith/projects/PiPER/easy_piper
python3 scripts/upload_to_huggingface.py

# 4. Follow prompts:
#    - Enter: your-username/piper-teaching-episodes
#    - Private: N (or Y if you want private)
#    - Confirm: y
```

### Expected Upload Time
- **6.2 GB** on typical broadband (10 Mbps upload) ≈ **1-2 hours**
- Progress will be shown during upload

---

## After Upload - Best Practices

### 1. Edit Dataset Card
Visit your repo and enhance the README:
- Add robot specifications
- Add example code
- Add visualizations
- Link to paper/project

### 2. Add Dataset Tags
```yaml
tags:
  - robotics
  - teleoperation
  - manipulation
  - imitation-learning
  - piper-robot
```

### 3. Add License
Choose appropriate license (MIT, Apache-2.0, etc.)

### 4. Create Data Loading Example
```python
from huggingface_hub import hf_hub_download

# Download specific episode
file = hf_hub_download(
    repo_id="your-username/piper-teaching-episodes",
    filename="screwdriver_20251104_203022.hdf5",
    repo_type="dataset"
)
```

---

## Troubleshooting

### Upload Fails
```bash
# Re-login
huggingface-cli logout
huggingface-cli login

# Check token permissions at: https://huggingface.co/settings/tokens
# Token needs 'write' permission
```

### Git LFS Issues
```bash
# Increase Git timeout
git config --global http.postBuffer 524288000
git config --global http.timeout 600
```

### Large File Errors
Files > 5GB need special handling. Your files are small enough (largest ~100KB HDF5), so no issues.

---

## Alternative: Zenodo for Archival

If you also want DOI for academic citation:
1. Upload to Hugging Face (for ML community)
2. Also archive on Zenodo (for academic citation)

Both are free and complement each other well.

---

## Questions?

Run the upload script and it will guide you through the process:
```bash
python3 scripts/upload_to_huggingface.py
```
