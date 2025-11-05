"""
EasyPiper — Pythonic wrapper around C_PiperInterface_V2

A simplified, user-friendly interface for controlling Piper robotic arms.
Handles unit conversions, mode switching, motion control, gripper operations,
configuration, and feedback reading with clear, intuitive method names.

Features:
- Automatic CAN device setup and validation
- Unit conversions (degrees, mm, N·m)
- Clear, Pythonic API
- Comprehensive feedback reading

Units (SDK uses):
- Joint angles: 0.001° (converted from/to degrees)
- TCP position: X/Y/Z in 0.001 mm, RX/RY/RZ in 0.001° (converted from/to mm/deg)
- Gripper: angle in 0.001 mm, effort in 0.001 N·m (converted from/to mm/N·m)

For detailed SDK mappings, see docs/MODE_SWITCH_CHEATSHEET.md
"""
from __future__ import annotations

import time
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence, Tuple, Dict, Any, Literal

# SDK import (provided by this repo)
from piper_sdk import C_PiperInterface_V2  # noqa: F401


def _mm_to_001mm(v_mm: float) -> int:
    """Convert millimeters to 0.001 mm units."""
    return int(round(v_mm * 1000))


def _deg_to_001deg(v_deg: float) -> int:
    """Convert degrees to 0.001 degree units."""
    return int(round(v_deg * 1000))


def _001mm_to_mm(v: int) -> float:
    """Convert 0.001 mm units to millimeters."""
    return v / 1000.0


def _001deg_to_deg(v: int) -> float:
    """Convert 0.001 degree units to degrees."""
    return v / 1000.0


