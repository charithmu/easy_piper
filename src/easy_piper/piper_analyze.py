#!/usr/bin/env python3
"""
Piper Analyze - Analyze and visualize recorded robot trajectories

Load, analyze, and visualize Piper robot arm recordings in LeRobot format.
This tool provides comprehensive analysis of recorded episodes including:
- Statistical summary of joint trajectories
- Data quality validation
- Trajectory visualization (plots)
- Export to numpy arrays for ML workflows

Usage:
    piper-analyze <recording.hdf5> [OPTIONS]
    # Or: python3 -m easy_piper.piper_analyze <recording.hdf5> [OPTIONS]

Examples:
    # Basic analysis
    piper-analyze recordings/demo_01.hdf5
    
    # Generate plot (saved as demo_01_plot.png in same directory)
    piper-analyze recordings/demo_01.hdf5 --plot
    
    # Export to numpy arrays (saved as demo_01_numpy/ in same directory)
    piper-analyze recordings/demo_01.hdf5 --export-numpy
    
    # Custom output locations
    piper-analyze recordings/demo_01.hdf5 --save-plot /tmp/myplot.png --export-numpy /tmp/mydata
"""

import h5py
import numpy as np
import argparse
import json
from pathlib import Path


def load_episode(filepath: str):
    """
    Load a recorded episode from HDF5 file.
    
    Args:
        filepath: Path to HDF5 file
        
    Returns:
        Dictionary with observations, actions, timestamps, metadata, and camera info
    """
    with h5py.File(filepath, 'r') as f:
        data = {
            'observations': f['observation/state'][:],
            'actions': f['action'][:],
            'timestamps': f['timestamp'][:],
            'metadata': {key: f.attrs[key] for key in f.attrs.keys()}
        }
        
        # Load camera image paths if available
        data['cameras'] = {}
        if 'observation/images/table_cam' in f:
            data['cameras']['table_cam'] = f['observation/images/table_cam'][:].astype(str)
        if 'observation/images/wrist_cam' in f:
            data['cameras']['wrist_cam'] = f['observation/images/wrist_cam'][:].astype(str)
    
    return data


def print_episode_info(data: dict):
    """Print episode information and statistics."""
    meta = data['metadata']
    obs = data['observations']
    
    print("="*70)
    print(f"Episode: {meta['episode_name']}")
    print("="*70)
    
    print(f"\nRecording Info:")
    print(f"  Date: {meta['recording_date']}")
    print(f"  Duration: {meta['duration_seconds']:.2f} seconds")
    print(f"  Frames: {meta['n_frames']}")
    print(f"  FPS: {meta['fps']}")
    print(f"  Robot: {meta['robot_type']}")
    
    # Display camera info if available
    if meta.get('cameras_enabled', False):
        print(f"  Cameras: Enabled")
        if 'camera_names' in meta:
            camera_names = json.loads(meta['camera_names'])
            print(f"    - {', '.join(camera_names)}")
        if len(data.get('cameras', {})) > 0:
            print(f"    - Images recorded: {len(list(data['cameras'].values())[0])} frames")
    
    print(f"\nData Shape:")
    print(f"  Observations: {obs.shape}")
    print(f"  State dimension: {meta['state_dim']}")
    
    # Parse joint names from JSON string
    joint_names = json.loads(meta['joint_names'])
    
    print(f"\nJoint Statistics (degrees/mm):")
    print(f"  {'Joint':<10} {'Mean':>8} {'Std':>8} {'Min':>8} {'Max':>8}")
    print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    
    for i, name in enumerate(joint_names):
        mean = obs[:, i].mean()
        std = obs[:, i].std()
        min_val = obs[:, i].min()
        max_val = obs[:, i].max()
        print(f"  {name:<10} {mean:8.2f} {std:8.2f} {min_val:8.2f} {max_val:8.2f}")
    
    print(f"\nTrajectory Analysis:")
    
    # Compute velocities (finite differences)
    dt = np.diff(data['timestamps'])
    velocities = np.diff(obs, axis=0) / dt[:, np.newaxis]
    
    print(f"  Average timestep: {dt.mean()*1000:.2f} ms")
    print(f"  Actual FPS: {1.0/dt.mean():.1f}")
    
    print(f"\n  Joint Velocities (deg/s or mm/s):")
    print(f"  {'Joint':<10} {'Mean':>10} {'Max':>10}")
    print(f"  {'-'*10} {'-'*10} {'-'*10}")
    
    for i, name in enumerate(joint_names):
        mean_vel = np.abs(velocities[:, i]).mean()
        max_vel = np.abs(velocities[:, i]).max()
        print(f"  {name:<10} {mean_vel:10.2f} {max_vel:10.2f}")


