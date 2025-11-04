#!/usr/bin/env python3
"""
Piper Recorder - Record robot arm trajectories for imitation learning

Records Piper robot arm joint angles and gripper positions in LeRobot format.
Compatible with the LeRobot library for training imitation learning policies.

LeRobot format specification:
- HDF5 file structure with datasets for observations and actions
- Timestamps for each frame
- Episode-based recording
- Metadata about robot configuration

Usage:
    piper-recorder [--can-name CAN_NAME] [--output-dir OUTPUT_DIR]
    # Or: python3 -m easy_piper.piper_recorder [OPTIONS]

Output Directory:
    Recordings are saved to (in priority order):
    1. --output-dir argument (if specified)
    2. PIPER_RECORDINGS_DIR environment variable (if set)
    3. <project_root>/recordings (if running from source)
    4. ./recordings (fallback for installed package)

Interactive commands:
    start <episode_name>  - Start recording a new episode
    stop                  - Stop and save current episode
    status                - Show recording status and robot state
    quit                  - Exit recorder

Examples:
    # Start recorder with default CAN device
    piper-recorder
    
    # Use specific CAN device and output directory
    piper-recorder --can-name can_piper --output-dir ./recordings
"""

import numpy as np
import time
import argparse
import math
import os
import sys
import json
import threading
import traceback
import select
import h5py
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from easy_piper import EasyPiper

# Default recordings directory
# Priority:
# 1. If PIPER_RECORDINGS_DIR env var is set, use it
# 2. If running from source (can find project root), use <project_root>/recordings
# 3. Otherwise (installed package), use ./recordings in current working directory
_current_file = Path(__file__).resolve()
_possible_roots = [
    _current_file.parent.parent.parent,  # From src/easy_piper/ -> project root
]

DEFAULT_RECORDINGS_DIR = './recordings'  # Fallback: current directory

# Check environment variable first
if 'PIPER_RECORDINGS_DIR' in os.environ:
    DEFAULT_RECORDINGS_DIR = os.environ['PIPER_RECORDINGS_DIR']
else:
    # Try to find project root
    for _root in _possible_roots:
        if (_root / 'setup.py').exists() and (_root / 'src' / 'easy_piper').exists():
            # We're running from source - use project root
            DEFAULT_RECORDINGS_DIR = str(_root / 'recordings')
            break
    # If not found, DEFAULT_RECORDINGS_DIR stays as './recordings' (installed package case)


