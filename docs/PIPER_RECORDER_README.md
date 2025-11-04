# Piper Recorder - Data Collection for Imitation Learning

Record robot arm trajectories in LeRobot format for imitation learning and behavior cloning.

## Overview

`piper_recorder.py` is a tool for collecting demonstration data from a Piper robot arm. It records joint angles and gripper positions at high frequency (default 30 Hz) and saves them in the LeRobot HDF5 format, which is compatible with popular imitation learning frameworks.

## Features

✓ **LeRobot Format**: Industry-standard format for robot learning data  
✓ **High-Frequency Recording**: 30 Hz default (configurable)  
✓ **Episode-Based**: Organize recordings into named episodes  
✓ **Data Validation**: Automatic checks for data streaming quality  
✓ **Interactive Mode**: Easy-to-use command interface  
✓ **Metadata**: Rich metadata for each recording  
✓ **HDF5 Compression**: Efficient storage with gzip compression  

## Installation

### Required Packages

```bash
# Install h5py for HDF5 file handling
pip install h5py numpy

# EasyPiper is already in the same directory
```

### Optional: LeRobot Library

To use recorded data with LeRobot:

```bash
pip install lerobot
```

## Usage

### Basic Usage

```bash
# Start recorder with default settings (can0, 30 Hz)
piper-recorder

# Use specific CAN device
piper-recorder --can-name can_piper

# Change recording frequency
piper-recorder --fps 50

# Save to custom directory
piper-recorder --output-dir ./my_demonstrations
```

### Interactive Commands

Once the recorder starts, you have an interactive prompt:

```
> start demo_task_01
✓ Started recording episode: 'demo_task_01'
Recording at 30 Hz (press 'stop' to finish)

🔴 Recording: 'demo_task_01' | Frames: 245 | Duration: 8.2s | FPS: 29.9

> stop
Stopping recording... (245 frames recorded)
✓ Episode saved successfully!
  File: ./recordings/demo_task_01_20250103_143022.hdf5
  Frames: 245
  Duration: 8.17 seconds
  Actual FPS: 30.0

> start demo_task_02
...

> quit
```

### Available Commands

| Command | Description |
|---------|-------------|
| `start <name>` | Start recording a new episode with given name |
| `stop` | Stop and save the current episode |
| `status` | Show current recording status and robot state |
| `debug [duration]` | Monitor hardware streaming without recording (default: 5s) |
| `help` | Show available commands |
| `quit` or `exit` | Exit the recorder |

## Data Format

### LeRobot HDF5 Structure

Each episode is saved as an HDF5 file with the following structure:

```
episode_name_20250103_143022.hdf5
├── observation/state     # (N, 7) Robot states: [j1..j6, gripper]
├── action               # (N, 7) Next states (for behavior cloning)
├── timestamp            # (N,) Frame timestamps in seconds
├── episode_index        # (N,) Episode indices (all 0 for single episode)
└── attributes           # Metadata
    ├── episode_name
    ├── n_frames
    ├── fps
    ├── state_dim
    ├── duration_seconds
    ├── recording_date
    ├── robot_type: "Piper"
    ├── state_description: "joint_angles(deg) + gripper_position(mm)"
    ├── joint_names: ["j1", "j2", "j3", "j4", "j5", "j6", "gripper"]
    ├── format: "lerobot"
    └── format_version: "1.0"
```

### State Vector

Each state observation is a 7-dimensional vector:

```python
state = [j1, j2, j3, j4, j5, j6, gripper]
#       ├──────────────┤  └────┘
#       Joint angles (deg)  Gripper (mm)
```

### Actions

For behavior cloning, actions are the next state (observation at t+1):

```python
action[t] = observation[t+1]
```

For the last frame, action equals the last observation (terminal state).

## Recording Workflow

### 1. Connect to Robot

The recorder automatically:
- Connects to the specified CAN device
- Checks data streaming quality
- Verifies joint and gripper data rates

```
Connecting to Piper arm...
✓ Connected to Piper arm

Checking data streaming...
✓ Data streaming OK - Joints: 50.0 Hz, Gripper: 50.0 Hz
```

### 2. Debug Hardware Streaming (Optional but Recommended)

Before recording, use the debug command to verify hardware is working:

