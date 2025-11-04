#!/usr/bin/env python3
"""
EasyPiper Demo - Comprehensive Examples

Demonstrates the main features of the EasyPiper wrapper for Piper robotic arms,
including automatic CAN device setup.

Usage:
    python3 easy_piper_demo.py [--can-name CAN_NAME] [--no-auto-setup]

Examples:
    # Default - auto CAN setup with can0
    python3 easy_piper_demo.py
    
    # Use specific CAN device
    python3 easy_piper_demo.py --can-name can_piper
    
    # Manual CAN setup (configure before running)
    bash scripts/can_activate.sh can0 1000000
    python3 easy_piper_demo.py --no-auto-setup
"""
import time
import argparse
from easy_piper import EasyPiper


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='EasyPiper comprehensive demo')
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
        '--no-auto-setup',
        action='store_true',
        help='Disable automatic CAN setup (requires manual configuration)'
    )
    return parser.parse_args()


def demo_basic_motion(arm: EasyPiper):
    """Demonstrate basic joint and TCP motion."""
    print("\n=== Demo: Basic Motion ===")
    
    # Safe reset
    print("Resetting arm...")
    arm.reset_sequence(speed_percent=30)
    time.sleep(1)
    
    # Joint motion
    print("Moving to zero joints...")
    arm.switch_mode_joint(speed_percent=30)
    arm.go_zero_joints()
    time.sleep(3)
    
    print("Moving to specific joint angles...")
    arm.go_to_joint_angles([0, -30, 45, 0, 60, 0])
    time.sleep(3)
    
    # Linear motion
    print("Switching to linear mode and moving TCP...")
    arm.switch_mode_move_l(speed_percent=40)
    arm.go_to_tcp_pose(
        X_mm=150, Y_mm=0, Z_mm=200,
        RX_deg=0, RY_deg=90, RZ_deg=0
    )
    time.sleep(3)
    
    print("Returning to zero TCP pose...")
    arm.go_zero_tcp(mode='L', speed_percent=40)
    time.sleep(3)


def demo_gripper(arm: EasyPiper):
    """Demonstrate gripper control."""
    print("\n=== Demo: Gripper Control ===")
    
    print("Enabling gripper...")
    arm.gripper_enable(effort=1000, clear_error=True)
    time.sleep(0.5)
    
    print("Opening gripper to 30mm...")
    arm.gripper_move(width_mm=30, effort_nm=1.5)
    time.sleep(2)
    
    print("Closing gripper...")
    arm.gripper_move(width_mm=0, effort_nm=2.0)
    time.sleep(2)
    
    print("Opening again...")
    arm.gripper_move(width_mm=20, effort_nm=1.0)
    time.sleep(2)


def demo_feedback(arm: EasyPiper):
    """Demonstrate reading feedback."""
    print("\n=== Demo: Reading Feedback ===")
    
    # Current TCP pose
    tcp = arm.get_current_tcp()
    print(f"\nCurrent TCP Pose:")
    print(f"  Position: X={tcp['X_mm']:.2f}, Y={tcp['Y_mm']:.2f}, Z={tcp['Z_mm']:.2f} mm")
    print(f"  Orientation: RX={tcp['RX_deg']:.2f}, RY={tcp['RY_deg']:.2f}, RZ={tcp['RZ_deg']:.2f} deg")
    print(f"  Update rate: {tcp['Hz']:.1f} Hz")
    
    # Joint state
    joints = arm.get_joint_state()
    print(f"\nCurrent Joint State:")
    print(f"  J1={joints['j1_deg']:.2f}°, J2={joints['j2_deg']:.2f}°, J3={joints['j3_deg']:.2f}°")
    print(f"  J4={joints['j4_deg']:.2f}°, J5={joints['j5_deg']:.2f}°, J6={joints['j6_deg']:.2f}°")
    print(f"  Update rate: {joints['Hz']:.1f} Hz")
    
    # Gripper state
    gripper = arm.get_gripper_state()
    print(f"\nCurrent Gripper State:")
    print(f"  Width: {gripper['angle_mm']:.2f} mm")
    print(f"  Effort: {gripper['effort_nm']:.2f} N·m")
    print(f"  Update rate: {gripper['Hz']:.1f} Hz")
    
    # Mode
    mode = arm.get_current_mode()
    print(f"\nCurrent Mode:")
    print(f"  Control mode: {mode.mode_ctrl.ctrl_mode}")
    print(f"  Move mode: {mode.mode_ctrl.move_mode}")
    print(f"  MIT mode: {mode.mode_ctrl.mit_mode}")
    print(f"  Speed rate: {mode.mode_ctrl.move_spd_rate_ctrl}%")
    
    # Enable status
    enable_status = arm.get_enable_status()
    print(f"\nEnable Status: {enable_status}")
    
    # System info
    print(f"\nSystem Info:")
    print(f"  Connected: {arm.get_connection_status()}")
    print(f"  CAN FPS: {arm.get_can_fps():.1f}")
    print(f"  CAN port: {arm.get_can_name()}")
    print(f"  OK status: {arm.is_ok()}")