class LeRobotDataRecorder:
    """
    Records robot arm data in LeRobot format for imitation learning.

    LeRobot format structure:
    - Each episode is stored in an HDF5 file
    - Datasets include:
        - observation/state: Joint angles (6 joints) + gripper position
        - action: Next state (for behavior cloning)
        - timestamp: Frame timestamps
        - episode_index: Episode number
    - Metadata includes robot configuration and recording info

    Attributes:
        arm: EasyPiper instance for robot control
        output_dir: Directory to save recordings
        recording: Whether currently recording
        current_episode: Current episode data buffer
        episode_name: Name of current episode
    """

    def __init__(self, arm: EasyPiper, output_dir: str = None):
        """
        Initialize the recorder.

        Args:
            arm: Connected EasyPiper instance
            output_dir: Directory to save recording files (default: project_root/recordings)
        """
        if output_dir is None:
            output_dir = DEFAULT_RECORDINGS_DIR
        
        self.arm = arm
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.recording = False
        self.current_episode: Dict[str, List] = {}
        self.episode_name: Optional[str] = None
        self.episode_start_time: Optional[float] = None

        # Recording configuration
        self.fps = 30  # Target recording frequency
        self.frame_time = 1.0 / self.fps

        # Robot configuration (7 DOF: 6 joints + 1 gripper)
        self.n_joints = 6
        self.n_gripper = 1
        self.state_dim = self.n_joints + self.n_gripper

        print("LeRobot Data Recorder initialized")
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"Recording frequency: {self.fps} Hz")

    def check_data_streaming(self) -> Tuple[bool, str]:
        """
        Check if robot is streaming joint and gripper data.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Check joint data
            joints = self.arm.get_joint_state()
            if joints['Hz'] < 10:
                return False, f"Joint data rate too low: {joints['Hz']:.1f} Hz (expected >10 Hz)"

            # Check gripper data
            gripper = self.arm.get_gripper_state()
            if gripper['Hz'] < 10:
                return False, f"Gripper data rate too low: {gripper['Hz']:.1f} Hz (expected >10 Hz)"

            # Verify data is not all zeros
            joint_values = [joints[f'j{i}_deg'] for i in range(1, 7)]
            if all(abs(v) < 0.01 for v in joint_values):
                return False, "Warning: All joint angles are near zero - robot may not be streaming data"

            return True, f"Data streaming OK - Joints: {joints['Hz']:.1f} Hz, Gripper: {gripper['Hz']:.1f} Hz"

        except Exception as e:
            return False, f"Error checking data stream: {e}"

    def get_current_state(self) -> Optional[np.ndarray]:
        """
        Get current robot state (joint angles + gripper position).

        Returns:
            numpy array of shape (7,): [j1, j2, j3, j4, j5, j6, gripper] in degrees/mm
            Returns None if data cannot be read
        """
        try:
            joints = self.arm.get_joint_state()
            gripper = self.arm.get_gripper_state()

            state = np.array([
                joints['j1_deg'],
                joints['j2_deg'],
                joints['j3_deg'],
                joints['j4_deg'],
                joints['j5_deg'],
                joints['j6_deg'],
                gripper['angle_mm']
            ], dtype=np.float32)

            return state

        except Exception as e:
            print(f"Error reading state: {e}")
            return None

    def start_episode(self, episode_name: str) -> bool:
        """
        Start recording a new episode.

        Args:
            episode_name: Name/identifier for this episode

        Returns:
            True if started successfully, False otherwise
        """
        if self.recording:
            print("❌ Already recording. Stop current episode first.")
            return False

        # Check data streaming
        streaming_ok, message = self.check_data_streaming()
        if not streaming_ok:
            print(f"❌ Cannot start recording: {message}")
            return False

        # Initialize episode data structure
        self.episode_name = episode_name
        self.episode_start_time = time.time()
        self.current_episode = {
            'observation': [],  # Robot states
            'action': [],       # Next states (for BC)
            'timestamp': [],    # Frame timestamps
            'frame_index': []   # Frame indices
        }

        self.recording = True
        print(f"✓ Started recording episode: '{episode_name}'")
        print(f"  Recording at {self.fps} Hz (press 'stop' to finish)")

        return True

    def record_frame(self) -> bool:
        """
        Record one frame of data.

        Returns:
            True if frame recorded successfully, False otherwise
        """
        if not self.recording:
            return False

        state = self.get_current_state()
        if state is None:
            return False

        # Record state as observation
        self.current_episode['observation'].append(state)

        # Record timestamp
        timestamp = time.time() - self.episode_start_time
        self.current_episode['timestamp'].append(timestamp)

        # Record frame index
        frame_idx = len(self.current_episode['observation']) - 1
        self.current_episode['frame_index'].append(frame_idx)

        return True

    def stop_episode(self) -> Optional[Path]:
        """
        Stop recording and save episode to HDF5 file.

        Returns:
            Path to saved file, or None if save failed
        """
        if not self.recording:
            print("❌ Not currently recording")
            return None

        self.recording = False

        # Check if we have data
        n_frames = len(self.current_episode['observation'])
        if n_frames == 0:
            print("❌ No data recorded")
            return None

        print(f"Stopping recording... ({n_frames} frames recorded)")

        # Create actions (next states for behavior cloning)
        # Actions are the next observation (shifted by 1)
        observations = np.array(self.current_episode['observation'])
        actions = np.roll(observations, -1, axis=0)
        # Last action is same as last observation (terminal state)
        actions[-1] = observations[-1]

        # Create filename with timestamp
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.episode_name}_{timestamp_str}.hdf5"
        filepath = self.output_dir / filename

        # Save to HDF5 in LeRobot format
        try:
            with h5py.File(filepath, 'w') as f:
                # Create datasets
                f.create_dataset('observation/state',
                                 data=observations,
                                 compression='gzip',
                                 compression_opts=9)

                f.create_dataset('action',
                                 data=actions,
                                 compression='gzip',
                                 compression_opts=9)

                f.create_dataset('timestamp',
                                 data=np.array(
                                     self.current_episode['timestamp'], dtype=np.float64),
                                 compression='gzip',
                                 compression_opts=9)

                f.create_dataset('episode_index',
                                 data=np.full(n_frames, 0, dtype=np.int64))

                # Add metadata
                f.attrs['episode_name'] = self.episode_name
                f.attrs['n_frames'] = n_frames
                f.attrs['fps'] = self.fps
                f.attrs['state_dim'] = self.state_dim
                f.attrs['n_joints'] = self.n_joints
                f.attrs['n_gripper'] = self.n_gripper
                f.attrs['duration_seconds'] = self.current_episode['timestamp'][-1]
                f.attrs['recording_date'] = datetime.now().isoformat()
                f.attrs['robot_type'] = 'Piper'
                f.attrs['state_description'] = 'joint_angles(deg) + gripper_position(mm)'
                f.attrs['joint_names'] = json.dumps(
                    ['j1', 'j2', 'j3', 'j4', 'j5', 'j6', 'gripper'])

                # LeRobot metadata
                f.attrs['format'] = 'lerobot'
                f.attrs['format_version'] = '1.0'

            # Save episode info to JSON for easy reference
            info_file = self.output_dir / \
                f"{self.episode_name}_{timestamp_str}.json"
            episode_info = {
                'episode_name': self.episode_name,
                'filename': filename,
                'n_frames': n_frames,
                'duration_seconds': float(self.current_episode['timestamp'][-1]),
                'fps': self.fps,
                'state_dim': self.state_dim,
                'recording_date': datetime.now().isoformat(),
                'state_stats': {
                    'mean': observations.mean(axis=0).tolist(),
                    'std': observations.std(axis=0).tolist(),
                    'min': observations.min(axis=0).tolist(),
                    'max': observations.max(axis=0).tolist(),
                }
            }

            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(episode_info, f, indent=2)

            print("✓ Episode saved successfully!")
            print(f"  File: {filepath}")
            print(f"  Frames: {n_frames}")
            print(
                f"  Duration: {self.current_episode['timestamp'][-1]:.2f} seconds")
            print(
                f"  Actual FPS: {n_frames / self.current_episode['timestamp'][-1]:.1f}")

            # Reset episode data
            self.current_episode = {}
            self.episode_name = None
            self.episode_start_time = None

            return filepath

        except Exception as e:
            print(f"❌ Error saving episode: {e}")
            traceback.print_exc()
            return None

    def get_status(self) -> str:
        """
        Get current recording status.

        Returns:
            Status string
        """
        if self.recording:
            n_frames = len(self.current_episode['observation'])
            duration = time.time() - self.episode_start_time
            actual_fps = n_frames / duration if duration > 0 else 0
            return (f"🔴 Recording: '{self.episode_name}' | "
                    f"Frames: {n_frames} | "
                    f"Duration: {duration:.1f}s | "
                    f"FPS: {actual_fps:.1f}")
        else:
            return "⚪ Not recording"

    def debug_stream_simple(self, duration_seconds: Optional[float] = 5.0, print_interval: float = 0.5):
        """Non-interactive debug: clears screen and prints values each interval.

        Args:
            duration_seconds: total duration to run
            print_interval: how often to refresh the screen
        """
        if self.recording:
            print("Cannot run debug while recording.")
            return

        start_time = time.time()
        clear_cmd = 'cls' if os.name == 'nt' else 'clear'

        try:
            while True:
                now = time.time()
                # Check if we should stop (only if duration is set and not infinite)
                if duration_seconds is not None:
                    if (now - start_time) >= duration_seconds:
                        break
                
                try:
                    joints = self.arm.get_joint_state()
                    gripper = self.arm.get_gripper_state()
                except Exception as e:
                    print(f"Error reading data: {e}")
                    break

                # Clear and print snapshot
                os.system(clear_cmd)
                elapsed = now - start_time
                print("Piper Debug (simple)\n" + "="*70)
                print(f"Elapsed: {elapsed:.1f}s  |  Interval: {print_interval:.2f}s")
                print(f"Joints SDK Hz: {joints.get('Hz', 0):.1f}  |  Gripper SDK Hz: {gripper.get('Hz', 0):.1f}")
                print("-"*70)
                print(
                    f"J1: {joints.get('j1_deg', 0.0):7.2f}°  "
                    f"J2: {joints.get('j2_deg', 0.0):7.2f}°  "
                    f"J3: {joints.get('j3_deg', 0.0):7.2f}°"
                )
                print(
                    f"J4: {joints.get('j4_deg', 0.0):7.2f}°  "
                    f"J5: {joints.get('j5_deg', 0.0):7.2f}°  "
                    f"J6: {joints.get('j6_deg', 0.0):7.2f}°"
                )
                print("-"*70)
                print(
                    f"Gripper: {gripper.get('angle_mm', 0.0):7.2f} mm  |  "
                    f"Effort: {gripper.get('effort_nm', 0.0):7.2f} N·m  |  "
                    f"Status: {gripper.get('status', 'unknown')}"
                )
                print("="*70)

                time.sleep(print_interval)

        except KeyboardInterrupt:
            total_time = time.time() - start_time
            print(f"\nStopped simple debug after {total_time:.2f}s")
            print("="*70)

    def run_recording_loop(self):
        """
        Main recording loop when recording is active.
        Maintains target FPS.
        """
        if not self.recording:
            return

        last_time = time.time()

        while self.recording:
            current_time = time.time()
            elapsed = current_time - last_time

            if elapsed >= self.frame_time:
                # Record frame
                success = self.record_frame()
                if not success:
                    print("Warning: Failed to record frame")

                last_time = current_time
            else:
                # Sleep for remaining time
                time.sleep(self.frame_time - elapsed)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Record Piper robot arm trajectories for imitation learning',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Start recorder with default settings
    piper-recorder
    
    # Use specific CAN device
    piper-recorder --can-name can_piper
    
    # Save to specific directory
    piper-recorder --output-dir ./my_recordings
    
Interactive commands:
    start <name>  - Start recording episode with given name
    stop          - Stop and save current episode
    status        - Show recording status
    help          - Show available commands
    quit/exit     - Exit recorder
        """
    )

    parser.add_argument(
        '--can-name',
        type=str,
        default='can0',
        help='CAN device name (default: can0)'
    )

    parser.add_argument(
        '--can-usb-port',
        type=str,
        default=None,
        help='USB hardware address for CAN device (e.g., 3-1.4:1.0)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default=DEFAULT_RECORDINGS_DIR,
        help=f'Output directory for recordings (default: {DEFAULT_RECORDINGS_DIR}). Can also set via PIPER_RECORDINGS_DIR env var'
    )

    parser.add_argument(
        '--fps',
        type=int,
        default=30,
        help='Recording frequency in Hz (default: 30)'
    )

    parser.add_argument(
        '--no-auto-setup',
        action='store_true',
        help='Disable automatic CAN setup'
    )

    # Non-interactive debug mode: optional value means duration in seconds;
    # if provided without value, runs continuously until killed.
    parser.add_argument(
        '--debug',
        nargs='?',
        const=math.inf,
        type=float,
        help='Run debug mode immediately; optional value sets duration in seconds; no value = run until killed'
    )

    return parser.parse_args()