def plot_trajectories(data: dict, filepath: Path, output_file: str = None):
    """
    Plot joint trajectories over time.
    
    Args:
        data: Episode data dictionary
        filepath: Original HDF5 file path (for auto-naming)
        output_file: Optional path to save plot image
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nMatplotlib not installed. Skipping plot.")
        print("Install with: pip install matplotlib")
        return
    
    obs = data['observations']
    timestamps = data['timestamps']
    meta = data['metadata']
    joint_names = json.loads(meta['joint_names'])
    
    # Create figure with subplots
    fig, axes = plt.subplots(4, 2, figsize=(12, 10))
    fig.suptitle(f"Episode: {meta['episode_name']}", fontsize=14, fontweight='bold')
    
    axes = axes.flatten()
    
    for i, name in enumerate(joint_names):
        ax = axes[i]
        ax.plot(timestamps, obs[:, i], linewidth=1.5)
        ax.set_xlabel('Time (s)')
        
        if i < 6:
            ax.set_ylabel('Angle (deg)')
            ax.set_title(f'Joint {name}')
        else:
            ax.set_ylabel('Position (mm)')
            ax.set_title('Gripper')
        
        ax.grid(True, alpha=0.3)
    
    # Hide the last unused subplot
    axes[-1].set_visible(False)
    
    plt.tight_layout()
    
    if output_file:
        save_path = Path(output_file)
    else:
        # Auto-generate filename in same directory as input file
        save_path = filepath.parent / f"{filepath.stem}_plot.png"
    
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ Plot saved to: {save_path}")
    plt.close()


def check_data_quality(data: dict):
    """Check data quality and report potential issues."""
    obs = data['observations']
    timestamps = data['timestamps']
    
    print("\n" + "="*70)
    print("Data Quality Checks")
    print("="*70)
    
    # Check for missing data (NaN or inf)
    has_nan = np.any(np.isnan(obs))
    has_inf = np.any(np.isinf(obs))
    
    if has_nan or has_inf:
        print("❌ Data contains NaN or Inf values!")
        print(f"   NaN: {np.sum(np.isnan(obs))} values")
        print(f"   Inf: {np.sum(np.isinf(obs))} values")
    else:
        print("✓ No NaN or Inf values")
    
    # Check timestamp consistency
    dt = np.diff(timestamps)
    dt_std = dt.std()
    dt_mean = dt.mean()
    
    if dt_std / dt_mean > 0.1:
        print(f"⚠️  Irregular timestamps (CV: {dt_std/dt_mean:.2%})")
        print(f"   Mean dt: {dt_mean*1000:.2f} ms")
        print(f"   Std dt: {dt_std*1000:.2f} ms")
    else:
        print(f"✓ Consistent timestamps (CV: {dt_std/dt_mean:.2%})")
    
    # Check for stationary periods
    velocities = np.diff(obs, axis=0) / dt[:, np.newaxis]
    max_velocities = np.abs(velocities).max(axis=0)
    
    stationary_joints = max_velocities < 0.1
    if np.any(stationary_joints):
        joint_names = json.loads(data['metadata']['joint_names'])
        stationary_names = [joint_names[i] for i, s in enumerate(stationary_joints) if s]
        print(f"⚠️  Mostly stationary joints: {', '.join(stationary_names)}")
    else:
        print("✓ All joints show movement")
    
    # Check data range
    obs_range = obs.max(axis=0) - obs.min(axis=0)
    small_range = obs_range < 1.0
    
    if np.any(small_range):
        joint_names = json.loads(data['metadata']['joint_names'])
        small_range_names = [joint_names[i] for i, s in enumerate(small_range) if s]
        print(f"⚠️  Small range of motion: {', '.join(small_range_names)}")
        print(f"   (Range < 1.0 deg/mm)")
    else:
        print("✓ All joints show good range of motion")


def export_to_numpy(data: dict, filepath: Path, output_dir: str = None):
    """
    Export data to numpy arrays for easy loading.
    
    Args:
        data: Episode data dictionary
        filepath: Original HDF5 file path (for auto-naming)
        output_dir: Optional directory to save numpy files (default: same as input with _numpy suffix)
    """
    if output_dir:
        output_path = Path(output_dir)
    else:
        # Auto-generate directory name in same location as input file
        output_path = filepath.parent / f"{filepath.stem}_numpy"
    
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save arrays
    np.save(output_path / 'observations.npy', data['observations'])
    np.save(output_path / 'actions.npy', data['actions'])
    np.save(output_path / 'timestamps.npy', data['timestamps'])
    
    # Save metadata as JSON
    meta_file = output_path / 'metadata.json'
    with open(meta_file, 'w', encoding='utf-8') as f:
        # Convert numpy types to Python types for JSON serialization
        metadata = {}
        for key, value in data['metadata'].items():
            if isinstance(value, (np.integer, np.floating)):
                metadata[key] = value.item()
            elif isinstance(value, np.ndarray):
                metadata[key] = value.tolist()
            elif isinstance(value, bytes):
                metadata[key] = value.decode('utf-8')
            else:
                metadata[key] = value
        
        json.dump(metadata, f, indent=2)
    
    print(f"\n✓ Exported to numpy arrays in: {output_path.absolute()}")
    print("  - observations.npy")
    print("  - actions.npy")
    print("  - timestamps.npy")
    print("  - metadata.json")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze and visualize Piper robot arm recordings',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic analysis with statistics and quality checks
    piper-analyze recordings/demo.hdf5
    
    # Generate trajectory plot (auto-saved as demo_plot.png in same directory)
    piper-analyze recordings/demo.hdf5 --plot
    
    # Export to numpy arrays (auto-saved as demo_numpy/ in same directory)
    piper-analyze recordings/demo.hdf5 --export-numpy
    
    # Custom output locations
    piper-analyze recordings/demo.hdf5 --save-plot /tmp/plot.png
    piper-analyze recordings/demo.hdf5 --export-numpy /tmp/numpy_data
    
    # Skip quality checks for faster analysis
    piper-analyze recordings/demo.hdf5 --plot --no-quality-check

Output files are saved in the same directory as the input file by default:
    input.hdf5 -> input_plot.png (plot)
    input.hdf5 -> input_numpy/ (numpy export directory)
        """
    )
    
    parser.add_argument(
        'filepath',
        type=str,
        help='Path to HDF5 recording file'
    )
    
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Generate and save trajectory plots (saved as <filename>_plot.png in same directory)'
    )
    
    parser.add_argument(
        '--save-plot',
        type=str,
        metavar='PATH',
        help='Save plot to custom file path (overrides --plot auto-naming)'
    )
    
    parser.add_argument(
        '--export-numpy',
        nargs='?',
        const='',
        metavar='DIR',
        help='Export data to numpy arrays (default: <filename>_numpy/ in same directory, or specify custom directory)'
    )
    
    parser.add_argument(
        '--no-quality-check',
        action='store_true',
        help='Skip data quality validation checks'
    )
    
    args = parser.parse_args()
    
    # Check file exists
    filepath = Path(args.filepath)
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return 1
    
    # Load data
    print(f"Loading: {filepath}")
    try:
        data = load_episode(str(filepath))
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return 1
    
    # Print info
    print_episode_info(data)
    
    # Quality check
    if not args.no_quality_check:
        check_data_quality(data)
    
    # Plot if requested
    if args.plot or args.save_plot:
        plot_trajectories(data, filepath, args.save_plot)
    
    # Export if requested
    if args.export_numpy is not None:
        export_dir = args.export_numpy if args.export_numpy else None
        export_to_numpy(data, filepath, export_dir)
    
    print("\n" + "="*70)
    print("Analysis complete!")
    print("="*70)
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
