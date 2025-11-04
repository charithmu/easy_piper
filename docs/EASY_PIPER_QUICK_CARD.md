# EasyPiper Quick Reference Card

**Ultra-condensed reference for experienced users**

## Initialization
```python
from piper_sdk.easy_piper import EasyPiper
arm = EasyPiper()  # auto-connects
```

## Power: `enable()` `disable()` `emergency_stop()` `resume()` `reset_sequence()`

## Modes: `switch_mode_joint()` `switch_mode_move_p()` `switch_mode_move_l()` `switch_mode_move_c()` `switch_mode_mit()`

## Motion (degrees/mm)
- **Joint**: `go_zero_joints()` `go_to_joint_angles([j1..j6])`
- **TCP**: `go_zero_tcp()` `go_to_tcp_pose(X_mm, Y_mm, Z_mm, RX_deg, RY_deg, RZ_deg)`
- **Arc**: `move_c_update(0|1|2|3)` after `switch_mode_move_c()`

## Gripper (mm, N·m)
`gripper_enable()` `gripper_disable()` `gripper_set_zero()` `gripper_move(width_mm, effort_nm)`

## Teach
`teach_start()` `teach_end()` `teach_execute()` `teach_pause()` `teach_continue()` `teach_terminate()`
`trajectory_clear()` `trajectory_clear_all()`

## Config
- **Joints**: `set_joint_zero(n)` `clear_joint_error(n)` `set_joint_max_acc()` `set_joint_max_speed()`
- **TCP**: `set_end_load()` `set_end_speed_acc()`
- **Safety**: `set_crash_protection(j1..j6_level)`
- **Gripper**: `set_gripper_params()`
- **Master/Slave**: `set_master_arm()` `set_slave_arm()`

## Feedback (returns dict with units)
```python
tcp = arm.get_current_tcp()        # X_mm, Y_mm, Z_mm, RX_deg, RY_deg, RZ_deg, Hz
joints = arm.get_joint_state()     # j1_deg, j2_deg, ..., j6_deg, Hz
gripper = arm.get_gripper_state()  # angle_mm, effort_nm, foc_status, Hz
```

## Queries (call search/query, wait, then get)
```python
arm.search_firmware_version(); time.sleep(0.1); v = arm.get_firmware_version()
arm.search_motor_limits(1, 1); time.sleep(0.1); lim = arm.get_motor_limits()
arm.query_crash_protection(); time.sleep(0.1); cp = arm.get_crash_protection()
```

## Status
`get_arm_status()` `get_enable_status()` `is_ok()` `get_connection_status()` `get_can_fps()`

## Advanced
`joint_mit_ctrl(motor, pos, vel, kp, kd, torque)` - **EXPERT ONLY**
`enable_fk_calculation()` `disable_fk_calculation()` `get_fk(mode)`
`disconnect()` `get_sdk_version()` `get_interface_version()`

## Direct SDK Access
`arm.iface.<SDK_method>()` for anything not exposed

---
**Units**: degrees, mm, N·m (SDK uses 0.001× internally, auto-converted)
**Docs**: See EASY_PIPER_CHEATSHEET.md and EASY_PIPER_README.md
