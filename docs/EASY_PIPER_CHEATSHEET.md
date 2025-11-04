# EasyPiper Quick Reference

Pythonic wrapper for Piper robotic arm control. All units automatically converted (degrees, mm, N·m).

## Quick Start

```python
from easy_piper import EasyPiper

# Auto-connect with automatic CAN setup
arm = EasyPiper()

# Specify CAN device
arm = EasyPiper(can_name='can_piper')

# Multiple CAN devices - specify USB port
arm = EasyPiper(can_name='can_arm', can_usb_port='3-1.4:1.0')

# Disable auto-setup (manual CAN configuration)
arm = EasyPiper(can_name='can0', auto_setup_can=False)

# Use existing SDK interface
from piper_sdk import C_PiperInterface_V2
iface = C_PiperInterface_V2('can0')
arm = EasyPiper(interface=iface)
```

## CAN Device Setup

### Automatic (Default)
```python
arm = EasyPiper()  # Auto-detects and configures CAN
```

### Manual Scripts
```bash
# Find all CAN devices
bash scripts/find_all_can_port.sh

# Activate single device
bash scripts/can_activate.sh can0 1000000

# Activate with USB port (multiple devices)
bash scripts/can_activate.sh can_arm 1000000 "3-1.4:1.0"
```

See [CAN_SETUP_GUIDE.md](CAN_SETUP_GUIDE.md) for detailed CAN setup instructions.

## Power & Safety

| Method | Description | SDK Reference |
|--------|-------------|---------------|
| `enable(wait=True, timeout_s=3.0)` | Enable motors, optionally wait | `EnablePiper()` |
| `disable()` | Disable motors | `DisablePiper()` |
| `emergency_stop()` | Immediate E-stop | `MotionCtrl_1(0x01, 0x00, 0x00)` |
| `resume()` | Resume after E-stop | `MotionCtrl_1(0x02, 0x00, 0x00)` |
| `reset_sequence(speed_percent=30)` | E-stop → resume → enable → MOVE J | Multiple calls |

## Mode Switching

| Method | Description | SDK Reference |
|--------|-------------|---------------|
| `switch_mode_joint(speed_percent=30, is_mit=False)` | Switch to MOVE J (joint mode) | `ModeCtrl(0x01, 0x01, %, mit)` |
| `switch_mode_move_p(speed_percent=30, is_mit=False)` | Switch to MOVE P (point-to-point) | `ModeCtrl(0x01, 0x00, %, mit)` |
| `switch_mode_move_l(speed_percent=30, is_mit=False)` | Switch to MOVE L (linear) | `ModeCtrl(0x01, 0x02, %, mit)` |
| `switch_mode_move_c(speed_percent=30)` | Switch to MOVE C (circular/arc) | `MotionCtrl_2(0x01, 0x03, %, 0x00)` |
| `switch_mode_mit(speed_percent=0)` | Switch to MIT/drag-teach mode | `MotionCtrl_2(0x01, 0x04, %, 0xAD)` |

## Joint Motion (degrees)

| Method | Description | SDK Reference |
|--------|-------------|---------------|
| `go_zero_joints(ensure_joint_mode=True, speed_percent=30)` | Move all joints to 0° | `JointCtrl(0,0,0,0,0,0)` |
| `go_to_joint_angles([j1,j2,j3,j4,j5,j6])` | Move to absolute joint angles (deg) | `JointCtrl(...)` |

**Example:**
```python
arm.switch_mode_joint(speed_percent=30)
arm.go_zero_joints()
arm.go_to_joint_angles([0, -30, 45, 0, 60, 0])
```

## TCP Motion (mm, degrees)

| Method | Description | SDK Reference |
|--------|-------------|---------------|
| `go_zero_tcp(mode='L', speed_percent=30)` | Move to TCP pose when joints are zero | `EndPoseCtrl(...)` |
| `go_to_tcp_pose(X_mm, Y_mm, Z_mm, RX_deg, RY_deg, RZ_deg, ensure_mode='L', speed_percent=30, wait_s=0)` | Move to absolute TCP pose | `EndPoseCtrl(...)` |

