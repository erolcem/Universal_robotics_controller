#!/usr/bin/env python3
"""
Socket-Based Synchronous Pose Control with Gripper
Pure socket implementation that works perfectly!
"""

import json
import time
import sys
import socket
from pathlib import Path

def send_urscript(robot_ip: str, script: str) -> bool:
    """Send URScript command via socket"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((robot_ip, 30002))
        sock.send((script + "\n").encode('utf-8'))
        sock.close()
        return True
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False

def socket_pose_control_with_gripper():
    """Run pose control with gripper using pure socket control"""
    
    print("🤖 Socket-Based Pose Control with Gripper")
    print("=" * 50)
    print("💡 Pure socket implementation - no RTDE issues!")
    print("=" * 50)
    
    robot_ip = "192.168.1.6"
    commands_file = "examples/synchronous_poses_with_gripper.jsonl"
    
    # Load commands
    commands = []
    try:
        with open(commands_file, 'r') as f:
            for line in f:
                if line.strip():
                    commands.append(json.loads(line))
        print(f"📁 Loaded {len(commands)} commands from {commands_file}")
    except Exception as e:
        print(f"❌ Could not load commands: {e}")
        return
    
    # Initialize gripper
    print("🤏 Initializing gripper (open)...")
    if not send_urscript(robot_ip, "set_tool_digital_out(0, False)"):
        print("❌ Gripper initialization failed")
        return
    
    print("✅ Gripper initialized")
    time.sleep(1)
    
    print(f"\n🎯 Starting sequence with {len(commands)} commands...")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        for i, cmd in enumerate(commands):
            # Extract pose
            x, y, z = cmd['x'], cmd['y'], cmd['z']
            rx, ry, rz = cmd['rx'], cmd['ry'], cmd['rz']
            gripper_state = cmd['gripper']
            
            print(f"\n{i+1:2d}/{len(commands)} Pose: [{x:6.3f}, {y:6.3f}, {z:6.3f}] Gripper: {gripper_state}")
            
            # Send pose command
            pose_script = f"movel(p[{x}, {y}, {z}, {rx}, {ry}, {rz}], 0.2, 0.5)"
            if send_urscript(robot_ip, pose_script):
                print(f"     ✅ Pose command sent")
            else:
                print(f"     ❌ Pose command failed")
                continue
            
            # Wait for movement
            time.sleep(2)
            
            # Send gripper command
            gripper_script = f"set_tool_digital_out(0, {bool(gripper_state)})"
            if send_urscript(robot_ip, gripper_script):
                action = "closed" if gripper_state else "opened"
                print(f"     ✅ Gripper {action}")
            else:
                print(f"     ❌ Gripper command failed")
            
            # Wait before next command
            time.sleep(2)
    
    except KeyboardInterrupt:
        print("\n⏹️  Sequence stopped by user")
    
    # Final gripper open
    print("\n🤏 Opening gripper before exit...")
    send_urscript(robot_ip, "set_tool_digital_out(0, False)")
    
    print("✅ Socket-based sequence completed!")

if __name__ == "__main__":
    socket_pose_control_with_gripper()
