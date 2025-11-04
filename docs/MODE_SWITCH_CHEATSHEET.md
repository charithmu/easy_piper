## Piper SDK V2 — Mode and Motion Control Cheatsheet

This page explains, in plain terms, how to switch robot modes and send movement commands with the Piper V2 SDK. It focuses on the three control methods, what inputs they take, and when to use each. Examples mirror the official demos.

---

### TL;DR — the three control methods

- MotionCtrl_1 (CAN 0x150): runtime control flags
  - Purpose: emergency stop/resume, teach/trajectory control
  - Inputs: `emergency_stop`, `track_ctrl`, `grag_teach_ctrl`
  - Use when: you need to E‑stop/resume or manage teach/trajectory execution

- ModeCtrl (CAN 0x151, simplified): set control/motion mode and speed
  - Purpose: quick way to select CAN control, motion type (J/P/L/C), speed%, and MIT flag
  - Inputs: `ctrl_mode`, `move_mode`, `move_spd_rate_ctrl`, `is_mit_mode`
  - Use when: you just need to switch modes for normal operation

- MotionCtrl_2 (CAN 0x151, full): advanced mode control
  - Purpose: same core fields as ModeCtrl plus extras like `residence_time`, `installation_pos`
  - Inputs: `ctrl_mode`, `move_mode`, `move_spd_rate_ctrl`, `is_mit_mode`, plus optional fields (firmware‑dependent)
  - Use when: you need fields beyond ModeCtrl (e.g., offline trajectories, installation position)

### Units (always)
- JointCtrl: angles in 0.001°
- EndPoseCtrl: X/Y/Z in 0.001 mm; RX/RY/RZ in 0.001°
- Gripper: angle in 0.001 mm; effort in 0.001 N·m

---

## Mode & command map (quick)

- Emergency stop → `MotionCtrl_1(0x01, 0x00, 0x00)`
- Resume → `MotionCtrl_1(0x02, 0x00, 0x00)`
- Enable motors → loop `EnablePiper()` until True
- Joint mode (MOVE J) → `ModeCtrl(0x01, 0x01, speed%, 0x00)`
- Point mode (MOVE P) → `ModeCtrl(0x01, 0x00, speed%, 0x00)`
- Linear mode (MOVE L) → `ModeCtrl(0x01, 0x02, speed%, 0x00)`
- Zero joints → `JointCtrl(0,0,0,0,0,0)` (after MOVE J)
- Move TCP pose → `EndPoseCtrl(X,Y,Z,RX,RY,RZ)` (after MOVE P/L)
- MIT on/off → `ModeCtrl(..., is_mit_mode=0xAD)` / `0x00`
- Teach start/stop/exec/pause → `MotionCtrl_1(grag_teach_ctrl=0x01/0x02/0x03/0x04)`
- Master/slave → `MasterSlaveConfig(0xFA master | 0xFC slave, offsets)`
- Gripper enable/disable/clear → `GripperCtrl(angle, effort, code=0x01/0x00/0x02/0x03, set_zero)`

---

### Safety first
- Emergency stop and resume live under MotionCtrl_1 (0x150).
- Always ensure motors are enabled before sending motion commands.

```python
# Emergency stop / resume (0x150)
piper.MotionCtrl_1(emergency_stop=0x01, track_ctrl=0x00, grag_teach_ctrl=0x00)  # E-stop
piper.MotionCtrl_1(emergency_stop=0x02, track_ctrl=0x00, grag_teach_ctrl=0x00)  # Resume

# Ensure motors enabled
import time
while not piper.EnablePiper():
    time.sleep(0.01)
```

---

## Mode control overview (0x151)

There are two helpers that target the same underlying 0x151 channel:
- ModeCtrl: simplified subset — `ctrl_mode`, `move_mode`, `move_spd_rate_ctrl`, `is_mit_mode`
- MotionCtrl_2: full superset — same core fields plus extras (e.g., `residence_time`, `installation_pos`)

### ctrl_mode values
- 0x00: Standby
- 0x01: CAN command control
- 0x03: Ethernet control
- 0x04: Wi‑Fi control
- 0x07: Offline trajectory

Tip: For normal CAN control use `ctrl_mode=0x01`. Use `MotionCtrl_2` only if you need non‑CAN modes or extra fields.

### move_mode values
- 0x00: MOVE P (Position)
- 0x01: MOVE J (Joint)
- 0x02: MOVE L (Linear)
- 0x03: MOVE C (Circular)
- 0x04: MOVE M (MIT) — firmware ≥ V1.5-2

