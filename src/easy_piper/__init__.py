"""
EasyPiper - Pythonic wrapper for Piper robotic arm control

A simplified, user-friendly interface for controlling Piper robotic arms with
automatic CAN device setup, unit conversions, and comprehensive control capabilities.

Main Classes:
    EasyPiper: Main interface for robot control
    LeRobotDataRecorder: Record trajectories for imitation learning

Example:
    >>> from easy_piper import EasyPiper
    >>> arm = EasyPiper()
    >>> arm.enable()
    >>> arm.go_zero_joints()
"""

from .easy_piper import EasyPiper
from .piper_recorder import LeRobotDataRecorder

__version__ = "0.1.0"
__all__ = ["EasyPiper", "LeRobotDataRecorder"]
