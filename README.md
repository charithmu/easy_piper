# EasyPiper - Pythonic Wrapper for Piper Robotic Arm Control

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

Pythonic wrapper for Piper robotic arm control with automatic CAN device setup and intuitive API.

## 🚀 Quick Start

```python
from easy_piper import EasyPiper

# That's it! Automatic CAN detection and configuration
arm = EasyPiper()

# Use the arm
arm.enable(wait=True)
arm.switch_mode_joint(speed_percent=30)
arm.go_zero_joints()
```

## ✨ Features

### Robot Control
- ✅ **Automatic CAN Setup** - Detects and configures CAN devices automatically
- ✅ **Unit Conversion** - Use degrees, mm, N·m (not 0.001× units)
- ✅ **Pythonic API** - Clear, intuitive method names
- ✅ **Multiple Control Modes** - Joint space, Cartesian space, teach mode
- ✅ **Gripper Control** - Position and force control
- ✅ **Comprehensive Feedback** - Read joints, TCP pose, gripper state, and more

### Data Collection
- 🎥 **PiperRecorder** - Record trajectories for imitation learning
- 📊 **LeRobot Compatible** - HDF5 format compatible with LeRobot library
- 📈 **Visualization Tools** - Plot and analyze recorded data

## 📦 Installation

### Option 1: Quick Install (Recommended)

```bash
# Clone with submodules
git clone --recursive https://github.com/<YOUR_USERNAME>/easy_piper.git
cd easy_piper

# Install piper_sdk submodule
cd piper_sdk
pip install -e .
cd ..

# Install EasyPiper
pip install -e .

# Or with recording support
pip install -e .[recorder]
```

### Option 2: Manual Installation

```bash
# Clone the repository
git clone https://github.com/<YOUR_USERNAME>/easy_piper.git
cd easy_piper

# Initialize submodules
git submodule update --init --recursive

# Install dependencies
pip install -r requirements.txt

# Install piper_sdk
cd piper_sdk
pip install -e .
cd ..

# Install EasyPiper
pip install -e .
```

For detailed setup instructions, see [CAN Setup Guide](docs/CAN_SETUP_GUIDE.md).

## 📖 Usage

### Basic Control

```python
from easy_piper import EasyPiper

# Initialize (automatic CAN detection)
arm = EasyPiper()

# Enable the arm
arm.enable(wait=True)

# Joint space control
arm.switch_mode_joint(speed_percent=30)
arm.go_to_joint_angles([0, 30, -60, 0, 90, 0])  # degrees

# Cartesian space control
arm.switch_mode_move_l(speed_percent=20)
arm.go_to_tcp_pose(300, 0, 400, 180, 0, 0)  # mm and degrees

# Gripper control
arm.gripper_enable(effort=1000, clear_error=True)
arm.gripper_move(width_mm=20, effort_nm=1.5)  # Open
arm.gripper_move(width_mm=0, effort_nm=1.0)  # Close

# Disable when done
arm.disable()
```

### Recording Data for Imitation Learning

```python
from easy_piper import EasyPiper

# Initialize arm
arm = EasyPiper()
arm.enable(wait=True)

# Use the interactive CLI recorder
# See examples/quick_start_recorder.py for detailed usage
```

Use the interactive CLI recorder:
```bash
piper-recorder
# Or: python3 -m easy_piper.piper_recorder
# Then use commands: start <episode_name>, stop, status, quit
```

## 📁 Project Structure

```
easy_piper/
├── src/
│   └── easy_piper/            # Main package
│       ├── __init__.py        # Package initialization
│       ├── easy_piper.py      # Core EasyPiper class
│       ├── piper_recorder.py  # Data recorder for imitation learning
│       └── piper_analyze.py   # Recording analysis and visualization
├── examples/                  # Example scripts
│   ├── simple_example.py
│   ├── easy_piper_demo.py
│   ├── test_recorder_setup.py
│   └── quick_start_recorder.py
├── scripts/                   # Utility scripts
│   ├── can_activate.sh              # CAN device activation
│   ├── find_all_can_port.sh         # CAN device discovery
│   ├── upload_to_huggingface.py     # Upload datasets to Hugging Face
│   ├── hf_login.py                  # Hugging Face authentication
│   ├── crop_table_cam_images.py     # Image processing for table camera
│   └── flip_wrist_cam_images.py     # Image processing for wrist camera
├── docs/                      # Documentation
│   ├── EASY_PIPER_README.md
│   ├── EASY_PIPER_CHEATSHEET.md
│   ├── PIPER_RECORDER_README.md
│   ├── CAN_SETUP_GUIDE.md
│   └── MODE_SWITCH_CHEATSHEET.md
├── tests/                     # Unit tests
├── notebooks/                 # Jupyter notebooks
├── piper_sdk/                 # Git submodule (Piper SDK)
├── piper_sdk_gui/             # Git submodule (UI, optional)
├── setup.py                   # Package setup
├── requirements.txt           # Python dependencies
├── LICENSE                    # MIT License
└── CONTRIBUTING.md            # Contribution guidelines
```