### is_mit_mode values
- 0x00: Position–velocity control (normal)
- 0xAD: MIT/drag‑teach control (firmware‑dependent)
- 0xFF: Invalid

### Speed and extras
- move_spd_rate_ctrl: 0–100 (%)
- residence_time (offline trajectories): 0–254 s, 255 = end of trajectory
- installation_pos (≥ V1.5-2): 0x00 invalid, 0x01 horizontal upright, 0x02 side‑left, 0x03 side‑right

### Common switches (copy‑paste)
```python
# Switch to CAN + MOVE J at 30%
piper.ModeCtrl(ctrl_mode=0x01, move_mode=0x01, move_spd_rate_ctrl=30, is_mit_mode=0x00)

# Switch to CAN + MOVE L at 60%
piper.ModeCtrl(ctrl_mode=0x01, move_mode=0x02, move_spd_rate_ctrl=60, is_mit_mode=0x00)

# Full form (e.g., set offline residence time or installation position)
piper.MotionCtrl_2(ctrl_mode=0x01, move_mode=0x03, move_spd_rate_ctrl=50,
                   is_mit_mode=0x00, residence_time=0, installation_pos=0x01)
```

---

## Emergency, teach, and trajectory controls (0x150)

### SDK signature (aka MotionCtrl_1)
In the SDK this call is exposed as `MotionCtrl_1` (sometimes referred to as Mode_Ctrl_1 in docs).

Signature:

```python
MotionCtrl_1(
  emergency_stop: int,   # 0x00 no-op, 0x01 E-stop, 0x02 resume
  track_ctrl: int,       # trajectory management (see codes below)
  grag_teach_ctrl: int   # teach/record/execute (see codes below)
)
```

Typical usage patterns:

- Emergency stop: `MotionCtrl_1(0x01, 0x00, 0x00)`
- Resume:        `MotionCtrl_1(0x02, 0x00, 0x00)`
- Start teach:   `MotionCtrl_1(0x00, 0x00, 0x01)`
- End teach:     `MotionCtrl_1(0x00, 0x00, 0x02)`
- Execute traj:  `MotionCtrl_1(0x00, 0x00, 0x03)`
- Pause traj:    `MotionCtrl_1(0x00, 0x00, 0x04)`
- Continue traj: `MotionCtrl_1(0x00, 0x00, 0x05)`
- Clear traj:    `MotionCtrl_1(0x00, 0x03, 0x00)` (or 0x04 to clear all)

Note: You can combine fields in one call if needed (e.g., resume and execute), but keeping them separate improves clarity.

### grag_teach_ctrl (teach mode)
- 0x00: Disable
- 0x01: Start teach record (enter teach mode)
- 0x02: End teach record (exit teach mode)
- 0x03: Execute taught trajectory
- 0x04: Pause execution
- 0x05: Continue execution
- 0x06: Terminate execution
- 0x07: Move to trajectory start point

### track_ctrl (trajectory management)
- 0x00: Disable
- 0x01: Pause current plan
- 0x02: Continue current trajectory
- 0x03: Clear current trajectory
- 0x04: Clear all trajectories
- 0x05: Get current planned trajectory
- 0x06: Terminate execution
- 0x07: Trajectory transmission
- 0x08: End of trajectory transmission

Recovery tip: If you “get stuck” in teach/trajectory, send E‑stop → Resume, then re‑enable and switch back to CAN + MOVE J.

---

## Motion commands and units

### JointCtrl (0x155/0x156/0x157)
- Units: each joint angle in 0.001°

```python
# Zero posture (after switching to CAN + MOVE J)
piper.JointCtrl(0, 0, 0, 0, 0, 0)
```

### EndPoseCtrl (0x152/0x153/0x154) — Cartesian XYZ + RX/RY/RZ (Euler)
- X/Y/Z in 0.001 mm
- RX/RY/RZ in 0.001°

```python
mm = lambda v: int(round(v*1000))     # mm → 0.001 mm
mdeg = lambda v: int(round(v*1000))   # deg → 0.001 deg

# Example pose
piper.MotionCtrl_2(ctrl_mode=0x01, move_mode=0x02, move_spd_rate_ctrl=50, is_mit_mode=0x00)
piper.EndPoseCtrl(X=mm(57.0), Y=mm(0.0), Z=mm(260.0),
                  RX=mdeg(0.0), RY=mdeg(85.0), RZ=mdeg(0.0))
```

## MIT (drag‑teach) control — advanced

- Enable via `is_mit_mode=0xAD` in ModeCtrl/MotionCtrl_2 (MOVE M 0x04 if supported).
- Then use `JointMitCtrl(...)` per joint. This is an expert feature; misuse can damage hardware.
- To exit, set `is_mit_mode=0x00` and switch back to MOVE J/L.

