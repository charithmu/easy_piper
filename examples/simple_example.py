#!/usr/bin/env python3
"""
EasyPiper Simple Example with CAN Auto-Setup

This example demonstrates the simplest way to get started with EasyPiper,
including automatic CAN device detection and configuration.
"""
import time
from easy_piper import EasyPiper


def main():
    print("="*60)
    print("EasyPiper Simple Example")
    print("="*60)
    
    # Initialize with automatic CAN setup
    # This will:
    # 1. Check if 'can0' exists and is configured
    # 2. If not, search for available CAN devices
    # 3. Automatically configure the device
    # 4. Connect to the robot arm
    print("\nInitializing arm with automatic CAN setup...")
    try:
        arm = EasyPiper()  # That's it! CAN setup is automatic
    except RuntimeError as e:
        print(f"\n❌ Failed to initialize: {e}")
        return
    
    print("✓ Successfully connected to robot arm!")
    
    # Basic operations
    print("\n--- Power Management ---")
    print("Enabling motors...")
    if arm.enable(wait=True, timeout_s=3.0):
        print("✓ Motors enabled")
    else:
        print("❌ Failed to enable motors")
        return
    
    print("\n--- Joint Motion ---")
    print("Switching to joint mode...")
    arm.switch_mode_joint(speed_percent=30)
    time.sleep(0.1)
    
    print("Moving to zero position...")
    arm.go_zero_joints()
    time.sleep(3)
    
    print("Moving to specific angles...")
    arm.go_to_joint_angles([0, -20, 30, 0, 50, 0])
    time.sleep(3)
    
    print("\n--- TCP Motion ---")
    print("Switching to linear mode...")
    arm.switch_mode_move_l(speed_percent=40)
    time.sleep(0.1)
    
    print("Moving TCP...")
    arm.go_to_tcp_pose(
        X_mm=120, Y_mm=0, Z_mm=220,
        RX_deg=0, RY_deg=90, RZ_deg=0
    )
    time.sleep(3)
    
    print("\n--- Gripper Control ---")
    print("Enabling gripper...")
    arm.gripper_enable(effort=1000, clear_error=True)
    time.sleep(0.5)
    
    print("Opening gripper...")
    arm.gripper_move(width_mm=25, effort_nm=1.0)
    time.sleep(2)
    
    print("Closing gripper...")
    arm.gripper_move(width_mm=0, effort_nm=1.5)
    time.sleep(2)
    
    print("\n--- Reading Feedback ---")
    tcp = arm.get_current_tcp()
    print(f"TCP Position: X={tcp['X_mm']:.1f}, Y={tcp['Y_mm']:.1f}, Z={tcp['Z_mm']:.1f} mm")
    print(f"TCP Orientation: RX={tcp['RX_deg']:.1f}, RY={tcp['RY_deg']:.1f}, RZ={tcp['RZ_deg']:.1f} deg")
    
    joints = arm.get_joint_state()
    print(f"Joint Angles: J1={joints['j1_deg']:.1f}°, J2={joints['j2_deg']:.1f}°, J3={joints['j3_deg']:.1f}°")
    print(f"              J4={joints['j4_deg']:.1f}°, J5={joints['j5_deg']:.1f}°, J6={joints['j6_deg']:.1f}°")
    
    gripper = arm.get_gripper_state()
    print(f"Gripper: Width={gripper['angle_mm']:.1f} mm, Effort={gripper['effort_nm']:.2f} N·m")
    
    print(f"\nUpdate rates: TCP={tcp['Hz']:.1f} Hz, Joints={joints['Hz']:.1f} Hz")
    print(f"CAN bus FPS: {arm.get_can_fps():.1f}")
    print(f"System OK: {arm.is_ok()}")
    
    print("\n--- Shutdown ---")
    print("Emergency stop...")
    arm.emergency_stop()
    time.sleep(0.1)
    
    print("Disabling motors...")
    arm.disable()
    time.sleep(0.1)
    
    print("Disconnecting...")
    arm.disconnect()
    
    print("\n" + "="*60)
    print("Example completed successfully!")
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