**Example:**
```python
arm.switch_mode_move_l(speed_percent=40)
arm.go_to_tcp_pose(X_mm=100, Y_mm=0, Z_mm=250, 
                   RX_deg=0, RY_deg=90, RZ_deg=0)
```

## Circular Motion

```python
arm.switch_mode_move_c(speed_percent=30)
arm.go_to_tcp_pose(X_mm=135.481, Y_mm=9.349, Z_mm=161.129, 
                   RX_deg=178.756, RY_deg=6.035, RZ_deg=-178.440)
arm.move_c_update(1)  # Start point
time.sleep(0.001)

arm.go_to_tcp_pose(X_mm=222.158, Y_mm=128.758, Z_mm=142.126,
                   RX_deg=175.152, RY_deg=-1.259, RZ_deg=-157.235)
arm.move_c_update(2)  # Intermediate point
time.sleep(0.001)

arm.go_to_tcp_pose(X_mm=359.079, Y_mm=3.221, Z_mm=153.470,
                   RX_deg=179.038, RY_deg=1.105, RZ_deg=179.035)
arm.move_c_update(3)  # End point
```

## Gripper Control

| Method | Description | SDK Reference |
|--------|-------------|---------------|
| `gripper_enable(effort=1000, clear_error=False)` | Enable gripper | `GripperCtrl(..., 0x01/0x03, 0x00)` |
| `gripper_disable(clear_error=False)` | Disable gripper | `GripperCtrl(..., 0x00/0x02, 0x00)` |
| `gripper_set_zero()` | Set current position as zero | `GripperCtrl(..., 0x01, 0xAE)` |
| `gripper_move(width_mm, effort_nm=1.0)` | Move to width (mm) with effort (N·m) | `GripperCtrl(...)` |

**Example:**
```python
arm.gripper_enable(effort=1000, clear_error=True)
arm.gripper_move(width_mm=20, effort_nm=1.5)
arm.gripper_move(width_mm=0, effort_nm=1.0)  # Close
```

## Teach Mode

| Method | Description | SDK Reference |
|--------|-------------|---------------|
| `teach_start()` | Enter drag-teach/record mode | `MotionCtrl_1(..., grag_teach_ctrl=0x01)` |
| `teach_end()` | Exit drag-teach/record mode | `MotionCtrl_1(..., grag_teach_ctrl=0x02)` |
| `teach_execute()` | Execute recorded trajectory | `MotionCtrl_1(..., grag_teach_ctrl=0x03)` |
| `teach_pause()` | Pause trajectory execution | `MotionCtrl_1(..., grag_teach_ctrl=0x04)` |
| `teach_continue()` | Continue paused trajectory | `MotionCtrl_1(..., grag_teach_ctrl=0x05)` |
| `teach_terminate()` | Terminate trajectory execution | `MotionCtrl_1(..., grag_teach_ctrl=0x06)` |
| `trajectory_clear()` | Clear current trajectory | `MotionCtrl_1(..., track_ctrl=0x03)` |
| `trajectory_clear_all()` | Clear all trajectories | `MotionCtrl_1(..., track_ctrl=0x04)` |

**Example:**
```python
arm.teach_start()
# Manually move the arm to record trajectory
time.sleep(10)
arm.teach_end()
arm.teach_execute()
```

## MIT Control (Advanced)

**Warning:** MIT mode allows direct torque control. Misuse can damage hardware!

```python
arm.switch_mode_mit(speed_percent=0)
# motor_num, pos_ref(rad), vel_ref(rad/s), kp, kd, t_ref(N·m)
arm.joint_mit_ctrl(6, -0.5, 0, 10, 0.8, 0)
```

## Master-Slave Configuration

| Method | Description | SDK Reference |
|--------|-------------|---------------|
| `set_master_arm()` | Configure as master (teaching input) | `MasterSlaveConfig(0xFA, 0, 0, 0)` |
| `set_slave_arm()` | Configure as slave (motion output) | `MasterSlaveConfig(0xFC, 0, 0, 0)` |

## Joint Configuration

