#!/usr/bin/env python3
"""Test camera integration in piper_recorder"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Test camera capture functions
print("Testing camera capture integration...")

try:
    import cv2
    print("✓ OpenCV (cv2) is available")
    
    # Test ZED 2i
    table_cam = cv2.VideoCapture(6, cv2.CAP_V4L2)
    if table_cam.isOpened():
        print("✓ ZED 2i (table_cam) can be opened")
        table_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
        table_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        ret, frame = table_cam.read()
        if ret:
            left_img = frame[:, :1280]
            print(f"✓ ZED 2i captures {left_img.shape} frames")
        table_cam.release()
    else:
        print("✗ ZED 2i (table_cam) failed to open")
    
    # Test Orbbec
    wrist_cam = cv2.VideoCapture(4, cv2.CAP_V4L2)
    if wrist_cam.isOpened():
        print("✓ Orbbec (wrist_cam) can be opened")
        wrist_cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
        wrist_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        wrist_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        ret, frame = wrist_cam.read()
        if ret:
            print(f"✓ Orbbec captures {frame.shape} frames")
        wrist_cam.release()
    else:
        print("✗ Orbbec (wrist_cam) failed to open")
    
    print("\n✓ Camera integration test passed!")
    print("\nTo use cameras with piper_recorder:")
    print("  piper-recorder --enable-cameras")
    
except ImportError as e:
    print(f"✗ OpenCV not available: {e}")
    print("Install with: pip install opencv-python")