def demo_circular_motion(arm: EasyPiper):
    """Demonstrate circular/arc motion."""
    print("\n=== Demo: Circular Motion ===")
    
    print("Switching to circular motion mode...")
    arm.switch_mode_move_c(speed_percent=30)
    time.sleep(0.5)
    
    print("Moving to start point...")
    arm.go_to_tcp_pose(
        X_mm=135.481, Y_mm=9.349, Z_mm=161.129,
        RX_deg=178.756, RY_deg=6.035, RZ_deg=-178.440
    )
    arm.move_c_update(1)  # Start point
    time.sleep(0.5)
    
    print("Moving to intermediate point...")
    arm.go_to_tcp_pose(
        X_mm=222.158, Y_mm=128.758, Z_mm=142.126,
        RX_deg=175.152, RY_deg=-1.259, RZ_deg=-157.235
    )
    arm.move_c_update(2)  # Intermediate point
    time.sleep(0.5)
    
    print("Moving to end point...")
    arm.go_to_tcp_pose(
        X_mm=359.079, Y_mm=3.221, Z_mm=153.470,
        RX_deg=179.038, RY_deg=1.105, RZ_deg=179.035
    )
    arm.move_c_update(3)  # End point
    time.sleep(3)
    
    print("Circular motion complete!")


def demo_teach_mode(arm: EasyPiper):
    """Demonstrate teach mode recording and playback."""
    print("\n=== Demo: Teach Mode ===")
    
    print("Starting teach mode - you can now manually move the arm...")
    arm.teach_start()
    print("Recording for 10 seconds...")
    time.sleep(10)
    
    print("Ending teach mode...")
    arm.teach_end()
    time.sleep(1)
    
    print("Playing back recorded trajectory...")
    arm.teach_execute()
    time.sleep(5)
    
    print("Clearing trajectory...")
    arm.trajectory_clear()


def demo_configuration(arm: EasyPiper):
    """Demonstrate configuration operations."""
    print("\n=== Demo: Configuration ===")
    
    # Query firmware version
    print("\nQuerying firmware version...")
    arm.search_firmware_version()
    time.sleep(0.1)
    firmware = arm.get_firmware_version()
    print(f"Firmware version: {firmware}")
    
    # Query motor limits
    print("\nQuerying motor limits for joint 1...")
    arm.search_motor_limits(motor_num=1, content=1)
    time.sleep(0.1)
    limits = arm.get_motor_limits()
    print(f"Motor limits: {limits}")
    
    # Query crash protection
    print("\nQuerying crash protection levels...")
    arm.query_crash_protection()
    time.sleep(0.1)
    protection = arm.get_crash_protection()
    print(f"Crash protection: {protection}")
    
    # Set crash protection (all disabled for demo)
    print("\nSetting crash protection levels (all off)...")
    arm.set_crash_protection(0, 0, 0, 0, 0, 0)
    time.sleep(0.5)


def demo_monitoring_loop(arm: EasyPiper, duration_s: float = 5.0):
    """Demonstrate continuous monitoring of arm state."""
    print(f"\n=== Demo: Monitoring Loop ({duration_s}s) ===")
    
    start_time = time.time()
    while (time.time() - start_time) < duration_s:
        tcp = arm.get_current_tcp()
        joints = arm.get_joint_state()
        
        print(f"\rTCP: X={tcp['X_mm']:6.1f} Y={tcp['Y_mm']:6.1f} Z={tcp['Z_mm']:6.1f} | "
              f"J1={joints['j1_deg']:6.1f}° J2={joints['j2_deg']:6.1f}° | "
              f"{tcp['Hz']:.0f}Hz", end='')
        
        time.sleep(0.1)
    
    print()  # New line after monitoring


def main():
    """Run all demos."""
    args = parse_args()
    
    print("=" * 60)
    print("EasyPiper Comprehensive Demo")
    print("=" * 60)
    print(f"\nCAN Device: {args.can_name}")
    if args.can_usb_port:
        print(f"USB Port: {args.can_usb_port}")
    print(f"Auto-setup: {'Disabled' if args.no_auto_setup else 'Enabled'}")
    
    # Initialize arm
    print("\nInitializing arm...")
    try:
        arm = EasyPiper(
            can_name=args.can_name,
            can_usb_port=args.can_usb_port,
            auto_connect=True,
            auto_setup_can=not args.no_auto_setup
        )
    except RuntimeError as e:
        print(f"\n❌ Failed to initialize arm: {e}")
        print("\nTroubleshooting:")
        print("1. Check CAN adapter is connected")
        print("2. Verify robot arm is powered on")
        print("3. Try manual setup:")
        print(f"   bash scripts/can_activate.sh {args.can_name} 1000000")
        return 1
    
    try:
        # Run demos (comment out any you don't want to run)
        demo_feedback(arm)
        demo_configuration(arm)
        demo_basic_motion(arm)
        demo_gripper(arm)
        # demo_circular_motion(arm)  # Requires specific workspace setup
        # demo_teach_mode(arm)  # Interactive - requires manual manipulation
        demo_monitoring_loop(arm, duration_s=5.0)
        
        print("\n" + "=" * 60)
        print("All demos completed successfully!")
        print("=" * 60)
        return 0
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
        return 130
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Safe shutdown
        print("\nShutting down...")
        try:
            arm.emergency_stop()
            time.sleep(0.1)
            arm.disable()
            time.sleep(0.1)
            arm.disconnect()
            print("Disconnected.")
        except Exception as e:
            print(f"Warning during shutdown: {e}")


if __name__ == "__main__":
    import sys
    sys.exit(main())