See demo: `piper_sdk/demo/V2/V2_piper_ctrl_joint_mit.py`.

---

## Gripper control (0x159)
- gripper_angle: 0.001 mm
- gripper_effort: 0.001 N/m (range 0–5000 → 0–5 N/m)
- gripper_code:
  - 0x00 Disable
  - 0x01 Enable
  - 0x02 Disable + clear error
  - 0x03 Enable + clear error
- set_zero: 0xAE to set current position as zero

### SDK signature
```python
GripperCtrl(
    gripper_angle: int,   # 0.001 mm units
    gripper_effort: int,  # 0.001 N·m units (0–5000 → 0–5 N·m)
    gripper_code: int,    # 0x00 disable, 0x01 enable, 0x02 disable+clear, 0x03 enable+clear
    set_zero: int         # 0x00 normal, 0xAE set current as zero (with enable)
)
```

### Common patterns
- Enable + clear: `GripperCtrl(0, 800, 0x03, 0x00)`
- Enable (no clear): `GripperCtrl(0, 1000, 0x01, 0x00)`
- Disable + clear: `GripperCtrl(0, 0, 0x02, 0x00)`
- Set zero (enabled): `GripperCtrl(0, 0, 0x01, 0xAE)`
- Move to width w_mm: `GripperCtrl(int(w_mm*1000), effort, 0x01, 0x00)`

```python
# Enable gripper and open to 0 mm
piper.GripperCtrl(gripper_angle=0, gripper_effort=1000, gripper_code=0x01, set_zero=0x00)
```

---

## Master–Slave (linkage) configuration (0x470)
- linkage_config:
  - 0x00 Invalid
  - 0xFA Set as teaching input arm (master)
  - 0xFC Set as motion output arm (slave)
- feedback_offset: 0x00 none, 0x10 base 2Ax → 2Bx, 0x20 base 2Ax → 2Cx
- ctrl_offset: 0x00 none, 0x10 base 15x → 16x, 0x20 base 15x → 17x
- linkage_offset: 0x00 none, 0x10 target 15x → 16x, 0x20 target 15x → 17x

```python
# Example: set this arm as slave (motion output)
piper.MasterSlaveConfig(linkage_config=0xFC, feedback_offset=0x00, ctrl_offset=0x00, linkage_offset=0x00)
```

Quick roles:
- Master (0xFA): “teaching input arm” (drives output)
- Slave (0xFC): “motion output arm” (follows input)

---

## Read back current mode
```python
m = piper.GetArmModeCtrl()
print("ctrl_mode:", m.mode_ctrl.ctrl_mode,
      "move_mode:", m.mode_ctrl.move_mode,
      "mit_mode:",  m.mode_ctrl.mit_mode,
      "speed%:",    m.mode_ctrl.move_spd_rate_ctrl,
      "Hz:",        m.Hz)
```

---

## Reliable recovery recipe
1) Emergency stop → resume.
2) Ensure `EnablePiper()` returns True.
3) `ModeCtrl(ctrl_mode=0x01, move_mode=0x01, is_mit_mode=0x00, speed% as needed)`.
4) Verify with `GetArmModeCtrl()` and send `JointCtrl` targets.

```python
import time
piper.MotionCtrl_1(0x01, 0x00, 0x00); time.sleep(0.05)  # E-stop
piper.MotionCtrl_1(0x02, 0x00, 0x00); time.sleep(0.05)  # Resume
while not piper.EnablePiper():
    time.sleep(0.01)
piper.ModeCtrl(ctrl_mode=0x01, move_mode=0x01, move_spd_rate_ctrl=30, is_mit_mode=0x00)
```

---

## Unit conversions you’ll use often
- rad → milli‑degree: `int(rad * 180.0 / 3.141592653589793 * 1000)` ≈ multiply by 57295.7795
- deg → milli‑degree: `int(deg * 1000)`
- mm → 0.001 mm: `int(mm * 1000)`

---

## Gotchas and tips
- The first feedback frame after connect is default/zero; wait a brief moment (`sleep(0.05–0.1s)`) or read until `Hz`/fields look valid.
- After teach or MIT work, reset with E‑stop → resume and explicitly set `is_mit_mode=0x00` when returning to position–velocity control.
- `ModeCtrl` is a convenience wrapper; use `MotionCtrl_2` when you need residence/installation fields or non‑CAN ctrl_mode values.

