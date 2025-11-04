#!/usr/bin/env python3
"""
Example: Using the debug mode programmatically

This script shows how to use the recorder's debug_stream() method
directly in your own scripts to verify hardware before recording.

Usage:
    python3 debug_example.py [--duration SECONDS]
"""

import argparse
from easy_piper import EasyPiper
from easy_piper.piper_recorder import LeRobotDataRecorder


def main():
    parser = argparse.ArgumentParser(description='Test hardware streaming')
    parser.add_argument('--can-name', type=str, default='can0',
                       help='CAN device name (default: can0)')
    parser.add_argument('--duration', type=float, default=5.0,
                       help='How long to monitor in seconds (default: 5.0)')
    args = parser.parse_args()
    
    print("="*70)
    print("Piper Hardware Debug Test")
    print("="*70)
    print(f"\nCAN Device: {args.can_name}")
    print(f"Monitor Duration: {args.duration}s")
    
    # Connect to robot
    print("\nConnecting to Piper arm...")
    try:
        arm = EasyPiper(can_name=args.can_name, auto_connect=True)
        print("✓ Connected")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return 1
    
    # Create recorder (not recording, just using for debug)
    recorder = LeRobotDataRecorder(arm, output_dir='./recordings')
    
    # Run debug stream
    print("\n" + "="*70)
    print("Starting hardware debug...")
    print("Move the robot manually to verify it's responding")
    print("="*70)
    
    recorder.debug_stream(duration_seconds=args.duration)
    
    # Disconnect
    print("\nDisconnecting...")
    arm.disconnect()
    print("✓ Done")
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