| Method | Description | SDK Reference |
|--------|-------------|---------------|
| `set_joint_zero(joint_num=7)` | Set current as zero (1-6, 7=all) | `JointConfig(..., set_zero=0xAE, ...)` |
| `clear_joint_error(joint_num=7)` | Clear joint errors (1-6, 7=all) | `JointConfig(..., clear_err=0xAE)` |
| `set_joint_max_acc(motor_num, max_acc=500)` | Set max acceleration | `JointMaxAccConfig(...)` |
| `set_joint_max_speed(motor_num, max_speed=3000)` | Set max speed (0.001°/s) | `MotorMaxSpdSet(...)` |

## End Effector Configuration

| Method | Description | SDK Reference |
|--------|-------------|---------------|
| `set_end_speed_acc(max_linear_vel, max_angular_vel, max_linear_acc, max_angular_acc)` | Set TCP velocity/acceleration limits | `EndSpdAndAccParamSet(...)` |
| `set_end_load(load_type=3)` | Set end effector load type (0-3) | `ArmParamEnquiryAndConfig(...)` |

## Collision Protection

| Method | Description | SDK Reference |
|--------|-------------|---------------|
| `set_crash_protection(j1_level=0, j2_level=0, j3_level=0, j4_level=0, j5_level=0, j6_level=0)` | Set collision protection levels (0=off) | `CrashProtectionConfig(...)` |

## Feedback Reading

### Current State
| Method | Returns | SDK Reference |
|--------|---------|---------------|
| `get_current_tcp()` | Dict: X_mm, Y_mm, Z_mm, RX_deg, RY_deg, RZ_deg, Hz | `GetArmEndPoseMsgs()` |
| `get_joint_state()` | Dict: j1_deg, j2_deg, ..., j6_deg, Hz | `GetArmJointMsgs()` |
| `get_gripper_state()` | Dict: angle_mm, effort_nm, foc_status, Hz | `GetArmGripperMsgs()` |
| `get_current_mode()` | Mode control structure | `GetArmModeCtrl()` |
| `get_arm_status()` | Arm status structure | `GetArmStatus()` |
| `get_enable_status()` | List of enable states | `GetArmEnableStatus()` |

**Example:**
```python
tcp = arm.get_current_tcp()
print(f"TCP: X={tcp['X_mm']:.2f} Y={tcp['Y_mm']:.2f} Z={tcp['Z_mm']:.2f}")

joints = arm.get_joint_state()
print(f"Joints: {joints['j1_deg']:.2f}°, {joints['j2_deg']:.2f}°, ...")

gripper = arm.get_gripper_state()
print(f"Gripper: {gripper['angle_mm']:.2f} mm, {gripper['effort_nm']:.2f} N·m")
```

### Query & Read Pattern
Many parameters require a query first, then read the response:

```python
# Query firmware version
arm.search_firmware_version()
time.sleep(0.1)
version = arm.get_firmware_version()

# Query motor limits
arm.search_motor_limits(motor_num=1, content=1)
time.sleep(0.1)
limits = arm.get_motor_limits()

# Query all motor speeds
arm.search_all_motor_speeds()
time.sleep(0.1)
speeds = arm.get_all_motor_limits()

# Query crash protection
arm.query_crash_protection()
time.sleep(0.1)
protection = arm.get_crash_protection()
```

### Other Feedback Methods
| Method | Description |
|--------|-------------|
| `get_firmware_version()` | Firmware version (after search) |
| `get_motor_limits()` | Motor angle/speed limits (after search) |
| `get_motor_max_acc()` | Motor max acceleration (after search) |
| `get_all_motor_limits()` | All motors angle/speed limits (after search) |
| `get_all_motor_acc_limits()` | All motors max acceleration (after search) |
| `get_end_speed_acc()` | End effector speed/acc params (after query) |
| `get_crash_protection()` | Crash protection levels (after query) |
| `get_gripper_teach_params()` | Gripper teach params (after query) |
| `get_high_speed_info()` | High-speed driver feedback |
| `get_low_speed_info()` | Low-speed driver feedback |
| `get_joint_ctrl()` | Current joint control commands |
| `get_gripper_ctrl()` | Current gripper control commands |
| `get_fk(mode='feedback')` | Forward kinematics (mode: 'feedback' or 'control') |
| `get_can_fps()` | CAN bus frame rate |
| `is_ok()` | Check if arm is OK |
| `get_connection_status()` | Check if connected |