def print_help():
    """Print available commands."""
    print("\nAvailable commands:")
    print("  start <episode_name>  - Start recording a new episode")
    print("  stop                  - Stop and save current episode")
    print("  status                - Show recording status and current robot state")
    print("  help                  - Show this help message")
    print("  quit / exit           - Exit recorder")
    print()


def main():
    """Main interactive recording session."""
    args = parse_args()

    print("="*70)
    print("Piper Recorder - LeRobot Format Data Collection")
    print("="*70)
    print(f"\nCAN Device: {args.can_name}")
    print(f"Output Directory: {args.output_dir}")
    print(f"Recording FPS: {args.fps}")

    # Connect to robot
    print("\nConnecting to Piper arm...")
    try:
        arm = EasyPiper(
            can_name=args.can_name,
            can_usb_port=args.can_usb_port,
            auto_connect=True,
            auto_setup_can=not args.no_auto_setup
        )
        print("✓ Connected to Piper arm")
    except Exception as e:
        print(f"❌ Failed to connect to robot: {e}")
        return 1

    # Create recorder
    recorder = LeRobotDataRecorder(arm, output_dir=args.output_dir)
    recorder.fps = args.fps
    recorder.frame_time = 1.0 / args.fps

    # If non-interactive debug requested, run it and exit
    if args.debug is not None:
        print("\n" + "="*70)
        print("Running non-interactive debug mode...")
        if args.debug == math.inf:
            print("Press Ctrl+C to stop")
        else:
            print(f"Duration: {args.debug:.1f} seconds")
        print("="*70)
        recorder.debug_stream_simple(duration_seconds=args.debug if not math.isinf(args.debug) else None)
        print("\nDisconnecting from robot...")
        try:
            arm.disconnect()
            print("✓ Disconnected")
        except Exception:
            pass
        return 0

    # Check data streaming
    print("\nChecking data streaming...")
    streaming_ok, message = recorder.check_data_streaming()
    if streaming_ok:
        print(f"✓ {message}")
    else:
        print(f"⚠️  {message}")
        print("Warning: Data streaming issues detected. Recording may not work properly.")

    # Show current state
    print("\nCurrent robot state:")
    state = recorder.get_current_state()
    if state is not None:
        print(f"  Joints (deg): [{', '.join(f'{v:6.2f}' for v in state[:6])}]")
        print(f"  Gripper (mm): {state[6]:6.2f}")

    print("\n" + "="*70)
    print("Ready to record! Type 'help' for available commands.")
    print("="*70)

    # Interactive loop
    recording_thread = None

    try:
        while True:
            # Show status if recording
            if recorder.recording:
                print(f"\r{recorder.get_status()}", end='', flush=True)

            # Get user input
            try:
                if recorder.recording:
                    # Non-blocking input simulation (check for stop)
                    if select.select([0], [], [], 0.1)[0]:
                        user_input = input().strip().lower()
                    else:
                        continue
                else:
                    user_input = input("\n> ").strip().lower()
            except EOFError:
                break

            if not user_input:
                continue

            # Parse command
            parts = user_input.split(maxsplit=1)
            command = parts[0]

            if command in ['quit', 'exit', 'q']:
                if recorder.recording:
                    print("\n⚠️  Recording in progress. Stopping...")
                    recorder.stop_episode()
                print("\nExiting recorder. Goodbye!")
                break

            elif command == 'help' or command == 'h':
                print_help()

            elif command == 'start':
                if len(parts) < 2:
                    print("❌ Usage: start <episode_name>")
                    continue

                episode_name = parts[1]
                if recorder.start_episode(episode_name):
                    # Start recording thread
                    recording_thread = threading.Thread(
                        target=recorder.run_recording_loop,
                        daemon=True
                    )
                    recording_thread.start()

            elif command == 'stop':
                if recorder.recording:
                    recorder.stop_episode()
                    if recording_thread:
                        recording_thread.join(timeout=1.0)
                        recording_thread = None
                else:
                    print("⚪ Not currently recording")

            elif command == 'status':
                print(recorder.get_status())
                if not recorder.recording:
                    state = recorder.get_current_state()
                    if state is not None:
                        print(
                            f"  Joints: [{', '.join(f'{v:6.2f}' for v in state[:6])}]")
                        print(f"  Gripper: {state[6]:6.2f} mm")

            # interactive debug command removed in favor of CLI --debug

            else:
                print(
                    f"❌ Unknown command: '{command}'. Type 'help' for available commands.")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        if recorder.recording:
            print("Stopping recording...")
            recorder.stop_episode()

    finally:
        print("\nDisconnecting from robot...")
        try:
            arm.disconnect()
            print("✓ Disconnected")
        except Exception:
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