## 📚 Documentation

- [**User Guide**](docs/EASY_PIPER_README.md) - Complete guide with all features
- [**API Cheatsheet**](docs/EASY_PIPER_CHEATSHEET.md) - Quick reference for all methods
- [**Quick Card**](docs/EASY_PIPER_QUICK_CARD.md) - Ultra-condensed reference
- [**Recorder Guide**](docs/PIPER_RECORDER_README.md) - Data recording documentation
- [**CAN Setup**](docs/CAN_SETUP_GUIDE.md) - Detailed CAN configuration guide
- [**Hugging Face Upload**](docs/HUGGINGFACE_UPLOAD_GUIDE.md) - Upload datasets to Hugging Face
- [**Mode Switching**](docs/MODE_SWITCH_CHEATSHEET.md) - SDK mode control reference

## 🛠️ CAN Device Setup

EasyPiper automatically detects and configures CAN devices. For manual setup:

```bash
# Find available CAN devices
./scripts/find_all_can_port.sh

# Activate a specific device
./scripts/can_activate.sh can_piper
```

See [docs/CAN_SETUP_GUIDE.md](docs/CAN_SETUP_GUIDE.md) for detailed instructions.

## 🔧 Command-Line Tools

EasyPiper includes several CLI tools for common workflows:

### Data Recording
```bash
# Record robot demonstrations
piper-recorder --can-name can0 --output-dir ./recordings --fps 30

# With camera recording (requires opencv-python)
piper-recorder --enable-cameras
```

### Data Analysis
```bash
# View episode information
piper-analyze recordings/episode_001.hdf5

# Generate trajectory plots
piper-analyze recordings/episode_001.hdf5 --plot

# Export to numpy arrays
piper-analyze recordings/episode_001.hdf5 --export-numpy ./data
```

### Hugging Face Upload
```bash
# Login to Hugging Face (one-time)
python3 scripts/hf_login.py

# Upload recordings to Hugging Face Hub
python3 scripts/upload_to_huggingface.py
```

See [docs/PIPER_RECORDER_README.md](docs/PIPER_RECORDER_README.md) and [docs/HUGGINGFACE_UPLOAD_GUIDE.md](docs/HUGGINGFACE_UPLOAD_GUIDE.md) for details.

## 🎯 Use Cases

- **Robotics Research** - Control Piper arms with Pythonic interface
- **Imitation Learning** - Collect demonstration data in LeRobot format
- **Automation** - Build automated pick-and-place systems
- **Education** - Teach robotics programming with intuitive API
- **Prototyping** - Quickly test robot behaviors

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
pip install -e .[dev]
```

### Running Tests

```bash
pytest tests/
```

### Code Style

```bash
black .
flake8 .
```

## 📋 Requirements

- Python 3.7+
- Linux (tested on Ubuntu 20.04+)
- CAN-bus hardware
- Piper robotic arm

## 🔗 Dependencies

- `piper_sdk` - Official Piper SDK (included as submodule)
- `numpy` - Numerical operations
- `python-can` - CAN bus communication
- `h5py` - HDF5 file format (for recording)
- `opencv-python` - Camera capture and image processing (optional, for `--enable-cameras`)
- `matplotlib` - Visualization (optional)
- `huggingface_hub` - Upload datasets to Hugging Face (optional)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on top of [Agilex Robotics Piper SDK](https://github.com/agilexrobotics/piper_sdk)
- Compatible with [LeRobot](https://github.com/huggingface/lerobot) for imitation learning

## 📧 Contact

- **Author**: Charith Munasinghe
- **Issues**: [GitHub Issues](https://github.com/<YOUR_USERNAME>/easy_piper/issues)

## 🚀 Getting Started

1. Follow the installation instructions above
2. Run `python3 examples/simple_example.py`
3. Read the [User Guide](docs/EASY_PIPER_README.md)
4. Check out more [examples](examples/)

Happy robot controlling! 🤖