## SDK Parameter Limits

| Method | Description | SDK Reference |
|--------|-------------|---------------|
| `get_sdk_joint_limits(joint_name)` | Get software joint limits (j1-j6) | `GetSDKJointLimitParam()` |
| `set_sdk_joint_limits(joint_name, min_val, max_val)` | Set software joint limits | `SetSDKJointLimitParam()` |
| `get_sdk_gripper_range()` | Get software gripper range | `GetSDKGripperRangeParam()` |
| `set_sdk_gripper_range(min_val, max_val)` | Set software gripper range | `SetSDKGripperRangeParam()` |

## Advanced Features

| Method | Description | SDK Reference |
|--------|-------------|---------------|
| `enable_fk_calculation()` | Enable FK calculation | `EnableFkCal()` |
| `disable_fk_calculation()` | Disable FK calculation | `DisableFkCal()` |
| `is_fk_enabled()` | Check FK calculation status | `isCalFk()` |
| `disconnect(thread_timeout=0.1)` | Disconnect and cleanup | `DisconnectPort()` |
| `get_interface_version()` | Get interface version | `GetCurrentInterfaceVersion()` |
| `get_sdk_version()` | Get SDK version | `GetCurrentSDKVersion()` |
| `get_protocol_version()` | Get protocol version | `GetCurrentProtocolVersion()` |
| `get_can_bus()` | Get CAN bus object | `GetCanBus()` |
| `get_can_name()` | Get CAN port name | `GetCanName()` |

## Direct SDK Access

Access the underlying SDK interface for advanced features not exposed in EasyPiper:

```python
# Direct SDK access
arm.iface.MotionCtrl_2(ctrl_mode=0x01, move_mode=0x01, ...)
arm.iface.JointConfig(joint_num=1, set_zero=0xAE, ...)

# Access SDK constants and enums
from piper_sdk import C_PiperInterface_V2, PiperMessage
```

## Common Patterns

### Safe Initialization
```python
arm = EasyPiper()
arm.reset_sequence(speed_percent=30)
arm.go_zero_joints()
```

### Basic Movement Sequence
```python
# Joint motion
arm.switch_mode_joint(speed_percent=30)
arm.go_zero_joints()
time.sleep(2)
arm.go_to_joint_angles([0, -30, 45, 0, 60, 0])

# Linear motion
arm.switch_mode_move_l(speed_percent=40)
arm.go_to_tcp_pose(X_mm=150, Y_mm=0, Z_mm=200,
                   RX_deg=0, RY_deg=90, RZ_deg=0)
```

### Gripper Operation
```python
arm.gripper_enable(effort=1000, clear_error=True)
arm.gripper_move(width_mm=30, effort_nm=1.5)  # Open
time.sleep(1)
arm.gripper_move(width_mm=0, effort_nm=2.0)   # Close/grasp
```

### Recovery from Error
```python
arm.emergency_stop()
time.sleep(0.05)
arm.resume()
time.sleep(0.05)
arm.enable(wait=True)
arm.switch_mode_joint(speed_percent=30)
```

### Monitor Position
```python
while True:
    tcp = arm.get_current_tcp()
    joints = arm.get_joint_state()
    print(f"TCP: X={tcp['X_mm']:.1f} Y={tcp['Y_mm']:.1f} Z={tcp['Z_mm']:.1f}")
    print(f"J1={joints['j1_deg']:.1f}° Hz={tcp['Hz']:.1f}")
    time.sleep(0.1)
```

## Units Summary

| Quantity | EasyPiper | SDK Internal |
|----------|-----------|--------------|
| Joint angles | degrees | 0.001° (int) |
| TCP position | mm | 0.001 mm (int) |
| TCP orientation | degrees | 0.001° (int) |
| Gripper width | mm | 0.001 mm (int) |
| Gripper effort | N·m | 0.001 N·m (int) |
| Speed percentage | 0-100 | 0-100 (int) |

---

**See also:**
- `MODE_SWITCH_CHEATSHEET.md` - Detailed SDK control mode documentation
- `piper_sdk/interface/piper_interface_v2.py` - Full SDK interface
- `piper_sdk/demo/V2/` - SDK demo scripts
