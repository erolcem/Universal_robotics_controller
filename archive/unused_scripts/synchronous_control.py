#!/usr/bin/env python3
"""
Synchronous Robot Control with Gripper
Socket-based implementation for reliable control
"""

import json
import time
import socket
import argparse
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

def run_synchronous_control(commands_file: str, robot_ip: str = "192.168.1.6", 
                          speed: float = 0.2, no_gripper: bool = False):
    """Run synchronous pose control with optional gripper"""
    
    print("🤖 Synchronous Robot Control")
    print("=" * 40)
    print(f"📁 Commands: {commands_file}")
    print(f"🏃 Speed: {speed} m/s")
    print(f"🤏 Gripper: {'Disabled' if no_gripper else 'Enabled'}")
    print("=" * 40)
    
    # Load commands
    commands = []
    try:
        with open(commands_file, 'r') as f:
            for line in f:
                if line.strip():
                    commands.append(json.loads(line))
        print(f"📋 Loaded {len(commands)} commands")
    except Exception as e:
        print(f"❌ Could not load commands: {e}")
        return False
    
    # Initialize gripper if enabled
    if not no_gripper:
        print("🤏 Initializing gripper (open)...")
        if not send_urscript(robot_ip, "set_tool_digital_out(0, False)"):
            print("⚠️  Gripper initialization failed - continuing anyway")
        time.sleep(1)
    
    print(f"\n🎯 Starting sequence...")
    print("Press Ctrl+C to stop")
    print("-" * 40)
    
    try:
        for i, cmd in enumerate(commands):
            # Extract pose
            x, y, z = cmd['x'], cmd['y'], cmd['z']
            rx, ry, rz = cmd['rx'], cmd['ry'], cmd['rz']
            
            gripper_info = ""
            if not no_gripper and 'gripper' in cmd:
                gripper_state = cmd['gripper']
                gripper_info = f" | Gripper: {gripper_state}"
            
            print(f"{i+1:2d}/{len(commands)} → [{x:6.3f}, {y:6.3f}, {z:6.3f}]{gripper_info}")
            
            # Send pose command
            pose_script = f"movel(p[{x}, {y}, {z}, {rx}, {ry}, {rz}], {speed}, 0.5)"
            if send_urscript(robot_ip, pose_script):
                print(f"         ✅ Pose sent")
            else:
                print(f"         ❌ Pose failed")
                continue
            
            # Wait for movement
            time.sleep(2)
            
            # Send gripper command if enabled
            if not no_gripper and 'gripper' in cmd:
                gripper_script = f"set_tool_digital_out(0, {bool(cmd['gripper'])})"
                if send_urscript(robot_ip, gripper_script):
                    action = "closed" if cmd['gripper'] else "opened"
                    print(f"         ✅ Gripper {action}")
                else:
                    print(f"         ❌ Gripper failed")
            
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n⏹️  Stopped by user")
    
    # Final cleanup
    if not no_gripper:
        print("\n🤏 Opening gripper...")
        send_urscript(robot_ip, "set_tool_digital_out(0, False)")
    
    print("✅ Sequence completed!")
    return True

def main():
    parser = argparse.ArgumentParser(description='Synchronous Robot Control')
    parser.add_argument('commands', nargs='?', 
                       default='synchronous_poses_with_gripper.jsonl',
                       help='Commands file (default: synchronous_poses_with_gripper.jsonl)')
    parser.add_argument('--ip', default='192.168.1.6', 
                       help='Robot IP address')
    parser.add_argument('--speed', type=float, default=0.2, 
                       help='Movement speed (m/s)')
    parser.add_argument('--no-gripper', action='store_true',
                       help='Disable gripper control')
    
    args = parser.parse_args()
    
    success = run_synchronous_control(
        commands_file=args.commands,
        robot_ip=args.ip,
        speed=args.speed,
        no_gripper=args.no_gripper
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