### About physical teach buttons
- Searched the SDK/demos: no explicit API call or doc for a “physical teach button” on the robot.
- The SDK exposes teach via `MotionCtrl_1(grag_teach_ctrl=...)` and reports teach state through feedback (e.g., `teach_status`, `TEACHING_MODE`).
- If your hardware has a physical button, firmware may toggle the internal teach state; the SDK path to enter/exit teach remains `MotionCtrl_1`.

---

### Quick recipes (copy‑ready)

Switch to joint mode and zero joints
```python
import time
piper.ModeCtrl(ctrl_mode=0x01, move_mode=0x01, move_spd_rate_ctrl=30, is_mit_mode=0x00)
time.sleep(0.05)
piper.JointCtrl(0, 0, 0, 0, 0, 0)
```

Switch to linear mode and move to an absolute TCP pose
```python
mm = lambda v: int(round(v*1000))
mdeg = lambda v: int(round(v*1000))
piper.ModeCtrl(ctrl_mode=0x01, move_mode=0x02, move_spd_rate_ctrl=40, is_mit_mode=0x00)
time.sleep(0.05)
piper.EndPoseCtrl(X=mm(56.127), Y=mm(0.0), Z=mm(213.266),
          RX=mdeg(0.0), RY=mdeg(84.999), RZ=mdeg(0.0))
```

Emergency stop → resume → re‑enable → back to MOVE J
```python
import time
piper.MotionCtrl_1(0x01, 0x00, 0x00); time.sleep(0.05)
piper.MotionCtrl_1(0x02, 0x00, 0x00); time.sleep(0.05)
while not piper.EnablePiper():
  time.sleep(0.01)
piper.ModeCtrl(ctrl_mode=0x01, move_mode=0x01, move_spd_rate_ctrl=30, is_mit_mode=0x00)
```

---

## Reading feedback/state (quick)

### Mode feedback
```python
m = piper.GetArmModeCtrl()
print('ctrl_mode:', m.mode_ctrl.ctrl_mode,
  'move_mode:', m.mode_ctrl.move_mode,
  'mit_mode:',  m.mode_ctrl.mit_mode,
  'speed%:',    m.mode_ctrl.move_spd_rate_ctrl,
  'Hz:',        m.Hz)
```

### TCP (end pose) feedback
```python
pose = piper.GetArmEndPoseMsgs()
print('X(mm):', pose.end_pose.X_axis/1000.0,
  'Y(mm):', pose.end_pose.Y_axis/1000.0,
  'Z(mm):', pose.end_pose.Z_axis/1000.0,
  'RX(deg):', pose.end_pose.RX_axis/1000.0,
  'RY(deg):', pose.end_pose.RY_axis/1000.0,
  'RZ(deg):', pose.end_pose.RZ_axis/1000.0,
  'Hz:', pose.Hz)
```

### Joint state feedback
```python
jm = piper.GetArmJointMsgs()
js = jm.joint_state  # fields: joint_1..joint_6 (angles typically in 0.001°)
print(js.joint_1, js.joint_2, js.joint_3, js.joint_4, js.joint_5, js.joint_6)
```

### Gripper feedback
```python
gs = piper.GetArmGripperCtrl()
gc = gs.gripper_ctrl
print('Hz:', gs.Hz,
  'angle(0.001mm):', getattr(gc, 'grippers_angle', None),
  'effort(0.001N·m):', getattr(gc, 'grippers_effort', None),
  'status_code:', getattr(gc, 'status_code', None),
  'set_zero:', getattr(gc, 'set_zero', None))
```

### Gripper message feedback (detailed)
Use this when you need richer status (e.g., FOC driver flags) in addition to angle/effort.
```python
gm = piper.GetArmGripperMsgs()
gs = gm.gripper_state
print('Hz:', gm.Hz,
  'angle(0.001mm):', getattr(gs, 'grippers_angle', None),
  'effort(0.001N·m):', getattr(gs, 'grippers_effort', None))

# FOC/driver status flags (if present)
fs = getattr(gs, 'foc_status', None)
if fs is not None:
    print('FOC flags ->',
      'voltage_too_low:', getattr(fs, 'voltage_too_low', None),
      'motor_overheating:', getattr(fs, 'motor_overheating', None),
      'driver_overcurrent:', getattr(fs, 'driver_overcurrent', None),
      'driver_overheating:', getattr(fs, 'driver_overheating', None),
      'sensor_status:', getattr(fs, 'sensor_status', None),
      'driver_error_status:', getattr(fs, 'driver_error_status', None),
      'driver_enable_status:', getattr(fs, 'driver_enable_status', None),
      'homing_status:', getattr(fs, 'homing_status', None))
```
