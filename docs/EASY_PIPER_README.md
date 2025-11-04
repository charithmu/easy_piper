# EasyPiper - Pythonic Piper SDK Wrapper

A simple, user-friendly wrapper around the Piper SDK (`C_PiperInterface_V2`) that provides intuitive, Pythonic methods for controlling Piper robotic arms.

## Features

- **Automatic CAN setup**: Detects and configures CAN devices automatically
- **Automatic unit conversion**: Use degrees, mm, and N·m instead of 0.001° and 0.001 mm
- **Clear method names**: `enable()`, `go_zero_joints()`, `gripper_move()` instead of cryptic CAN codes
- **Safety first**: Built-in `reset_sequence()` for safe recovery
- **Comprehensive coverage**: Exposes all important SDK functionality
- **Type hints**: Full type annotations for better IDE support
- **Well documented**: Every method links back to the SDK reference

## Quick Start

### Automatic Setup (Recommended)

EasyPiper automatically detects and configures CAN devices:

```python
from easy_piper import EasyPiper
import time

# Initialize with automatic CAN setup
arm = EasyPiper()  # Uses 'can0', auto-configures if needed
```

### Manual CAN Device Selection

Specify a custom CAN device:

```python
# Use specific CAN device name
arm = EasyPiper(can_name='can_piper')

# Multiple CAN devices - specify USB port
arm = EasyPiper(can_name='can_arm', can_usb_port='3-1.4:1.0')

# Disable automatic CAN setup
arm = EasyPiper(can_name='can0', auto_setup_can=False)
```

### Basic Usage

```python
from easy_piper import EasyPiper
import time

# Initialize and auto-connect
arm = EasyPiper()

# Enable motors
arm.enable(wait=True)

# Move joints
arm.switch_mode_joint(speed_percent=30)
arm.go_zero_joints()
time.sleep(2)

# Move to specific joint angles (degrees)
arm.go_to_joint_angles([0, -30, 45, 0, 60, 0])
time.sleep(2)

# Linear TCP motion (mm and degrees)
arm.switch_mode_move_l(speed_percent=40)
arm.go_to_tcp_pose(
    X_mm=150, Y_mm=0, Z_mm=200,
    RX_deg=0, RY_deg=90, RZ_deg=0
)
time.sleep(2)

# Control gripper (mm and N·m)
arm.gripper_enable(effort=1000, clear_error=True)
arm.gripper_move(width_mm=30, effort_nm=1.5)
time.sleep(1)
arm.gripper_move(width_mm=0, effort_nm=2.0)

# Read feedback
tcp = arm.get_current_tcp()
print(f"TCP Position: X={tcp['X_mm']:.2f}, Y={tcp['Y_mm']:.2f}, Z={tcp['Z_mm']:.2f} mm")

joints = arm.get_joint_state()
print(f"Joint 1: {joints['j1_deg']:.2f}°")

# Safe shutdown
arm.emergency_stop()
arm.disable()
arm.disconnect()
```

## Installation

EasyPiper is included with the Piper SDK:

```bash
pip install piper-sdk
```

Or if installing from source:

```bash
cd piper_sdk
pip install -e .
```

## CAN Device Setup

EasyPiper can automatically configure CAN devices, but you can also set them up manually.

### Automatic Setup (Default)

```python
# Auto-detects and configures CAN device
arm = EasyPiper()
```

### Manual Setup

See **[CAN_SETUP_GUIDE.md](CAN_SETUP_GUIDE.md)** for detailed instructions on:
- Finding CAN devices
- Configuring multiple CAN adapters
- Manual activation scripts
- Troubleshooting CAN issues

Quick manual setup:
```bash
# Find CAN devices
bash scripts/find_all_can_port.sh

# Activate CAN device
bash scripts/can_activate.sh can0 1000000

# Or with specific USB port
bash scripts/can_activate.sh can_arm 1000000 "3-1.4:1.0"
```

## Documentation

### Complete Reference
See **[EASY_PIPER_CHEATSHEET.md](../EASY_PIPER_CHEATSHEET.md)** for comprehensive method listing and examples.

### SDK Documentation
- **[MODE_SWITCH_CHEATSHEET.md](../MODE_SWITCH_CHEATSHEET.md)** - Detailed mode switching and control
- **[piper_sdk/interface/piper_interface_v2.py](../piper_sdk/interface/piper_interface_v2.py)** - Full SDK interface
- **[piper_sdk/demo/V2/](../piper_sdk/demo/V2/)** - SDK example scripts

## Key Features

### Power & Safety
```python
arm.enable(wait=True, timeout_s=3.0)  # Enable motors
arm.disable()                          # Disable motors
arm.emergency_stop()                   # E-stop
arm.resume()                           # Resume after E-stop
arm.reset_sequence(speed_percent=30)   # Full reset cycle
```