```
> debug 10
══════════════════════════════════════════════════════════════════════
DEBUG MODE - Hardware Streaming Monitor
══════════════════════════════════════════════════════════════════════
Duration: 10.0s | Update interval: 0.5s
Press Ctrl+C to stop early

Initial check: Data streaming OK - Joints: 50.0 Hz, Gripper: 50.0 Hz

Monitoring... (move the robot to see values change)

──────────────────────────────────────────────────────────────────────
Time: 2.5s | Frames: 125

Joints (SDK: 50.0 Hz, Actual: 50.2 Hz):
  J1:    0.12°  J2:  -15.34°  J3:   45.67°
  J4:    0.00°  J5:   30.21°  J6:    0.00°

Gripper (SDK: 50.0 Hz, Actual: 50.1 Hz):
  Position:   15.23 mm
  Effort:      1.45 N·m
  Status:   enabled
──────────────────────────────────────────────────────────────────────

DEBUG COMPLETE
══════════════════════════════════════════════════════════════════════
Duration: 10.02s
Frames captured: 501
Average rate: 50.0 Hz

✓ Data streaming looks good! Ready to record.
══════════════════════════════════════════════════════════════════════
```

The debug mode:
- Shows real-time joint angles and gripper position
- Displays both SDK-reported and actual data rates
- Warns if data rates are too low
- Verifies hardware is responding to movement
- Can be stopped early with Ctrl+C

**Usage:**
```
> debug          # Monitor for 5 seconds (default)
> debug 10       # Monitor for 10 seconds
> debug 30       # Monitor for 30 seconds
```

### 3. Start Recording

```
> start pick_and_place_demo_01
✓ Started recording episode: 'pick_and_place_demo_01'
```

The recorder will:
- Check that data streaming is working
- Initialize data buffers
- Start recording at target FPS (30 Hz default)

### 3. Perform Demonstration

Manually move the robot through the desired trajectory. The recorder captures:
- Joint angles (6 joints)
- Gripper position
- Timestamps

### 4. Stop and Save

```
> stop
Stopping recording... (342 frames recorded)
✓ Episode saved successfully!
  File: ./recordings/pick_and_place_demo_01_20250103_143545.hdf5
  Frames: 342
  Duration: 11.40 seconds
  Actual FPS: 30.0
```

Two files are created:
- `episode_name_timestamp.hdf5` - Main data file
- `episode_name_timestamp.json` - Episode metadata and statistics

### 5. Repeat

Record multiple demonstrations of the same task with different episode names:
- `pick_and_place_demo_01`
- `pick_and_place_demo_02`
- `pick_and_place_demo_03`
- ...

## Data Verification

### Using Python

```python
import h5py
import numpy as np

# Load recording
with h5py.File('recordings/demo_01_20250103_143022.hdf5', 'r') as f:
    # Read data
    observations = f['observation/state'][:]  # (N, 7)
    actions = f['action'][:]                  # (N, 7)
    timestamps = f['timestamp'][:]            # (N,)
    
    # Read metadata
    print(f"Episode: {f.attrs['episode_name']}")
    print(f"Frames: {f.attrs['n_frames']}")
    print(f"Duration: {f.attrs['duration_seconds']:.2f}s")
    print(f"FPS: {f.attrs['fps']}")
    
    # Analyze trajectory
    print(f"\nTrajectory statistics:")
    print(f"  Observation shape: {observations.shape}")
    print(f"  Mean state: {observations.mean(axis=0)}")
    print(f"  Std state: {observations.std(axis=0)}")
```

### Using JSON Metadata

```python
import json

# Read episode info
with open('recordings/demo_01_20250103_143022.json', 'r') as f:
    info = json.load(f)
    
print(f"Episode: {info['episode_name']}")
print(f"Frames: {info['n_frames']}")
print(f"Duration: {info['duration_seconds']:.2f}s")
print(f"\nState statistics:")
print(f"  Mean: {info['state_stats']['mean']}")
print(f"  Std: {info['state_stats']['std']}")
```

## Command Line Options

```
usage: piper-recorder [-h] [--can-name CAN_NAME] [--can-usb-port CAN_USB_PORT]
                      [--output-dir OUTPUT_DIR] [--fps FPS] [--no-auto-setup]

optional arguments:
  -h, --help            Show help message
  --can-name CAN_NAME   CAN device name (default: can0)
  --can-usb-port USB    USB hardware address for CAN device
  --output-dir DIR      Output directory for recordings (default: ./recordings)
  --fps FPS             Recording frequency in Hz (default: 30)
  --no-auto-setup       Disable automatic CAN setup
```

