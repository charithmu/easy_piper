# CAN Device Setup Guide for EasyPiper

EasyPiper can automatically detect and configure CAN devices for Piper robot arm communication.

## Quick Start (Automatic Setup)

The easiest way - EasyPiper handles everything:

```python
from easy_piper import EasyPiper

# Automatic CAN detection and setup
arm = EasyPiper()  # Uses 'can0' by default
```

This will:
1. Check if `can0` exists and is configured
2. If not, search for available CAN devices
3. Automatically configure the device
4. Connect to the robot arm

## Manual CAN Device Name

Specify a custom CAN device name:

```python
arm = EasyPiper(can_name='can_piper')
```

## Multiple CAN Devices

When you have multiple USB-CAN adapters (e.g., for arm + chassis):

### 1. Find USB Ports

First, identify each device's USB port:

```bash
cd /path/to/easy_piper
bash scripts/find_all_can_port.sh
```

Output example:
```
Interface can0 is connected to USB port 3-1.4:1.0
Interface can1 is connected to USB port 3-1.1:1.0
```

### 2. Specify USB Port in Code

```python
# Arm on USB port 3-1.4:1.0
arm = EasyPiper(can_name='can_arm', can_usb_port='3-1.4:1.0')

# Chassis on USB port 3-1.1:1.0
chassis = SomeChassisClass(can_name='can_chassis', can_usb_port='3-1.1:1.0')
```

## Disable Automatic Setup

If you prefer manual CAN configuration:

```python
# Configure CAN manually first
import subprocess
subprocess.run(['bash', 'scripts/can_activate.sh', 'can0', '1000000'])

# Then create EasyPiper without auto-setup
arm = EasyPiper(can_name='can0', auto_setup_can=False)
```

## Manual CAN Setup (Command Line)

### Single CAN Device

```bash
bash scripts/can_activate.sh can0 1000000
```

- `can0`: Desired CAN device name
- `1000000`: Bitrate (must be 1000000 for Piper arms)

### Multiple CAN Devices

When multiple USB-CAN adapters are connected:

```bash
# Setup arm CAN (at USB port 3-1.4:1.0)
bash scripts/can_activate.sh can_arm 1000000 "3-1.4:1.0"

# Setup chassis CAN (at USB port 3-1.1:1.0)
bash scripts/can_activate.sh can_chassis 1000000 "3-1.1:1.0"
```

### Verify Setup

Check if CAN device is configured:

```bash
ifconfig can0
# or
ip link show can0
```

Should show `UP` and `state UP`.

## Troubleshooting

### No CAN Devices Found

**Problem:** `scripts/find_all_can_port.sh` finds no devices.

**Solutions:**
1. Check USB-CAN adapter is plugged in
2. Install required packages:
   ```bash
   sudo apt update
   sudo apt install can-utils ethtool iproute2
   ```
3. Try different USB port
4. Check if device is recognized:
   ```bash
   lsusb
   dmesg | grep -i can
   ```

### CAN Device Exists But Not UP

**Problem:** Device shows in `scripts/find_all_can_port.sh` but not UP.

**Solution:**
```bash
bash scripts/can_activate.sh can0 1000000
```

Or in Python:
```python
arm = EasyPiper(can_name='can0')  # auto_setup_can=True by default
```

### Connection Fails After CAN Setup

**Problem:** CAN device is UP but robot doesn't respond.

**Check:**
1. Robot arm is powered on
2. CAN cable is properly connected
3. Correct CAN device is being used:
   ```python
   arm = EasyPiper(can_name='can0')
   print(arm.iface.GetCanName())  # Verify CAN device name
   ```

### Multiple Devices - Wrong Device Used

**Problem:** Multiple CAN adapters, connecting to wrong one.

**Solution:** Specify USB port explicitly:
```python
# Find ports first
import subprocess
result = subprocess.run(['bash', 'scripts/find_all_can_port.sh'], 
                       capture_output=True, text=True)
print(result.stdout)

# Then specify the correct port
arm = EasyPiper(can_name='can_arm', can_usb_port='3-1.4:1.0')
```

### Permission Denied

**Problem:** Cannot configure CAN device (permission errors).

**Solution:** Scripts need sudo access for `ip link` commands:
```bash
# Grant sudo access for scripts/can_activate.sh
sudo bash scripts/can_activate.sh can0 1000000
```

Or add user to appropriate group and configure sudoers.

## Advanced: Persistent CAN Names

To have consistent CAN device names across reboots, use udev rules:

1. Find USB port and create udev rule:
```bash
# File: /etc/udev/rules.d/99-piper-can.rules
SUBSYSTEM=="net", ACTION=="add", KERNELS=="3-1.4:1.0", NAME="can_piper"
```

2. Reload udev:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

3. Now the device will always be named `can_piper`:
```python
arm = EasyPiper(can_name='can_piper')
```

## Common Patterns

### Development/Testing (Single Arm)
```python
# Simplest - auto everything
arm = EasyPiper()
```

### Production (Specific Device)
```python
# Explicit device name
arm = EasyPiper(can_name='can_piper')
```

### Multi-Robot System
```python
# Arm at specific USB port
arm = EasyPiper(can_name='can_arm', can_usb_port='3-1.4:1.0')

# Chassis at different USB port
chassis = ChassisClass(can_name='can_chassis', can_usb_port='3-1.1:1.0')
```

### Manual Control (No Auto-Setup)
```python
# Setup CAN manually first
import subprocess
subprocess.run(['sudo', 'bash', 'scripts/can_activate.sh', 'can0', '1000000'])

# Connect without auto-setup
arm = EasyPiper(can_name='can0', auto_setup_can=False)
```

## Script Reference

### scripts/find_all_can_port.sh

**Purpose:** Discover all CAN devices and their USB ports.

**Usage:**
```bash
bash scripts/find_all_can_port.sh
```

**Output:**
```
Both ethtool and can-utils are installed.
Interface can0 is connected to USB port 3-1.4:1.0
Interface can1 is connected to USB port 3-1.1:1.0
```

### scripts/can_activate.sh

**Purpose:** Configure and activate a CAN device.

**Usage:**
```bash
bash scripts/can_activate.sh <can_name> <bitrate> [usb_port]
```

**Parameters:**
- `can_name`: Desired CAN device name (e.g., 'can0', 'can_piper')
- `bitrate`: CAN bitrate - must be `1000000` for Piper arms
- `usb_port`: Optional USB hardware address (e.g., '3-1.4:1.0')

**Examples:**
```bash
# Single device (auto-detect)
bash scripts/can_activate.sh can0 1000000

# Specific USB port
bash scripts/can_activate.sh can_arm 1000000 "3-1.4:1.0"
```

## Requirements

- Linux system (Ubuntu 18.04+, 20.04, 22.04 tested)
- Python 3.6+
- Packages:
  ```bash
  sudo apt install can-utils ethtool iproute2
  pip install python-can
  ```

## See Also

- [EASY_PIPER_README.md](EASY_PIPER_README.md) - Main EasyPiper documentation
- [EASY_PIPER_CHEATSHEET.md](EASY_PIPER_CHEATSHEET.md) - API reference
- Main README.MD - Detailed CAN setup for SDK