### Mode Switching
```python
arm.switch_mode_joint(speed_percent=30)    # Joint/position mode
arm.switch_mode_move_p(speed_percent=30)   # Point-to-point Cartesian
arm.switch_mode_move_l(speed_percent=40)   # Linear Cartesian
arm.switch_mode_move_c(speed_percent=30)   # Circular/arc motion
arm.switch_mode_mit(speed_percent=0)       # MIT/drag-teach mode
```

### Motion Control
```python
# Joint motion (degrees)
arm.go_zero_joints()
arm.go_to_joint_angles([0, -30, 45, 0, 60, 0])

# TCP motion (mm, degrees)
arm.go_zero_tcp(mode='L', speed_percent=30)
arm.go_to_tcp_pose(X_mm=100, Y_mm=0, Z_mm=250,
                   RX_deg=0, RY_deg=90, RZ_deg=0)

# Circular motion
arm.switch_mode_move_c(speed_percent=30)
arm.go_to_tcp_pose(...)  # Start point
arm.move_c_update(1)
# ... intermediate and end points
```

### Gripper Control
```python
arm.gripper_enable(effort=1000, clear_error=True)
arm.gripper_disable(clear_error=False)
arm.gripper_set_zero()
arm.gripper_move(width_mm=20, effort_nm=1.5)
```

### Teach Mode
```python
arm.teach_start()        # Enter drag-teach mode
# ... manually move arm ...
arm.teach_end()          # Exit teach mode
arm.teach_execute()      # Play back trajectory
arm.teach_pause()        # Pause playback
arm.teach_continue()     # Resume playback
arm.trajectory_clear()   # Clear trajectory
```

### Feedback Reading
```python
# Current state (with unit conversion)
tcp = arm.get_current_tcp()          # Dict: X_mm, Y_mm, Z_mm, RX_deg, RY_deg, RZ_deg, Hz
joints = arm.get_joint_state()       # Dict: j1_deg, j2_deg, ..., j6_deg, Hz
gripper = arm.get_gripper_state()    # Dict: angle_mm, effort_nm, foc_status, Hz

# System status
mode = arm.get_current_mode()        # Current mode structure
status = arm.get_arm_status()        # Arm status
enabled = arm.get_enable_status()    # Enable status for all joints
ok = arm.is_ok()                     # Check if arm is OK
connected = arm.get_connection_status()  # Check connection
```

### Configuration
```python
# Joint configuration
arm.set_joint_zero(joint_num=7)      # Set current as zero (7=all)
arm.clear_joint_error(joint_num=7)   # Clear errors
arm.set_joint_max_acc(motor_num=1, max_acc=500)
arm.set_joint_max_speed(motor_num=1, max_speed=3000)

# End effector
arm.set_end_load(load_type=3)
arm.set_end_speed_acc(max_linear_vel, max_angular_vel, 
                      max_linear_acc, max_angular_acc)

# Collision protection
arm.set_crash_protection(j1_level=0, j2_level=0, j3_level=0,
                         j4_level=0, j5_level=0, j6_level=0)

# Gripper parameters
arm.set_gripper_params(teaching_range_pct=100, max_range=70, friction=1)
```

### Master-Slave
```python
arm.set_master_arm()  # Configure as teaching input
arm.set_slave_arm()   # Configure as motion output
```

### Query Operations
Many parameters require a query first, then read:

```python
# Firmware version
arm.search_firmware_version()
time.sleep(0.1)
version = arm.get_firmware_version()

# Motor limits
arm.search_motor_limits(motor_num=1, content=1)
time.sleep(0.1)
limits = arm.get_motor_limits()

# All motor info
arm.search_all_motor_speeds()
time.sleep(0.1)
speeds = arm.get_all_motor_limits()
```

## Advanced Features

### MIT Control (Expert Mode)
**Warning:** Direct torque control. Misuse can damage hardware!

```python
arm.switch_mode_mit(speed_percent=0)
# motor_num, pos_ref(rad), vel_ref(rad/s), kp, kd, t_ref(N·m)
arm.joint_mit_ctrl(6, -0.5, 0, 10, 0.8, 0)
```

### Direct SDK Access
Access the full SDK when needed:

```python
# Access underlying SDK interface
arm.iface.MotionCtrl_2(ctrl_mode=0x01, move_mode=0x01, ...)
arm.iface.JointConfig(joint_num=1, set_zero=0xAE, ...)

# Use SDK directly
from piper_sdk import C_PiperInterface_V2
piper_sdk = arm.iface  # or create new instance
```

## Units Summary