## Tips for Good Recordings

### 1. Data Quality

- **Check streaming**: Always verify data streaming is working before recording
- **Smooth motions**: Perform smooth, deliberate movements
- **Consistent speed**: Try to maintain consistent speed across demonstrations
- **Target FPS**: Recording should achieve target FPS (shown in status)

### 2. Episode Naming

Use descriptive, systematic names:

```
task_variation_demo_number
├─┘  └────┘    └────┘
│    │         └─ Demo instance (01, 02, 03...)
│    └─ Variation (if any)
└─ Task name
```

Examples:
- `pick_red_cube_demo_01`
- `pick_red_cube_demo_02`
- `pick_blue_cube_demo_01`
- `place_on_shelf_demo_01`

### 3. Multiple Demonstrations

Collect multiple demonstrations (10-50+) for robust learning:
- Variations in approach
- Different starting/ending positions
- Various speeds
- Success and near-success examples

### 4. Recording Duration

- **Short tasks**: 5-15 seconds typical
- **Complex tasks**: 20-30 seconds
- **Very long tasks**: Consider breaking into sub-tasks

## Troubleshooting

### Data Streaming Issues

**Problem**: "Joint data rate too low: 5.2 Hz (expected >10 Hz)"

**Solutions**:
1. Check CAN connection: `ifconfig can0`
2. Verify robot is powered on and connected
3. Check CAN bitrate: `ip -details link show can0` (should be 1000000)
4. Restart CAN device: `sudo ip link set can0 down && sudo ip link set can0 up`

### Recording Drops Frames

**Problem**: Actual FPS is much lower than target FPS

**Solutions**:
1. Reduce target FPS: `--fps 20`
2. Check system load (close other applications)
3. Use faster storage device

### Cannot Save Episode

**Problem**: "Error saving episode: Permission denied"

**Solutions**:
1. Check output directory permissions
2. Verify disk space: `df -h`
3. Try different output directory: `--output-dir ~/recordings`

### All Joints Are Zero

**Problem**: "Warning: All joint angles are near zero"

**Solutions**:
1. Move robot to non-zero position
2. Check if robot is in error state
3. Verify encoder feedback is working

## Future Extensions

The recorder is designed to be extended with additional features:

### Camera Streams (Coming Soon)

```python
# Future feature
recorder = LeRobotDataRecorder(
    arm=arm,
    cameras=['wrist_cam', 'third_person_cam'],
    output_dir='./recordings'
)
```

Camera data will be added as:
```
observation/
├── state          # (N, 7) Joint + gripper
├── wrist_cam      # (N, H, W, 3) RGB images
└── third_person   # (N, H, W, 3) RGB images
```

### Additional Sensors

- Force/torque sensors
- Tactile sensors
- Audio data

## Integration with LeRobot

### Loading Data in LeRobot

```python
from lerobot.common.datasets.lerobot_dataset import LeRobotDataset
import h5py

# Load single episode
with h5py.File('recordings/demo_01.hdf5', 'r') as f:
    observations = f['observation/state'][:]
    actions = f['action'][:]
    
# Use in training
# ... (LeRobot training code)
```

### Converting to LeRobot Dataset

For full LeRobot integration, you may need to merge multiple episodes into a single dataset structure. See LeRobot documentation for dataset creation.

## File Formats

### HDF5 File (.hdf5)

Binary format with compressed data:
- Fast to read/write
- Efficient storage (gzip compression)
- Supports large arrays
- Standard in ML/robotics

### JSON Metadata (.json)

Human-readable summary:
- Episode information
- Recording statistics
- State statistics (mean, std, min, max)
- Easy to parse and share

## References

- **LeRobot**: https://github.com/huggingface/lerobot
- **HDF5**: https://www.hdfgroup.org/solutions/hdf5/
- **Imitation Learning**: https://en.wikipedia.org/wiki/Imitation_learning

## License

Same as Piper SDK (see repository LICENSE file)

## Support

For issues or questions:
1. Check troubleshooting section
2. Verify data streaming with `status` command
3. Check HDF5 file integrity with `h5py`
4. Review episode JSON metadata for statistics