# ----------------------------
# CAN Device Setup Helpers
# ----------------------------
def _check_can_device_exists(can_name: str) -> bool:
    """Check if a CAN device exists in the system.
    
    Args:
        can_name: Name of the CAN device (e.g., 'can0')
    
    Returns:
        True if the device exists, False otherwise
    """
    try:
        result = subprocess.run(
            ['ip', 'link', 'show', can_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def _check_can_device_up(can_name: str) -> bool:
    """Check if a CAN device is UP and configured.
    
    Args:
        can_name: Name of the CAN device (e.g., 'can0')
    
    Returns:
        True if the device is UP, False otherwise
    """
    try:
        result = subprocess.run(
            ['ip', 'link', 'show', can_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return 'UP' in result.stdout and 'state UP' in result.stdout
        return False
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        return False


def _find_can_devices() -> Dict[str, str]:
    """Find all CAN devices using scripts/find_all_can_port.sh script.
    
    Returns:
        Dict mapping CAN device names to USB port addresses
    """
    # Script is in root/scripts/, we are in root/src/easy_piper/
    script_dir = Path(__file__).parent.parent.parent
    script_path = script_dir / "scripts" / "find_all_can_port.sh"
    
    if not script_path.exists():
        print(f"Warning: scripts/find_all_can_port.sh not found at {script_path}")
        return {}
    
    try:
        result = subprocess.run(
            ['bash', str(script_path)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Parse output: "Interface can0 is connected to USB port 3-1.4:1.0"
        devices = {}
        for line in result.stdout.split('\n'):
            if 'Interface' in line and 'is connected to USB port' in line:
                parts = line.split()
                if len(parts) >= 7:
                    can_name = parts[1]
                    usb_port = parts[7]
                    devices[can_name] = usb_port
        
        return devices
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"Warning: Failed to find CAN devices: {e}")
        return {}


def _activate_can_device(can_name: str = "can0", bitrate: int = 1000000, 
                         usb_address: Optional[str] = None, verbose: bool = True) -> bool:
    """Activate a CAN device using scripts/can_activate.sh script.
    
    Args:
        can_name: Desired name for the CAN device (e.g., 'can0')
        bitrate: CAN bus bitrate (must be 1000000 for Piper)
        usb_address: Optional USB hardware address (e.g., '3-1.4:1.0')
        verbose: If True, print script output
    
    Returns:
        True if activation succeeded, False otherwise
    """
    # Script is in root/scripts/, we are in root/src/easy_piper/
    script_dir = Path(__file__).parent.parent.parent
    script_path = script_dir / "scripts" / "can_activate.sh"
    
    if not script_path.exists():
        print(f"Error: scripts/can_activate.sh not found at {script_path}")
        return False
    
    try:
        cmd = ['bash', str(script_path), can_name, str(bitrate)]
        if usb_address:
            cmd.append(usb_address)
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if verbose:
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
        
        # Check if activation was successful
        if result.returncode == 0:
            # Verify the device is now up
            time.sleep(0.5)  # Give system time to configure
            return _check_can_device_up(can_name)
        else:
            return False
            
    except subprocess.TimeoutExpired:
        print(f"Error: CAN activation script timed out")
        return False
    except Exception as e:
        print(f"Error: Failed to activate CAN device: {e}")
        return False


def _setup_can_device_interactive(can_name: str = "can0") -> bool:
    """Interactively set up CAN device with user guidance.
    
    Args:
        can_name: Desired name for the CAN device
    
    Returns:
        True if setup succeeded, False otherwise
    """
    print("\n" + "="*60)
    print("CAN Device Setup Required")
    print("="*60)
    
    # Find available CAN devices
    print("\nSearching for CAN devices...")
    devices = _find_can_devices()
    
    if not devices:
        print("\n⚠️  No CAN devices found!")
        print("\nPossible solutions:")
        print("1. Check that the USB-CAN adapter is plugged in")
        print("2. Install required packages:")
        print("   sudo apt update && sudo apt install can-utils ethtool")
        print("3. Check USB connection and try a different port")
        print("4. Verify the CAN adapter is recognized by the system")
        return False
    
    print(f"\nFound {len(devices)} CAN device(s):")
    for can_dev, usb_port in devices.items():
        status = "UP" if _check_can_device_up(can_dev) else "DOWN"
        print(f"  - {can_dev}: USB port {usb_port} [{status}]")
    
    # Check if desired device exists
    if can_name in devices:
        print(f"\n✓ Device '{can_name}' found at USB port {devices[can_name]}")
        if _check_can_device_up(can_name):
            print(f"✓ Device '{can_name}' is already UP and configured")
            return True
        else:
            print(f"⚠️  Device '{can_name}' exists but is not configured")
            print(f"\nActivating '{can_name}'...")
            return _activate_can_device(can_name, verbose=True)
    
    # Device with desired name doesn't exist
    if len(devices) == 1:
        # Only one device found - activate it with desired name
        existing_name = list(devices.keys())[0]
        usb_port = devices[existing_name]
        print(f"\n→ Configuring '{existing_name}' as '{can_name}'...")
        return _activate_can_device(can_name, usb_address=usb_port, verbose=True)
    else:
        # Multiple devices - need user to specify
        print(f"\n⚠️  Multiple CAN devices found, but '{can_name}' not configured")
        print("\nTo activate a specific device, provide its USB port:")
        print(f"  EasyPiper(can_name='{can_name}', can_usb_port='<USB_PORT>')")
        print("\nOr activate manually:")
        for can_dev, usb_port in devices.items():
            print(f"  bash scripts/can_activate.sh {can_name} 1000000 {usb_port}")
        return False


class EasyPiper:
    """User-friendly wrapper for C_PiperInterface_V2.

    Automatically handles CAN device setup and provides a Pythonic interface
    for controlling Piper robotic arms.

    Parameters
    ----------
    can_name : str
        CAN device name (e.g., 'can0', 'can_piper'). Default: 'can0'
    can_usb_port : Optional[str]
        USB hardware address for the CAN device (e.g., '3-1.4:1.0').
        Only needed when multiple CAN devices are present.
    auto_connect : bool
        If True, automatically call ConnectPort() upon construction.
    auto_setup_can : bool
        If True, automatically detect and configure CAN device if needed.
        Will run scripts/find_all_can_port.sh and scripts/can_activate.sh scripts.
    tcp_zero_pose : Optional[Tuple[float, float, float, float, float, float]]
        Default TCP pose (X,Y,Z, RX,RY,RZ) in units of mm/deg for the robot when joints are all zero.
        If None, uses a conservative default: (56.127, 0.0, 213.266, 0.0, 84.999, 0.0)
    interface : Optional[C_PiperInterface_V2]
        If provided, use this instance instead of creating a new one.
        When using this parameter, can_name and auto_setup_can are ignored.
    
    Examples
    --------
    Basic usage (auto-setup enabled):
    >>> arm = EasyPiper()  # Uses can0, auto-detects and configures
    
    Specify CAN device:
    >>> arm = EasyPiper(can_name='can_piper')
    
    Multiple CAN devices (specify USB port):
    >>> arm = EasyPiper(can_name='can_arm', can_usb_port='3-1.4:1.0')
    
    Manual CAN setup (disable auto-setup):
    >>> arm = EasyPiper(can_name='can0', auto_setup_can=False)
    
    Use existing SDK interface:
    >>> from piper_sdk import C_PiperInterface_V2
    >>> iface = C_PiperInterface_V2('can0')
    >>> arm = EasyPiper(interface=iface)
    """

    # Default TCP pose (mm/deg) when all joints are 0 deg (from test.ipynb observations)
    DEFAULT_TCP_ZERO_POSE = (56.127, 0.0, 213.266, 0.0, 84.999, 0.0)

    def __init__(
        self,
        can_name: str = "can0",
        can_usb_port: Optional[str] = None,
        auto_connect: bool = True,
        auto_setup_can: bool = True,
        tcp_zero_pose: Optional[Tuple[float, float, float, float, float, float]] = None,
        interface: Optional[C_PiperInterface_V2] = None,
    ) -> None:
        self.can_name = can_name
        self.can_usb_port = can_usb_port
        self.tcp_zero_pose = tcp_zero_pose or self.DEFAULT_TCP_ZERO_POSE
        
        # If interface provided, use it directly
        if interface is not None:
            self.iface = interface
            if auto_connect and not self.iface.get_connect_status():
                self.iface.ConnectPort()
                time.sleep(0.1)
            return
        
        # Check and setup CAN device if needed
        if auto_setup_can:
            can_ready = self._ensure_can_device_ready()
            if not can_ready:
                raise RuntimeError(
                    f"Failed to setup CAN device '{can_name}'. "
                    f"Please check CAN adapter connection and try again, "
                    f"or set auto_setup_can=False and configure manually."
                )
        
        # Create SDK interface
        try:
            self.iface = C_PiperInterface_V2(
                can_name=can_name,
                judge_flag=False,  # Don't judge - we've already checked
                can_auto_init=True
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to create SDK interface for '{can_name}': {e}\n"
                f"Please verify CAN device is properly configured."
            ) from e
        
        # Connect if requested
        if auto_connect:
            try:
                self.iface.ConnectPort()
                # Give firmware a moment to start streaming feedback frames
                time.sleep(0.1)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to connect to robot arm on '{can_name}': {e}\n"
                    f"Please check:\n"
                    f"  1. Robot arm is powered on\n"
                    f"  2. CAN cable is connected\n"
                    f"  3. CAN device '{can_name}' is properly configured"
                ) from e

    def _ensure_can_device_ready(self) -> bool:
        """Ensure CAN device exists and is properly configured.
        
        Returns:
            True if CAN device is ready, False otherwise
        """
        # Check if device exists
        if _check_can_device_exists(self.can_name):
            # Check if it's UP and configured
            if _check_can_device_up(self.can_name):
                print(f"✓ CAN device '{self.can_name}' is ready")
                return True
            else:
                print(f"⚠️  CAN device '{self.can_name}' exists but not configured")
                print(f"Attempting to activate '{self.can_name}'...")
                return _activate_can_device(
                    self.can_name, 
                    usb_address=self.can_usb_port,
                    verbose=True
                )
        else:
            # Device doesn't exist - try to set it up
            print(f"⚠️  CAN device '{self.can_name}' not found")
            if self.can_usb_port:
                # USB port specified - activate directly
                print(f"Activating '{self.can_name}' at USB port '{self.can_usb_port}'...")
                return _activate_can_device(
                    self.can_name,
                    usb_address=self.can_usb_port,
                    verbose=True
                )
            else:
                # No USB port specified - interactive setup
                return _setup_can_device_interactive(self.can_name)

    # ----------------------------
    # Basic power/motion management
    # ----------------------------
    def enable(self, wait: bool = True, timeout_s: float = 3.0) -> bool:
        """Enable arm motors.

        SDK: EnablePiper() → bool.

        Returns True if enable acknowledged. If wait=True, will poll until success or timeout.
        """
        start = time.time()
        ok = self.iface.EnablePiper()
        if not wait:
            return ok
        while not ok and (time.time() - start) < timeout_s:
            time.sleep(0.01)
            ok = self.iface.EnablePiper()
        return ok

    def disable(self) -> bool:
        """Disable arm motors.

        SDK: DisablePiper() → bool.
        Return value semantics are SDK-defined; we simply return the SDK result.
        """
        return self.iface.DisablePiper()

    def emergency_stop(self) -> None:
        """Immediate emergency stop.

        SDK: MotionCtrl_1(emergency_stop=0x01, track_ctrl=0x00, grag_teach_ctrl=0x00)
        """
        self.iface.MotionCtrl_1(emergency_stop=0x01, track_ctrl=0x00, grag_teach_ctrl=0x00)

    def resume(self) -> None:
        """Resume after emergency stop.

        SDK: MotionCtrl_1(emergency_stop=0x02, track_ctrl=0x00, grag_teach_ctrl=0x00)
        """
        self.iface.MotionCtrl_1(emergency_stop=0x02, track_ctrl=0x00, grag_teach_ctrl=0x00)

    def reset_sequence(self, speed_percent: int = 30) -> None:
        """Safe reset: emergency stop → resume → enable → set MOVE J at given speed.

        Calls:
        - MotionCtrl_1(0x01) [E-stop]
        - MotionCtrl_1(0x02) [Resume]
        - EnablePiper() until True
        - ModeCtrl(ctrl_mode=0x01, move_mode=0x01, move_spd_rate_ctrl=speed_percent, is_mit_mode=0x00)
        """
        self.emergency_stop()
        time.sleep(0.05)
        self.resume()
        time.sleep(0.05)
        self.enable(wait=True)
        time.sleep(0.05)
        self.switch_mode_joint(speed_percent=speed_percent)
        time.sleep(0.1)

    # ----------------------------
    # Mode switching
    # ----------------------------
    def switch_mode_joint(self, speed_percent: int = 30, is_mit: bool = False) -> None:
        """Switch to CAN + MOVE J (joint mode).

        SDK: ModeCtrl(ctrl_mode=0x01, move_mode=0x01, move_spd_rate_ctrl, is_mit_mode)
        """
        self.iface.ModeCtrl(
            ctrl_mode=0x01,
            move_mode=0x01,
            move_spd_rate_ctrl=int(speed_percent),
            is_mit_mode=0x01 if is_mit else 0x00,
        )

    def switch_mode_move_p(self, speed_percent: int = 30, is_mit: bool = False) -> None:
        """Switch to CAN + MOVE P (point-to-point Cartesian motion).

        SDK: ModeCtrl(ctrl_mode=0x01, move_mode=0x00, move_spd_rate_ctrl, is_mit_mode)
        """
        self.iface.ModeCtrl(
            ctrl_mode=0x01,
            move_mode=0x00,
            move_spd_rate_ctrl=int(speed_percent),
            is_mit_mode=0x01 if is_mit else 0x00,
        )

    def switch_mode_move_l(self, speed_percent: int = 30, is_mit: bool = False) -> None:
        """Switch to CAN + MOVE L (linear Cartesian motion).

        SDK: ModeCtrl(ctrl_mode=0x01, move_mode=0x02, move_spd_rate_ctrl, is_mit_mode)
        """
        self.iface.ModeCtrl(
            ctrl_mode=0x01,
            move_mode=0x02,
            move_spd_rate_ctrl=int(speed_percent),
            is_mit_mode=0x01 if is_mit else 0x00,
        )

    def switch_mode_cartesian(self, speed_percent: int = 30, mode: str = "L") -> None:
        """Switch to Cartesian motion mode (alias for move_l/move_p).

        Convenience method for API consistency with README examples.

        Args:
            speed_percent: Speed as percentage (0-100)
            mode: 'L' for linear motion, 'P' for point-to-point (default: 'L')

        Raises:
            ValueError: If mode is not 'L' or 'P'
        """
        if mode.upper() == "L":
            self.switch_mode_move_l(speed_percent=speed_percent)
        elif mode.upper() == "P":
            self.switch_mode_move_p(speed_percent=speed_percent)
        else:
            raise ValueError("mode must be 'L' or 'P'")

    # ----------------------------
    # Joint motions
    # ----------------------------
    def go_zero_joints(self, ensure_joint_mode: bool = True, speed_percent: int = 30) -> None:
        """Go to joint zero (all joints = 0 deg).

        SDK calls:
        - optional: ModeCtrl(... move_mode=0x01 ...)
        - JointCtrl(0, 0, 0, 0, 0, 0)
        """
        if ensure_joint_mode:
            self.switch_mode_joint(speed_percent=speed_percent)
            time.sleep(0.05)
        self.iface.JointCtrl(0, 0, 0, 0, 0, 0)

    def go_to_joint_angles(self, angles_deg: Sequence[float]) -> None:
        """Move to absolute joint angles in degrees (length-6 sequence).

        SDK: JointCtrl(j1..j6) in 0.001 deg.
        """
        if len(angles_deg) != 6:
            raise ValueError("angles_deg must have 6 elements")
        j = [_deg_to_001deg(v) for v in angles_deg]
        self.iface.JointCtrl(j[0], j[1], j[2], j[3], j[4], j[5])

    def move_joints(self, angles_deg: Sequence[float]) -> None:
        """Alias for go_to_joint_angles for API consistency with README examples.

        Move to absolute joint angles in degrees (length-6 sequence).

        Args:
            angles_deg: List/tuple of 6 joint angles in degrees

        SDK: JointCtrl(j1..j6) in 0.001 deg.
        """
        self.go_to_joint_angles(angles_deg)

    # ----------------------------
    # TCP motions (Cartesian)
    # ----------------------------
    def go_zero_tcp(self, mode: str = "L", speed_percent: int = 30) -> None:
        """Go to the TCP pose corresponding to joint zero using EndPoseCtrl.

        Args
        ----
        mode: 'L' or 'P' — switches to MOVE L or MOVE P, then commands EndPoseCtrl.
        speed_percent: speed percentage to set when switching mode.

        SDK calls:
        - ModeCtrl(... move_mode=0x02 or 0x00 ...)
        - EndPoseCtrl(X,Y,Z,RX,RY,RZ) in 0.001 mm/deg
        """
        if mode.upper() == "L":
            self.switch_mode_move_l(speed_percent=speed_percent)
        elif mode.upper() == "P":
            self.switch_mode_move_p(speed_percent=speed_percent)
        else:
            raise ValueError("mode must be 'L' or 'P'")
        time.sleep(0.05)
        X, Y, Z, RX, RY, RZ = self.tcp_zero_pose
        self.iface.EndPoseCtrl(
            X=_mm_to_001mm(X),
            Y=_mm_to_001mm(Y),
            Z=_mm_to_001mm(Z),
            RX=_deg_to_001deg(RX),
            RY=_deg_to_001deg(RY),
            RZ=_deg_to_001deg(RZ),
        )

    def go_to_tcp_pose(
        self,
        X_mm: float,
        Y_mm: float,
        Z_mm: float,
        RX_deg: float,
        RY_deg: float,
        RZ_deg: float,
        ensure_mode: Optional[str] = None,
        speed_percent: int = 30,
        wait_s: float = 0.0,
    ) -> None:
        """Move to an absolute TCP pose. Units are mm/deg.

        Args
        ----
        ensure_mode: Optional[str]
            If 'L' or 'P', switch to corresponding mode before moving.
        speed_percent: If switching mode, sets the mode speed.
        wait_s: Optional sleep after issuing the command.

        SDK: EndPoseCtrl(X,Y,Z,RX,RY,RZ) with 0.001 mm/deg units.
        """
        if ensure_mode is not None:
            if ensure_mode.upper() == "L":
                self.switch_mode_move_l(speed_percent=speed_percent)
            elif ensure_mode.upper() == "P":
                self.switch_mode_move_p(speed_percent=speed_percent)
            else:
                raise ValueError("ensure_mode must be 'L', 'P', or None")
            time.sleep(0.05)
        self.iface.EndPoseCtrl(
            X=_mm_to_001mm(X_mm),
            Y=_mm_to_001mm(Y_mm),
            Z=_mm_to_001mm(Z_mm),
            RX=_deg_to_001deg(RX_deg),
            RY=_deg_to_001deg(RY_deg),
            RZ=_deg_to_001deg(RZ_deg),
        )
        if wait_s > 0:
            time.sleep(wait_s)

    def move_tcp_pose(
        self,
        pose: Sequence[float],
        ensure_mode: Optional[str] = None,
        speed_percent: int = 30,
        wait_s: float = 0.0,
    ) -> None:
        """Move to TCP pose using list/tuple format (for API consistency with README).

        Convenience method that accepts pose as a single sequence instead of separate args.

        Args:
            pose: Sequence of 6 values [X, Y, Z, RX, RY, RZ] in mm and degrees
            ensure_mode: Optional[str] - If 'L' or 'P', switch to mode before moving
            speed_percent: If switching mode, sets the mode speed
            wait_s: Optional sleep after issuing the command

        Raises:
            ValueError: If pose doesn't have exactly 6 elements

        SDK: EndPoseCtrl(X,Y,Z,RX,RY,RZ) with 0.001 mm/deg units.
        """
        if len(pose) != 6:
            raise ValueError("pose must have 6 elements [X, Y, Z, RX, RY, RZ]")
        
        self.go_to_tcp_pose(
            X_mm=pose[0],
            Y_mm=pose[1],
            Z_mm=pose[2],
            RX_deg=pose[3],
            RY_deg=pose[4],
            RZ_deg=pose[5],
            ensure_mode=ensure_mode,
            speed_percent=speed_percent,
            wait_s=wait_s,
        )

    # ----------------------------
    # Gripper
    # ----------------------------
    def gripper_enable(self, effort: int = 1000, clear_error: bool = False) -> None:
        """Enable gripper; optionally clear errors.

        SDK:
        - GripperCtrl(gripper_angle=0, gripper_effort=effort, gripper_code=0x03 if clear else 0x01, set_zero=0x00)
        """
        self.iface.GripperCtrl(
            gripper_angle=0,
            gripper_effort=int(effort),
            gripper_code=0x03 if clear_error else 0x01,
            set_zero=0x00,
        )

    def gripper_disable(self, clear_error: bool = False) -> None:
        """Disable gripper; optionally clear errors.

        SDK:
        - GripperCtrl(gripper_angle=0, gripper_effort=0, gripper_code=0x02 if clear else 0x00, set_zero=0x00)
        """
        self.iface.GripperCtrl(
            gripper_angle=0,
            gripper_effort=0,
            gripper_code=0x02 if clear_error else 0x00,
            set_zero=0x00,
        )

    def gripper_set_zero(self) -> None:
        """Set current gripper position as zero.

        SDK requires gripper enabled. Call:
        - GripperCtrl(gripper_angle=0, gripper_effort=0, gripper_code=0x01, set_zero=0xAE)
        """
        self.iface.GripperCtrl(
            gripper_angle=0,
            gripper_effort=0,
            gripper_code=0x01,
            set_zero=0xAE,
        )

    def gripper_move(self, width_mm: float, effort_nm: float = 1.0) -> None:
        """Move gripper to specified width with given effort.

        Args:
            width_mm: Target gripper width in millimeters
            effort_nm: Gripper effort in N·m (0-5 N·m)

        SDK: GripperCtrl(gripper_angle, gripper_effort, 0x01, 0x00)
        """
        self.iface.GripperCtrl(
            gripper_angle=_mm_to_001mm(width_mm),
            gripper_effort=int(effort_nm * 1000),
            gripper_code=0x01,
            set_zero=0x00,
        )

    def gripper_open(self, width_mm: float = 70.0, effort_nm: float = 1.0) -> None:
        """Open gripper to specified width.

        Convenience method for API consistency with README examples.

        Args:
            width_mm: Target gripper width in millimeters (default: 70mm, fully open)
            effort_nm: Gripper effort in N·m (default: 1.0 N·m)
        """
        self.gripper_move(width_mm=width_mm, effort_nm=effort_nm)

    def gripper_close(self, width_mm: float = 0.0, effort_nm: float = 1.5) -> None:
        """Close gripper to specified width.

        Convenience method for API consistency with README examples.

        Args:
            width_mm: Target gripper width in millimeters (default: 0mm, fully closed)
            effort_nm: Gripper effort in N·m (default: 1.5 N·m for gripping)
        """
        self.gripper_move(width_mm=width_mm, effort_nm=effort_nm)

    def gripper_set_position(self, width_mm: float, effort_nm: float = 1.0) -> None:
        """Set gripper position (alias for gripper_move).

        Convenience method for API consistency with README examples.

        Args:
            width_mm: Target gripper width in millimeters
            effort_nm: Gripper effort in N·m (default: 1.0 N·m)
        """
        self.gripper_move(width_mm=width_mm, effort_nm=effort_nm)

    # ----------------------------
    # Advanced motion control
    # ----------------------------
    def switch_mode_move_c(self, speed_percent: int = 30) -> None:
        """Switch to CAN + MOVE C (circular/arc motion).

        SDK: MotionCtrl_2(ctrl_mode=0x01, move_mode=0x03, move_spd_rate_ctrl, is_mit_mode=0x00)
        """
        self.iface.MotionCtrl_2(
            ctrl_mode=0x01,
            move_mode=0x03,
            move_spd_rate_ctrl=int(speed_percent),
            is_mit_mode=0x00,
            residence_time=0,
            installation_pos=0x00,
        )

    def move_c_update(self, instruction: Literal[0, 1, 2, 3] = 0) -> None:
        """Update circular motion instruction.

        Args:
            instruction:
                0x00: No action
                0x01: Start point
                0x02: Intermediate point
                0x03: End point

        SDK: MoveCAxisUpdateCtrl(instruction_num)
        """
        self.iface.MoveCAxisUpdateCtrl(instruction_num=instruction)

    def switch_mode_mit(self, speed_percent: int = 0) -> None:
        """Switch to MIT/drag-teach mode (firmware >= V1.5-2).

        SDK: MotionCtrl_2(ctrl_mode=0x01, move_mode=0x04, move_spd_rate_ctrl, is_mit_mode=0xAD)
        """
        self.iface.MotionCtrl_2(
            ctrl_mode=0x01,
            move_mode=0x04,
            move_spd_rate_ctrl=int(speed_percent),
            is_mit_mode=0xAD,
            residence_time=0,
            installation_pos=0x00,
        )

    def joint_mit_ctrl(
        self,
        motor_num: int,
        pos_ref: float,
        vel_ref: float,
        kp: float,
        kd: float,
        t_ref: float,
    ) -> None:
        """Send MIT control command to a specific joint.

        Args:
            motor_num: Joint number (1-6)
            pos_ref: Position reference (rad)
            vel_ref: Velocity reference (rad/s)
            kp: Position gain (0-500)
            kd: Damping gain (-5 to 5)
            t_ref: Torque reference (-8 to 8 N·m)

        SDK: JointMitCtrl(motor_num, pos_ref, vel_ref, kp, kd, t_ref)
        Note: Requires MIT mode enabled. Use with caution - can damage hardware if misused.
        """
        self.iface.JointMitCtrl(motor_num, pos_ref, vel_ref, kp, kd, t_ref)

    # ----------------------------
    # Teach mode control
    # ----------------------------
    def teach_start(self) -> None:
        """Start teach/record mode (enter drag-teach).

        SDK: MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x00, grag_teach_ctrl=0x01)
        """
        self.iface.MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x00, grag_teach_ctrl=0x01)

    def teach_end(self) -> None:
        """End teach/record mode (exit drag-teach).

        SDK: MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x00, grag_teach_ctrl=0x02)
        """
        self.iface.MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x00, grag_teach_ctrl=0x02)

    def teach_execute(self) -> None:
        """Execute recorded trajectory.

        SDK: MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x00, grag_teach_ctrl=0x03)
        """
        self.iface.MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x00, grag_teach_ctrl=0x03)

    def teach_pause(self) -> None:
        """Pause trajectory execution.

        SDK: MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x00, grag_teach_ctrl=0x04)
        """
        self.iface.MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x00, grag_teach_ctrl=0x04)

    def teach_continue(self) -> None:
        """Continue paused trajectory execution.

        SDK: MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x00, grag_teach_ctrl=0x05)
        """
        self.iface.MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x00, grag_teach_ctrl=0x05)

    def teach_terminate(self) -> None:
        """Terminate trajectory execution.

        SDK: MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x00, grag_teach_ctrl=0x06)
        """
        self.iface.MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x00, grag_teach_ctrl=0x06)

    def trajectory_clear(self) -> None:
        """Clear current trajectory.

        SDK: MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x03, grag_teach_ctrl=0x00)
        """
        self.iface.MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x03, grag_teach_ctrl=0x00)

    def trajectory_clear_all(self) -> None:
        """Clear all trajectories.

        SDK: MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x04, grag_teach_ctrl=0x00)
        """
        self.iface.MotionCtrl_1(emergency_stop=0x00, track_ctrl=0x04, grag_teach_ctrl=0x00)

    # ----------------------------
    # Master-Slave configuration
    # ----------------------------
    def set_master_arm(self) -> None:
        """Configure this arm as master (teaching input arm).

        SDK: MasterSlaveConfig(linkage_config=0xFA, feedback_offset=0, ctrl_offset=0, linkage_offset=0)
        """
        self.iface.MasterSlaveConfig(
            linkage_config=0xFA, feedback_offset=0, ctrl_offset=0, linkage_offset=0
        )

    def set_slave_arm(self) -> None:
        """Configure this arm as slave (motion output arm).

        SDK: MasterSlaveConfig(linkage_config=0xFC, feedback_offset=0, ctrl_offset=0, linkage_offset=0)
        """
        self.iface.MasterSlaveConfig(
            linkage_config=0xFC, feedback_offset=0, ctrl_offset=0, linkage_offset=0
        )

    # ----------------------------
    # Joint configuration
    # ----------------------------
    def set_joint_zero(self, joint_num: Literal[1, 2, 3, 4, 5, 6, 7] = 7) -> None:
        """Set current position as zero for specified joint(s).

        Args:
            joint_num: Joint number 1-6, or 7 for all joints

        SDK: JointConfig(joint_num, set_zero=0xAE, acc_param_is_effective=0x00, max_joint_acc=500, clear_err=0x00)
        """
        self.iface.JointConfig(
            joint_num=joint_num,
            set_zero=0xAE,
            acc_param_is_effective=0x00,
            max_joint_acc=500,
            clear_err=0x00,
        )

    def set_joint_max_acc(
        self, motor_num: Literal[1, 2, 3, 4, 5, 6], max_acc: int = 500
    ) -> None:
        """Set maximum acceleration for a specific joint.

        Args:
            motor_num: Joint number 1-6
            max_acc: Maximum acceleration value

        SDK: JointMaxAccConfig(motor_num, max_joint_acc)
        """
        self.iface.JointMaxAccConfig(motor_num=motor_num, max_joint_acc=max_acc)

    def set_joint_max_speed(
        self, motor_num: Literal[1, 2, 3, 4, 5, 6], max_speed: int = 3000
    ) -> None:
        """Set maximum speed for a specific joint.

        Args:
            motor_num: Joint number 1-6
            max_speed: Maximum speed value (0.001 deg/s units)

        SDK: MotorMaxSpdSet(motor_num, max_joint_spd)
        """
        self.iface.MotorMaxSpdSet(motor_num=motor_num, max_joint_spd=max_speed)

    def clear_joint_error(self, joint_num: Literal[1, 2, 3, 4, 5, 6, 7] = 7) -> None:
        """Clear error for specified joint(s).

        Args:
            joint_num: Joint number 1-6, or 7 for all joints

        SDK: JointConfig(joint_num, set_zero=0x00, acc_param_is_effective=0x00, max_joint_acc=500, clear_err=0xAE)
        """
        self.iface.JointConfig(
            joint_num=joint_num,
            set_zero=0x00,
            acc_param_is_effective=0x00,
            max_joint_acc=500,
            clear_err=0xAE,
        )

    # ----------------------------
    # End effector configuration
    # ----------------------------
    def set_end_speed_acc(
        self,
        max_linear_vel: int,
        max_angular_vel: int,
        max_linear_acc: int,
        max_angular_acc: int,
    ) -> None:
        """Set end effector maximum velocities and accelerations.

        Args:
            max_linear_vel: Maximum linear velocity
            max_angular_vel: Maximum angular velocity
            max_linear_acc: Maximum linear acceleration
            max_angular_acc: Maximum angular acceleration

        SDK: EndSpdAndAccParamSet(end_max_linear_vel, end_max_angular_vel, end_max_linear_acc, end_max_angular_acc)
        """
        self.iface.EndSpdAndAccParamSet(
            max_linear_vel, max_angular_vel, max_linear_acc, max_angular_acc
        )

    def set_end_load(self, load_type: Literal[0, 1, 2, 3] = 3) -> None:
        """Set end effector load type.

        Args:
            load_type: Load configuration (0-3)

        SDK: ArmParamEnquiryAndConfig(param_enquiry=0, param_setting=0, data_feedback_0x48x=0,
                                       end_load_param_setting_effective=0xAE, set_end_load=load_type)
        """
        self.iface.ArmParamEnquiryAndConfig(
            param_enquiry=0x00,
            param_setting=0x00,
            data_feedback_0x48x=0x00,
            end_load_param_setting_effective=0xAE,
            set_end_load=load_type,
        )

    # ----------------------------
    # Collision protection
    # ----------------------------
    def set_crash_protection(
        self,
        j1_level: int = 0,
        j2_level: int = 0,
        j3_level: int = 0,
        j4_level: int = 0,
        j5_level: int = 0,
        j6_level: int = 0,
    ) -> None:
        """Set collision protection levels for all joints.

        Args:
            j1_level to j6_level: Protection level for each joint (0 = off)

        SDK: CrashProtectionConfig(joint_1_protection_level, ..., joint_6_protection_level)
        """
        self.iface.CrashProtectionConfig(
            j1_level, j2_level, j3_level, j4_level, j5_level, j6_level
        )

    # ----------------------------
    # Gripper advanced configuration
    # ----------------------------
    def set_gripper_params(
        self, teaching_range_pct: int = 100, max_range: int = 70, friction: int = 1
    ) -> None:
        """Configure gripper teaching and range parameters.

        Args:
            teaching_range_pct: Teaching range percentage (0-100)
            max_range: Maximum range configuration
            friction: Friction parameter

        SDK: GripperTeachingPendantParamConfig(teaching_range_per, max_range_config, teaching_friction)
        """
        self.iface.GripperTeachingPendantParamConfig(
            teaching_range_pct, max_range, friction
        )

    # ----------------------------
    # Query/Search operations
    # ----------------------------
    def search_firmware_version(self) -> None:
        """Request firmware version (read with get_firmware_version).

        SDK: SearchPiperFirmwareVersion()
        """
        self.iface.SearchPiperFirmwareVersion()

    def search_motor_limits(
        self, motor_num: Literal[1, 2, 3, 4, 5, 6], content: Literal[1, 2] = 1
    ) -> None:
        """Search motor angle/speed/acceleration limits.

        Args:
            motor_num: Joint number 1-6
            content: 0x01 for angle/speed limits, 0x02 for acceleration limits

        SDK: SearchMotorMaxAngleSpdAccLimit(motor_num, search_content)
        """
        self.iface.SearchMotorMaxAngleSpdAccLimit(
            motor_num=motor_num, search_content=content
        )

    def search_all_motor_speeds(self) -> None:
        """Request max speeds for all motors (read with get_all_motor_limits).

        SDK: SearchAllMotorMaxAngleSpd()
        """
        self.iface.SearchAllMotorMaxAngleSpd()

    def search_all_motor_accelerations(self) -> None:
        """Request max accelerations for all motors (read with get_all_motor_acc_limits).

        SDK: SearchAllMotorMaxAccLimit()
        """
        self.iface.SearchAllMotorMaxAccLimit()

    def query_end_speed_acc(self) -> None:
        """Query end effector speed/acceleration parameters (read with get_end_speed_acc).

        SDK: ArmParamEnquiryAndConfig(param_enquiry=0x01, ...)
        """
        self.iface.ArmParamEnquiryAndConfig(
            param_enquiry=0x01,
            param_setting=0x00,
            data_feedback_0x48x=0x00,
            end_load_param_setting_effective=0x00,
            set_end_load=0x03,
        )

    def query_crash_protection(self) -> None:
        """Query crash protection levels (read with get_crash_protection).

        SDK: ArmParamEnquiryAndConfig(param_enquiry=0x02, ...)
        """
        self.iface.ArmParamEnquiryAndConfig(
            param_enquiry=0x02,
            param_setting=0x00,
            data_feedback_0x48x=0x00,
            end_load_param_setting_effective=0x00,
            set_end_load=0x03,
        )

    def query_gripper_params(self) -> None:
        """Query gripper parameters (read with get_gripper_teach_params).

        SDK: ArmParamEnquiryAndConfig(param_enquiry=0x04, ...)
        """
        self.iface.ArmParamEnquiryAndConfig(
            param_enquiry=0x04,
            param_setting=0x00,
            data_feedback_0x48x=0x00,
            end_load_param_setting_effective=0x00,
            set_end_load=0x03,
        )

    # ----------------------------
    # Introspection helpers
    # ----------------------------
    def get_current_mode(self) -> Any:
        """Return raw mode structure.

        SDK: GetArmModeCtrl() → struct with fields: mode_ctrl.ctrl_mode, move_mode, mit_mode, move_spd_rate_ctrl; Hz
        """
        return self.iface.GetArmModeCtrl()

    def get_current_tcp(self) -> Dict[str, float]:
        """Get current TCP pose as a dict with mm/deg units.

        SDK: GetArmEndPoseMsgs() → struct with end_pose.X_axis, Y_axis, Z_axis (0.001 mm);
             RX_axis, RY_axis, RZ_axis (0.001 deg); and Hz.
        """
        pose = self.iface.GetArmEndPoseMsgs()
        return {
            "X_mm": _001mm_to_mm(pose.end_pose.X_axis),
            "Y_mm": _001mm_to_mm(pose.end_pose.Y_axis),
            "Z_mm": _001mm_to_mm(pose.end_pose.Z_axis),
            "RX_deg": _001deg_to_deg(pose.end_pose.RX_axis),
            "RY_deg": _001deg_to_deg(pose.end_pose.RY_axis),
            "RZ_deg": _001deg_to_deg(pose.end_pose.RZ_axis),
            "Hz": pose.Hz,
        }

    def get_joint_state(self) -> Dict[str, float]:
        """Get current joint angles as a dict with degree units.

        SDK: GetArmJointMsgs() → struct with joint_state.joint_1..joint_6 (0.001 deg)
        """
        joints = self.iface.GetArmJointMsgs()
        js = joints.joint_state
        return {
            "j1_deg": _001deg_to_deg(js.joint_1),
            "j2_deg": _001deg_to_deg(js.joint_2),
            "j3_deg": _001deg_to_deg(js.joint_3),
            "j4_deg": _001deg_to_deg(js.joint_4),
            "j5_deg": _001deg_to_deg(js.joint_5),
            "j6_deg": _001deg_to_deg(js.joint_6),
            "Hz": joints.Hz,
        }

    def get_gripper_state(self) -> Dict[str, Any]:
        """Get current gripper state.

        SDK: GetArmGripperMsgs() → struct with gripper_state fields
        """
        gm = self.iface.GetArmGripperMsgs()
        gs = gm.gripper_state
        result = {
            "Hz": gm.Hz,
            "angle_mm": _001mm_to_mm(getattr(gs, "grippers_angle", 0)),
            "effort_nm": getattr(gs, "grippers_effort", 0) / 1000.0,
        }
        # Include FOC status if available
        fs = getattr(gs, "foc_status", None)
        if fs is not None:
            result["foc_status"] = {
                "voltage_too_low": getattr(fs, "voltage_too_low", None),
                "motor_overheating": getattr(fs, "motor_overheating", None),
                "driver_overcurrent": getattr(fs, "driver_overcurrent", None),
                "driver_overheating": getattr(fs, "driver_overheating", None),
                "sensor_status": getattr(fs, "sensor_status", None),
                "driver_error_status": getattr(fs, "driver_error_status", None),
                "driver_enable_status": getattr(fs, "driver_enable_status", None),
                "homing_status": getattr(fs, "homing_status", None),
            }
        return result

    def get_arm_status(self) -> Any:
        """Get arm status information.

        SDK: GetArmStatus() → struct with motion_status, mode_status, error_status, etc.
        """
        return self.iface.GetArmStatus()

    def get_enable_status(self) -> list:
        """Get enable status for all joints.

        SDK: GetArmEnableStatus() → list of enable states
        """
        return self.iface.GetArmEnableStatus()

    def get_firmware_version(self) -> Any:
        """Get firmware version (call search_firmware_version first).

        SDK: GetPiperFirmwareVersion()
        """
        return self.iface.GetPiperFirmwareVersion()

    def get_motor_limits(self) -> Any:
        """Get motor angle limits and max velocity (call search_motor_limits first).

        SDK: GetCurrentMotorAngleLimitMaxVel()
        """
        return self.iface.GetCurrentMotorAngleLimitMaxVel()

    def get_motor_max_acc(self) -> Any:
        """Get motor maximum acceleration (call search_motor_limits first).

        SDK: GetCurrentMotorMaxAccLimit()
        """
        return self.iface.GetCurrentMotorMaxAccLimit()

    def get_all_motor_limits(self) -> Any:
        """Get all motors' angle limits and max speeds (call search_all_motor_speeds first).

        SDK: GetAllMotorAngleLimitMaxSpd()
        """
        return self.iface.GetAllMotorAngleLimitMaxSpd()

    def get_all_motor_acc_limits(self) -> Any:
        """Get all motors' max accelerations (call search_all_motor_accelerations first).

        SDK: GetAllMotorMaxAccLimit()
        """
        return self.iface.GetAllMotorMaxAccLimit()

    def get_end_speed_acc(self) -> Any:
        """Get end effector speed/acceleration parameters (call query_end_speed_acc first).

        SDK: GetCurrentEndVelAndAccParam()
        """
        return self.iface.GetCurrentEndVelAndAccParam()

    def get_crash_protection(self) -> Any:
        """Get crash protection levels (call query_crash_protection first).

        SDK: GetCrashProtectionLevelFeedback()
        """
        return self.iface.GetCrashProtectionLevelFeedback()

    def get_gripper_teach_params(self) -> Any:
        """Get gripper teaching parameters (call query_gripper_params first).

        SDK: GetGripperTeachingPendantParamFeedback()
        """
        return self.iface.GetGripperTeachingPendantParamFeedback()

    def get_high_speed_info(self) -> Any:
        """Get high-speed motor driver feedback information.

        SDK: GetArmHighSpdInfoMsgs()
        """
        return self.iface.GetArmHighSpdInfoMsgs()

    def get_low_speed_info(self) -> Any:
        """Get low-speed motor driver feedback information.

        SDK: GetArmLowSpdInfoMsgs()
        """
        return self.iface.GetArmLowSpdInfoMsgs()

    def get_joint_ctrl(self) -> Any:
        """Get current joint control commands being sent.

        SDK: GetArmJointCtrl()
        """
        return self.iface.GetArmJointCtrl()

    def get_gripper_ctrl(self) -> Any:
        """Get current gripper control commands being sent.

        SDK: GetArmGripperCtrl()
        """
        return self.iface.GetArmGripperCtrl()

    def get_fk(self, mode: Literal["feedback", "control"] = "feedback") -> Any:
        """Get forward kinematics calculation result.

        Args:
            mode: "feedback" for FK from joint feedback, "control" for FK from joint commands

        SDK: GetFK(mode)
        """
        return self.iface.GetFK(mode=mode)

    def get_can_fps(self) -> float:
        """Get CAN bus communication frame rate.

        SDK: GetCanFps()
        """
        return self.iface.GetCanFps()

    def is_ok(self) -> bool:
        """Check if arm is in OK state.

        SDK: isOk()
        """
        return self.iface.isOk()

    def get_connection_status(self) -> bool:
        """Check if port is connected.

        SDK: get_connect_status()
        """
        return self.iface.get_connect_status()

    # ----------------------------
    # SDK parameter configuration
    # ----------------------------
    def get_sdk_joint_limits(
        self, joint_name: Literal["j1", "j2", "j3", "j4", "j5", "j6"]
    ) -> Any:
        """Get SDK-level software joint limits.

        SDK: GetSDKJointLimitParam(joint_name)
        """
        return self.iface.GetSDKJointLimitParam(joint_name)

    def set_sdk_joint_limits(
        self,
        joint_name: Literal["j1", "j2", "j3", "j4", "j5", "j6"],
        min_val: float,
        max_val: float,
    ) -> None:
        """Set SDK-level software joint limits.

        SDK: SetSDKJointLimitParam(joint_name, min_val, max_val)
        """
        self.iface.SetSDKJointLimitParam(joint_name, min_val, max_val)

    def get_sdk_gripper_range(self) -> Any:
        """Get SDK-level software gripper range limits.

        SDK: GetSDKGripperRangeParam()
        """
        return self.iface.GetSDKGripperRangeParam()

    def set_sdk_gripper_range(self, min_val: float, max_val: float) -> None:
        """Set SDK-level software gripper range limits.

        SDK: SetSDKGripperRangeParam(min_val, max_val)
        """
        self.iface.SetSDKGripperRangeParam(min_val, max_val)

    # ----------------------------
    # Advanced features
    # ----------------------------
    def enable_fk_calculation(self) -> None:
        """Enable forward kinematics calculation.

        SDK: EnableFkCal()
        """
        self.iface.EnableFkCal()

    def disable_fk_calculation(self) -> None:
        """Disable forward kinematics calculation.

        SDK: DisableFkCal()
        """
        self.iface.DisableFkCal()

    def is_fk_enabled(self) -> bool:
        """Check if FK calculation is enabled.

        SDK: isCalFk()
        """
        return self.iface.isCalFk()

    def disconnect(self, thread_timeout: float = 0.1) -> None:
        """Disconnect from the arm and clean up.

        SDK: DisconnectPort(thread_timeout)
        """
        self.iface.DisconnectPort(thread_timeout=thread_timeout)

    def get_interface_version(self) -> Any:
        """Get current interface version.

        SDK: GetCurrentInterfaceVersion()
        """
        return self.iface.GetCurrentInterfaceVersion()

    def get_sdk_version(self) -> Any:
        """Get current SDK version.

        SDK: GetCurrentSDKVersion()
        """
        return self.iface.GetCurrentSDKVersion()

    def get_protocol_version(self) -> Any:
        """Get current protocol version.

        SDK: GetCurrentProtocolVersion()
        """
        return self.iface.GetCurrentProtocolVersion()

    def get_can_bus(self) -> Any:
        """Get CAN bus object.

        SDK: GetCanBus()
        """
        return self.iface.GetCanBus()

    def get_can_name(self) -> str:
        """Get CAN port name.

        SDK: GetCanName()
        """
        return self.iface.GetCanName()


__all__ = ["EasyPiper"]