| Quantity | EasyPiper | SDK Internal |
|----------|-----------|--------------|
| Joint angles | degrees (float) | 0.001° (int) |
| TCP position | mm (float) | 0.001 mm (int) |
| TCP orientation | degrees (float) | 0.001° (int) |
| Gripper width | mm (float) | 0.001 mm (int) |
| Gripper effort | N·m (float) | 0.001 N·m (int) |
| Speed | percent 0-100 | percent 0-100 (int) |

All unit conversions are handled automatically by EasyPiper.

## Examples

### Complete Demo Script
See [easy_piper_demo.py](demo/easy_piper_demo.py) for comprehensive examples including:
- Basic motion control
- Gripper operation
- Feedback reading
- Configuration
- Circular motion
- Teach mode
- Continuous monitoring

Run the demo:
```bash
cd piper_sdk/demo
python3 easy_piper_demo.py
```

### Common Patterns

**Safe initialization:**
```python
arm = EasyPiper()
arm.reset_sequence(speed_percent=30)
arm.go_zero_joints()
```

**Pick and place:**
```python
arm.switch_mode_move_l(speed_percent=40)
arm.gripper_enable(effort=1000, clear_error=True)

# Move to pick position
arm.go_to_tcp_pose(X_mm=200, Y_mm=100, Z_mm=150,
                   RX_deg=0, RY_deg=90, RZ_deg=0)
time.sleep(1)

# Grasp
arm.gripper_move(width_mm=0, effort_nm=2.0)
time.sleep(1)

# Move to place position
arm.go_to_tcp_pose(X_mm=200, Y_mm=-100, Z_mm=150,
                   RX_deg=0, RY_deg=90, RZ_deg=0)
time.sleep(1)

# Release
arm.gripper_move(width_mm=30, effort_nm=1.0)
```

**Monitoring loop:**
```python
while True:
    tcp = arm.get_current_tcp()
    joints = arm.get_joint_state()
    print(f"TCP: X={tcp['X_mm']:.1f} Y={tcp['Y_mm']:.1f} Z={tcp['Z_mm']:.1f}")
    print(f"Joints: J1={joints['j1_deg']:.1f}° Hz={tcp['Hz']:.1f}")
    time.sleep(0.1)
```

**Error recovery:**
```python
try:
    arm.go_to_tcp_pose(...)
except Exception as e:
    print(f"Error: {e}")
    arm.emergency_stop()
    time.sleep(0.05)
    arm.resume()
    time.sleep(0.05)
    arm.enable(wait=True)
    arm.switch_mode_joint(speed_percent=30)
```

## Comparison: EasyPiper vs Raw SDK

### EasyPiper (Pythonic)
```python
arm = EasyPiper()
arm.enable(wait=True)
arm.switch_mode_joint(speed_percent=30)
arm.go_to_joint_angles([0, -30, 45, 0, 60, 0])
tcp = arm.get_current_tcp()
print(f"X={tcp['X_mm']:.2f} mm")
```

### Raw SDK (Low-level)
```python
piper = C_PiperInterface_V2()
piper.ConnectPort()
while not piper.EnablePiper():
    time.sleep(0.01)
piper.ModeCtrl(ctrl_mode=0x01, move_mode=0x01, move_spd_rate_ctrl=30, is_mit_mode=0x00)
piper.JointCtrl(0, -30000, 45000, 0, 60000, 0)
pose = piper.GetArmEndPoseMsgs()
x_mm = pose.end_pose.X_axis / 1000.0
print(f"X={x_mm:.2f} mm")
```

## Design Philosophy

1. **Pythonic**: Use natural Python conventions (snake_case, clear names)
2. **Safe defaults**: Conservative settings that work out of the box
3. **Unit conversion**: Work in human-readable units (degrees, mm, N·m)
4. **Type hints**: Full typing for IDE autocomplete and type checking
5. **SDK transparency**: Every method documents the underlying SDK call
6. **No magic**: Clear, explicit behavior with minimal abstraction
7. **Fail gracefully**: Return values and status checks for robust error handling

## Contributing

EasyPiper is part of the Piper SDK project. Contributions welcome!

When adding new methods:
- Follow the existing naming conventions
- Add comprehensive docstrings with SDK references
- Include type hints
- Update EASY_PIPER_CHEATSHEET.md
- Add examples to easy_piper_demo.py

## License

Same as Piper SDK - see [LICENSE](../LICENSE)

## Support

- **Documentation**: See EASY_PIPER_CHEATSHEET.md and MODE_SWITCH_CHEATSHEET.md
- **Examples**: Check piper_sdk/demo/V2/ for SDK examples
- **Issues**: Report bugs via the main Piper SDK repository

## Version

EasyPiper follows the Piper SDK version. Check version:

```python
arm = EasyPiper()
print(arm.get_sdk_version())
print(arm.get_interface_version())
```
