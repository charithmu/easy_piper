#!/usr/bin/env python3
"""
Quick Start Guide for Piper Recorder

This script demonstrates the complete workflow for collecting
imitation learning data with the Piper Recorder.

Run this to see example commands and workflow.
"""

print("""
╔══════════════════════════════════════════════════════════════════════╗
║                   Piper Recorder - Quick Start                       ║
║              Data Collection for Imitation Learning                  ║
╚══════════════════════════════════════════════════════════════════════╝

STEP 1: Install Dependencies
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pip install h5py numpy matplotlib

STEP 2: Start the Recorder
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Default CAN device (can0)
    piper-recorder
    
    # Specific CAN device
    piper-recorder --can-name can_piper
    
    # Custom output directory and FPS
    piper-recorder --output-dir ~/my_demos --fps 30

STEP 3: Interactive Recording Session
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Once started, you'll see:
    
    ══════════════════════════════════════════════════════════════════
    Piper Recorder - LeRobot Format Data Collection
    ══════════════════════════════════════════════════════════════════
    
    CAN Device: can0
    Output Directory: ./recordings
    Recording FPS: 30
    
    Connecting to Piper arm...
    ✓ Connected to Piper arm
    
    Checking data streaming...
    ✓ Data streaming OK - Joints: 50.0 Hz, Gripper: 50.0 Hz
    
    Current robot state:
      Joints (deg): [  0.00,   0.00,   0.00,   0.00,   0.00,   0.00]
      Gripper (mm):   0.00
    
    ══════════════════════════════════════════════════════════════════
    Ready to record! Type 'help' for available commands.
    ══════════════════════════════════════════════════════════════════
    
    > _

STEP 4: Available Commands
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    start <episode_name>  - Start recording a new episode
    stop                  - Stop and save current episode
    status                - Show recording status and robot state
    debug [duration]      - Monitor hardware streaming (default: 5s)
    help                  - Show available commands
    quit / exit           - Exit recorder

STEP 5: Debug Hardware Streaming (Recommended First!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Before recording, verify hardware is working properly:
    
    > debug 10
    ══════════════════════════════════════════════════════════════════
    DEBUG MODE - Hardware Streaming Monitor
    ══════════════════════════════════════════════════════════════════
    Duration: 10.0s | Update interval: 0.5s
    
    Monitoring... (move the robot to see values change)
    
    Time: 2.5s | Frames: 125
    
    Joints (SDK: 50.0 Hz, Actual: 50.2 Hz):
      J1:    0.12°  J2:  -15.34°  J3:   45.67°
      J4:    0.00°  J5:   30.21°  J6:    0.00°
    
    Gripper (SDK: 50.0 Hz, Actual: 50.1 Hz):
      Position:   15.23 mm
      Effort:      1.45 N·m
      Status:   enabled
    
    ✓ Data streaming looks good! Ready to record.
    
    The debug mode helps you:
    - Verify all hardware is working before recording
    - Check data rates are adequate (>10 Hz)
    - Confirm robot responds to movement
    - Catch any streaming issues early

STEP 6: Record Your First Episode
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Start recording
    > start pick_cube_demo_01
    ✓ Started recording episode: 'pick_cube_demo_01'
      Recording at 30 Hz (press 'stop' to finish)
    
    # The recorder shows live status:
    🔴 Recording: 'pick_cube_demo_01' | Frames: 245 | Duration: 8.2s | FPS: 29.9
    
    # NOW: Manually move the robot through the desired motion
    #      - Pick up the cube
    #      - Move to target location
    #      - Place the cube
    
    # Stop when done
    > stop
    Stopping recording... (245 frames recorded)
    ✓ Episode saved successfully!
      File: ./recordings/pick_cube_demo_01_20250103_143022.hdf5
      Frames: 245
      Duration: 8.17 seconds
      Actual FPS: 30.0

STEP 6: Record Multiple Demonstrations
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Record 10-50+ demonstrations of the same task:
    
    > start pick_cube_demo_02
    > stop
    
    > start pick_cube_demo_03
    > stop
    
    ... (repeat for more variations)
    
    > quit
    Exiting recorder. Goodbye!

STEP 7: Analyze Your Recordings
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # View episode information
    python3 load_recording_example.py recordings/pick_cube_demo_01_*.hdf5
    
    # Plot trajectories
    python3 load_recording_example.py recordings/pick_cube_demo_01_*.hdf5 --plot
    
    # Export to numpy for training
    python3 load_recording_example.py recordings/pick_cube_demo_01_*.hdf5 \\
        --export-numpy ./numpy_data

STEP 8: Use Data for Training
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # Load in Python
    import h5py
    
    with h5py.File('recordings/pick_cube_demo_01_*.hdf5', 'r') as f:
        observations = f['observation/state'][:]  # (N, 7)
        actions = f['action'][:]                  # (N, 7)
        timestamps = f['timestamp'][:]            # (N,)
    
    # Use with your imitation learning framework
    # (LeRobot, Diffusion Policy, ACT, etc.)

═══════════════════════════════════════════════════════════════════════

EPISODE NAMING BEST PRACTICES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Use descriptive, systematic names:

    task_variation_demo_number
    
Examples:
    ✓ pick_red_cube_demo_01
    ✓ pick_red_cube_demo_02
    ✓ pick_blue_cube_demo_01
    ✓ place_on_shelf_demo_01
    ✓ open_drawer_demo_01
    
    ✗ test1
    ✗ demo
    ✗ asdf

RECORDING TIPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. USE DEBUG MODE FIRST
   - Always run 'debug' before your first recording
   - Verify data streaming >10 Hz (ideally 50 Hz)
   - Check robot responds to manual movement
   
2. CHECK DATA STREAMING
   - Run 'status' or 'debug' to verify before recording
   - Expect joint data rate >10 Hz (typically 50 Hz)
   - Move robot during debug to see values change
   
3. SMOOTH MOVEMENTS
   - Perform smooth, deliberate motions
   - Avoid jerky or sudden movements
   - Maintain consistent speed
   
3. MULTIPLE DEMONSTRATIONS
   - Record 10-50+ demos per task for robust learning
   - Include variations (different approaches, speeds)
   - Record both success and near-success examples
   
4. EPISODE LENGTH
   - Keep episodes 5-30 seconds typical
   - Longer tasks: consider breaking into sub-tasks
   
5. DATA QUALITY
   - Check actual FPS matches target (shown in status)
   - Verify recording saves successfully
   - Review recordings with load_recording_example.py

TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Problem: "Joint data rate too low"
Solution: Check CAN connection, verify robot is powered on

Problem: Actual FPS much lower than target
Solution: Reduce target FPS with --fps 20, close other applications

Problem: Cannot save episode
Solution: Check disk space, try different --output-dir

Problem: All joints are zero
Solution: Move robot, check encoder feedback

═══════════════════════════════════════════════════════════════════════

NEXT STEPS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Read full documentation:
   → docs/PIPER_RECORDER_README.md

2. Try the recorder:
   → piper-recorder

3. Analyze recordings:
   → python3 load_recording_example.py <recording_file> --plot

4. Integrate with your learning framework:
   → LeRobot, Diffusion Policy, ACT, etc.

═══════════════════════════════════════════════════════════════════════
""")

if __name__ == '__main__':
    print("\n✓ Quick start guide displayed!")
    print("\nReady to start recording? Run:")
    print("    piper-recorder\n")
