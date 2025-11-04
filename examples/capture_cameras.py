#!/usr/bin/env python3
"""Capture images from ZED 2i (table_cam) and Orbbec (wrist_cam)"""
import cv2
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

# Open cameras
print("Opening cameras...")
orbbec = cv2.VideoCapture(4, cv2.CAP_V4L2)
zed2i = cv2.VideoCapture(6, cv2.CAP_V4L2)

# Configure
orbbec.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M','J','P','G'))
orbbec.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
orbbec.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
zed2i.set(cv2.CAP_PROP_FRAME_WIDTH, 2560)
zed2i.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Warmup
for _ in range(30):
    orbbec.read()
    zed2i.read()

# Capture
ret_orbbec, frame_orbbec = orbbec.read()
ret_zed, frame_zed = zed2i.read()

if ret_orbbec:
    cv2.imwrite(os.path.join(script_dir, 'wrist_cam.jpg'), frame_orbbec)
    print("Saved: wrist_cam.jpg")

if ret_zed:
    left_img = frame_zed[:, :1280]
    cv2.imwrite(os.path.join(script_dir, 'table_cam.jpg'), left_img)
    print("Saved: table_cam.jpg")

orbbec.release()
zed2i.release()
print("Done!")
