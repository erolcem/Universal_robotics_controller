#!/usr/bin/env python3
"""
Simple Robot Movement Test
Basic test to see why robot won't move
"""

import socket
import time
import sys
from pathlib import Path

def send_urscript_with_response(robot_ip: str, command: str, timeout: float = 5.0):
    """Send URScript command and get response"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((robot_ip, 30002))
        sock.send((command + "\n").encode('utf-8'))
        
        # Wait a bit for response
        time.sleep(0.5)
        
        try:
            response = sock.recv(1024).decode('utf-8').strip()
        except:
            response = ""
            
        sock.close()
        return True, response
    except Exception as e:
        return False, str(e)

def test_robot_status(robot_ip: str = "192.168.1.6"):
    """Test basic robot status"""
    print("🔍 Basic Robot Status Check")
    print("=" * 30)
    
    # Check basic status
    status_commands = [
        ("Robot Mode", "get_robot_mode()"),
        ("Safety Mode", "get_safety_mode()"),
        ("TCP Position", "get_actual_tcp_pose()"),
        ("Joint Positions", "get_actual_joint_positions()"),
    ]
    
    for name, cmd in status_commands:
        success, response = send_urscript_with_response(robot_ip, cmd)
        if success:
            print(f"✅ {name}: {response if response else 'Command sent'}")
        else:
            print(f"❌ {name}: {response}")
        time.sleep(0.5)

def test_very_simple_movement(robot_ip: str = "192.168.1.6"):
    """Test the simplest possible movement"""
    print("\n🚀 Testing Very Simple Movement")
    print("=" * 30)
    
    # Get current position first
    print("📍 Getting current position...")
    success, pose_response = send_urscript_with_response(robot_ip, "get_actual_tcp_pose()")
    
    if not success:
        print("❌ Cannot get current position")
        return False
    
    print(f"📍 Current position response: {pose_response}")
    
    # Try a tiny movement - just 1mm up
    print("🔧 Attempting 1mm upward movement...")
    
    # Simple movement command with very slow speed
    move_cmd = "movel(p[get_actual_tcp_pose()[0], get_actual_tcp_pose()[1], get_actual_tcp_pose()[2] + 0.001, get_actual_tcp_pose()[3], get_actual_tcp_pose()[4], get_actual_tcp_pose()[5]], 0.01, 0.01)"
    
    success, response = send_urscript_with_response(robot_ip, move_cmd, timeout=10.0)
    
    if success:
        print(f"✅ Movement command sent: {response}")
        print("⏳ Waiting 3 seconds...")
        time.sleep(3)
        
        # Check if position changed
        success2, new_pose = send_urscript_with_response(robot_ip, "get_actual_tcp_pose()")
        if success2:
            print(f"📍 New position: {new_pose}")
        
        return True
    else:
        print(f"❌ Movement failed: {response}")
        return False

def test_robot_freedrive(robot_ip: str = "192.168.1.6"):
    """Test if robot is in freedrive mode"""
    print("\n🤖 Testing Robot Control Mode")
    print("=" * 30)
    
    # Try to disable freedrive if it's on
    commands = [
        ("End Freedrive", "end_freedrive_mode()"),
        ("Stop Script", "stop()"),
        ("Set Manual Mode", "set_robot_mode(7)"),  # RUNNING
    ]
    
    for name, cmd in commands:
        success, response = send_urscript_with_response(robot_ip, cmd)
        print(f"{'✅' if success else '❌'} {name}: {response}")
        time.sleep(1)

def main():
    robot_ip = "192.168.1.6"
    
    print("🛠️  Simple Robot Movement Test")
    print("=" * 40)
    
    # Test basic status
    test_robot_status(robot_ip)
    
    # Test freedrive mode
    test_robot_freedrive(robot_ip)
    
    # Test simple movement
    movement_success = test_very_simple_movement(robot_ip)
    
    if not movement_success:
        print("\n💡 The robot is not responding to movement commands.")
        print("🔧 Most likely causes:")
        print("   1. Robot is in Freedrive/Manual mode - check teach pendant")
        print("   2. A popup or safety message needs to be acknowledged")
        print("   3. Robot is not in 'Remote Control' mode")
        print("   4. A protective stop is active")
        print("   5. Robot program needs to be started on teach pendant")
        
        print("\n🎯 Quick fixes to try:")
        print("   1. On teach pendant: Go to Settings → System → Remote Control → Enable")
        print("   2. Press any 'OK' or 'Continue' buttons on teach pendant")
        print("   3. Check if 'Freedrive' button is pressed (should be OFF)")
        print("   4. Try starting a simple program on teach pendant first")
    else:
        print("\n✅ Robot movement test successful!")

if __name__ == "__main__":
    main()
