# EasyPiper Setup Guide

Complete installation and setup guide for EasyPiper - Pythonic wrapper for Piper robotic arm control.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Hardware Setup](#hardware-setup)
3. [Software Installation](#software-installation)
4. [CAN Device Configuration](#can-device-configuration)
5. [Verification](#verification)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.7 or higher
- **Hardware**: 
  - Piper robotic arm
  - USB-CAN adapter
  - USB cable for CAN adapter

### Required System Packages

```bash
sudo apt update
sudo apt install -y \
    python3-pip \
    python3-venv \
    git \
    can-utils \
    ethtool
```

## Hardware Setup

### 1. Connect the Hardware

1. **Power up the Piper arm**
   - Connect the power supply to the robot arm
   - Ensure the power LED is illuminated

2. **Connect the CAN adapter**
   - Plug the USB-CAN adapter into your computer's USB port
   - Connect the CAN cable from the adapter to the robot arm's CAN port

3. **Verify USB connection**
   ```bash
   lsusb | grep -i can
   ```
   You should see your CAN adapter listed.

### 2. Verify CAN Interface

Check if the CAN interface is detected:

```bash
ip link show type can
```

If no CAN interface appears, check your USB connection and ensure the adapter drivers are loaded.

## Software Installation

### Option 1: Quick Install (Recommended)

This is the fastest way to get started:

```bash
# Clone the repository with submodules
git clone --recursive https://github.com/charithmu/easy_piper.git
cd easy_piper

# Install piper_sdk submodule
cd piper_sdk
pip install -e .
cd ..

# Install EasyPiper
pip install -e .

# Or install with recording support
pip install -e .[recorder]

# Or install with all optional dependencies
pip install -e .[recorder,viz,dev]
```

### Option 2: Manual Installation

For more control over the installation process:

```bash
# Clone the repository
git clone https://github.com/charithmu/easy_piper.git
cd easy_piper

# Initialize and update submodules
git submodule update --init --recursive

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install core dependencies
pip install -r requirements.txt

# Install piper_sdk
cd piper_sdk
pip install -e .
cd ..

# Install EasyPiper in development mode
pip install -e .
```

### Option 3: Virtual Environment (Recommended for Development)

Using a virtual environment keeps your installation isolated:

```bash
# Create virtual environment
python3 -m venv ~/easy_piper_env

# Activate the environment
source ~/easy_piper_env/bin/activate

# Follow Option 1 or Option 2 steps above
```

### Installing Optional Dependencies

**Data Recording Support:**
```bash
pip install -e .[recorder]
```

**Visualization Tools:**
```bash
pip install -e .[viz]
```

**Development Tools:**
```bash
pip install -e .[dev]
```

**All Optional Features:**
```bash
pip install -e .[recorder,viz,dev]
```

## CAN Device Configuration

EasyPiper includes automatic CAN device detection and configuration. However, you can also configure it manually.

### Automatic Configuration (Recommended)

EasyPiper will automatically detect and configure your CAN device:

```python
from easy_piper import EasyPiper

# Automatic CAN setup
arm = EasyPiper()  # Uses can0, auto-detects and configures
```

### Manual Configuration

#### Find Available CAN Devices

```bash
./scripts/find_all_can_port.sh
```

This will show all detected CAN devices and their USB ports.

#### Activate a Specific CAN Device

```bash
# Activate with default name (can0)
./scripts/can_activate.sh can0 1000000

# Or specify USB port for multiple devices
./scripts/can_activate.sh can0 1000000 3-1.4:1.0
```

#### Manual CAN Setup (Advanced)

If you need to configure CAN manually:

```bash
# Bring down the interface
sudo ip link set can0 down

# Configure bitrate (1 Mbps for Piper)
sudo ip link set can0 type can bitrate 1000000

# Bring up the interface
sudo ip link set can0 up

# Verify configuration
ip -details link show can0
```

### Using Custom CAN Names

You can use custom CAN device names:

```python
from easy_piper import EasyPiper

# Use custom CAN name
arm = EasyPiper(can_name='can_piper')

# For multiple devices, specify USB port
arm = EasyPiper(can_name='can_piper', can_usb_port='3-1.4:1.0')
```

## Verification

### Test Basic Functionality

Run the simple example to verify everything works:

```bash
python3 examples/simple_example.py
```

Expected output:
- ✓ CAN device connected
- ✓ Robot arm initialized
- ✓ Motors enabled
- Robot performs basic movements
- No error messages

### Test Data Streaming

Check if robot data is streaming properly:

```python
from easy_piper import EasyPiper

arm = EasyPiper()

# Check joint state
joints = arm.get_joint_state()
print(f"Joints Hz: {joints['Hz']}")  # Should be > 10 Hz

# Check gripper state
gripper = arm.get_gripper_state()
print(f"Gripper Hz: {gripper['Hz']}")  # Should be > 10 Hz

# Check CAN bus
print(f"CAN FPS: {arm.get_can_fps()}")  # Should be > 50 FPS
```

### Run Additional Examples

Try other examples to explore features:

```bash
# Interactive recorder
python3 examples/quick_start_recorder.py

# Debug mode
python3 examples/debug_example.py

# Camera recording (if cameras available)
python3 examples/capture_cameras.py
```

## Troubleshooting

### CAN Device Not Found

**Problem**: `❌ Failed to setup CAN device 'can0'`

**Solutions**:
1. Check USB connection:
   ```bash
   lsusb | grep -i can
   ```

2. Verify CAN utilities are installed:
   ```bash
   dpkg -l | grep -E "(can-utils|ethtool)"
   ```

3. Check if interface exists:
   ```bash
   ip link show type can
   ```

4. Try manual activation:
   ```bash
   ./scripts/can_activate.sh can0 1000000
   ```

### Permission Denied Errors

**Problem**: Permission errors when accessing CAN device

**Solution**: Add your user to the appropriate groups:
```bash
sudo usermod -a -G dialout $USER
sudo usermod -a -G plugdev $USER

# Log out and log back in for changes to take effect
```

Or run with sudo (not recommended for regular use):
```bash
sudo python3 examples/simple_example.py
```

### Robot Not Responding

**Problem**: CAN configured but robot doesn't respond

**Checklist**:
1. Verify robot is powered on
2. Check CAN cable connections
3. Verify bitrate is correct (1000000 for Piper):
   ```bash
   ip -details link show can0 | grep bitrate
   ```
4. Check for CAN bus errors:
   ```bash
   candump can0
   ```

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'piper_sdk'`

**Solution**: Install the piper_sdk submodule:
```bash
cd piper_sdk
pip install -e .
cd ..
```

**Problem**: `ModuleNotFoundError: No module named 'h5py'`

**Solution**: Install recording dependencies:
```bash
pip install -e .[recorder]
```

### Multiple CAN Devices

**Problem**: Multiple CAN devices detected, unable to auto-select

**Solution**: Specify the USB port:
```python
from easy_piper import EasyPiper

# First, find your device
# Run: ./scripts/find_all_can_port.sh

# Then specify the USB port
arm = EasyPiper(can_name='can0', can_usb_port='3-1.4:1.0')
```

### Data Rate Issues

**Problem**: Low Hz reported for joint/gripper data

**Checks**:
1. Verify CAN bus FPS:
   ```python
   print(f"CAN FPS: {arm.get_can_fps()}")
   # Should be > 50 FPS
   ```

2. Check system load (high CPU usage can affect performance)

3. Verify no CAN bus errors:
   ```bash
   ip -s link show can0
   ```

### Submodule Issues

**Problem**: `piper_sdk` directory is empty

**Solution**: Initialize submodules:
```bash
git submodule update --init --recursive
```

## Next Steps

After successful installation:

1. **Read the documentation**: 
   - [User Guide](docs/EASY_PIPER_README.md)
   - [API Reference](docs/EASY_PIPER_CHEATSHEET.md)
   - [Quick Card](docs/EASY_PIPER_QUICK_CARD.md)

2. **Try the examples**: Explore the `examples/` directory

3. **Record data**: Use `piper-recorder` for imitation learning data collection

4. **Join the community**: Report issues and contribute on [GitHub](https://github.com/charithmu/easy_piper)

## Additional Resources

- [CAN Setup Guide](docs/CAN_SETUP_GUIDE.md) - Detailed CAN configuration
- [Recorder Guide](docs/PIPER_RECORDER_README.md) - Data recording for ML
- [Mode Switching](docs/MODE_SWITCH_CHEATSHEET.md) - SDK mode reference
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [documentation](docs/)
2. Search [existing issues](https://github.com/charithmu/easy_piper/issues)
3. Create a [new issue](https://github.com/charithmu/easy_piper/issues/new) with:
   - Your system details
   - Error messages
   - Steps to reproduce

Happy robot controlling! 🤖
