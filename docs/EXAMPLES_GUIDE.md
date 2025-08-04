# UR Robot Control Examples Guide

This document describes all the available examples for controlling your UR robot, including both delta-based and pose-based control methods.

## Overview

The `examples/` directory contains scripts and data files for different robot control patterns:

### Delta-Based Control (Relative Movement)
- Commands specify relative movements from current position
- Uses velocity commands for smooth, continuous motion
- Format: `{"dx": 0.05, "dy": 0.0, "dz": 0.0, "drx": 0.0, "dry": 0.0, "drz": 0.0}`

### Pose-Based Control (Absolute Positioning)
- Commands specify exact target positions in space
- Uses linear movement commands for point-to-point motion
- Format: `{"x": -0.135, "y": -0.635, "z": 0.200, "rx": 2.221, "ry": 2.221, "rz": 0.000}`

## Available Examples

### 1. Basic Example (`basic_example.py`)
**Purpose**: Simple connection test and basic movement
**Usage**: `python examples/basic_example.py --robot-type physical`
- Connects to robot
- Gets current pose
- Performs simple movements
- Good for testing robot connectivity

### 2. Synchronous Delta Control (`synchronous_control.py`)
**Purpose**: Execute delta commands sequentially with fixed timing
**Data File**: `synchronous_deltas.jsonl`
**Usage**: `python examples/synchronous_control.py --robot-type physical --responsiveness 1.0`
- Reads delta commands from JSONL file line by line
- Each command executed with fixed delay
- Good for pre-planned movement sequences

### 3. Asynchronous Delta Control (`asynchronous_control.py`)
**Purpose**: Stream delta commands continuously
**Data File**: `asynchronous_deltas.jsonl`
**Usage**: `python examples/asynchronous_control.py --robot-type physical --responsiveness 1.0`
- Monitors file for new commands
- Applies most recent command continuously
- Good for real-time control applications

### 4. Synchronous Pose Control (`synchronous_pose_control.py`) ⭐ NEW
**Purpose**: Execute absolute pose commands sequentially
**Data File**: `synchronous_poses.jsonl`
**Usage**: `python examples/synchronous_pose_control.py --robot-type physical --responsiveness 1.5`
- Moves robot to exact positions in sequence
- Each pose command executed with fixed delay
- Good for precise positioning tasks

### 5. Asynchronous Pose Control (`asynchronous_pose_control.py`) ⭐ NEW
**Purpose**: Stream absolute pose commands continuously
**Data File**: `asynchronous_poses.jsonl`
**Usage**: `python examples/asynchronous_pose_control.py --robot-type physical --responsiveness 2.0`
- Monitors file for new pose commands
- Moves to most recent target pose
- Good for dynamic positioning control

## Data File Formats

### Delta Commands (Relative Movement)
```jsonl
{"dx": -0.05, "dy": 0.00, "dz": 0.00}
{"dx": 0.05, "dy": 0.00, "dz": 0.00}
{"dx": 0.00, "dy": 0.05, "dz": 0.00}
```
- `dx`, `dy`, `dz`: Linear movement in meters
- `drx`, `dry`, `drz`: Rotational movement in radians
- Values are relative to current position

### Pose Commands (Absolute Position)
```jsonl
{"x": -0.135, "y": -0.635, "z": 0.200, "rx": 2.221, "ry": 2.221, "rz": 0.000}
{"x": -0.235, "y": -0.635, "z": 0.200, "rx": 2.221, "ry": 2.221, "rz": 0.000}
{"x": -0.235, "y": -0.535, "z": 0.200, "rx": 2.221, "ry": 2.221, "rz": 0.000}
```
- `x`, `y`, `z`: Absolute position in meters (robot base frame)
- `rx`, `ry`, `rz`: Absolute orientation in radians (axis-angle representation)
- Values are absolute positions in robot workspace

## Common Parameters

### Required for Physical Robot
```bash
--robot-type physical
```

### Optional Parameters
- `--config`: Path to configuration file (default: `config/robot_config.yaml`)
- `--robot-ip`: Robot IP address (default: from config file)
- `--speed`: Movement speed in m/s (default: 0.2)
- `--acceleration`: Acceleration in m/s² (default: 0.5)
- `--responsiveness`: Time between commands in seconds (varies by example)

## Robot Setup Requirements

### For Physical Robot (UR10e)
1. **Network Connection**: Robot at IP 192.168.1.5, computer at 192.168.1.155
2. **Robot Mode**: Set to "Remote" mode on teach pendant
3. **External Control**: URCap auto-starts when script connects
4. **Safety**: Robot should be in safe working area

### Pre-execution Checklist
1. ✅ Robot in Remote mode
2. ✅ Network connectivity confirmed
3. ✅ Safety area clear
4. ✅ Emergency stop accessible

## Example Movement Patterns

### Synchronous Poses Pattern
The `synchronous_poses.jsonl` creates a 3D rectangular path:
1. Corner 1: (-0.135, -0.635, 0.200)
2. Corner 2: (-0.235, -0.635, 0.200) → Move 10cm in -X
3. Corner 3: (-0.235, -0.535, 0.200) → Move 10cm in +Y  
4. Corner 4: (-0.135, -0.535, 0.200) → Move 10cm in +X
5. Level 2: Same pattern at Z=0.300 (10cm higher)
6. Center: (-0.185, -0.585, 0.250) → Move to center
7. Return: Back to starting corner

### Asynchronous Poses Pattern
The `asynchronous_poses.jsonl` creates a more complex path suitable for streaming:
- Larger set of waypoints (17 commands)
- Covers more workspace area
- Suitable for continuous streaming applications

## Safety Notes

⚠️ **Important Safety Reminders**:
- Always test with simulation first (`--robot-type simulation`)
- Keep emergency stop within reach
- Verify workspace limits in configuration
- Start with slower speeds and longer responsiveness times
- Monitor robot movement closely during operation

## Troubleshooting

### "RTDE control program is not running"
- Ensure robot is in Remote mode
- Check External Control URCap configuration
- Verify network connectivity
- Robot may need to be restarted in some cases

### Connection Issues
- Check IP addresses in configuration
- Verify robot network settings
- Ensure URCap is installed and configured

### Movement Issues
- Check safety limits in configuration
- Verify workspace boundaries
- Reduce speed/acceleration if movements are too aggressive
- Check pose values are within robot reach


Calling:
/home/erolc/Projects/ursim_pipeline/ur_venv/bin/python examples/synchronous_pose_control.py --robot-type physical --responsiveness 1.5


timeout 10s /home/erolc/Projects/ursim_pipeline/ur_venv/bin/python examples/asynchronous_pose_control.py --robot-type physical --responsiveness 2.0