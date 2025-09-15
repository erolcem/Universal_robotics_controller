#!/usr/bin/env python3
"""
Complete Test: API Detection + Robot Movement
Tests the full pipeline from MIR position detection to UR robot movement
"""

import subprocess
import time
import signal
import sys
from pathlib import Path

def start_robot_control():
    """Start the robot control system"""
    print("🤖 Starting robot control system...")
    
    cmd = ["python3", "unified_robot_control_simple.py", "--robot-ip", "192.168.1.6", "--mir-ip", "offline"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Give it time to start
    time.sleep(3)
    
    if process.poll() is None:
        print("✅ Robot control system started")
        return process
    else:
        stdout, stderr = process.communicate()
        print(f"❌ Robot control failed to start: {stderr}")
        return None

def test_robot_movement():
    """Test basic robot movement"""
    print("\n🧪 Testing robot movement...")
    
    # Clear old commands
    control_dir = Path("control")
    control_dir.mkdir(exist_ok=True)
    
    command_file = control_dir / "robot_commands.txt"
    with open(command_file, "w") as f:
        f.write("add home 0.05\n")
    
    print("📤 Sent 'home' command")
    print("⏳ Wait 10 seconds to see if robot moves...")
    
    for i in range(10, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    print("✅ Movement test complete")

def test_p_start_sequence():
    """Test P_start sequence"""
    print("\n🎯 Testing P_start sequence (pickup + compact)...")
    
    control_dir = Path("control")
    command_file = control_dir / "robot_commands.txt"
    
    with open(command_file, "a") as f:
        f.write("add pickup 0.1 true\n")
        f.write("add compact 0.1\n")
    
    print("📤 Sent P_start sequence:")
    print("   1. pickup (with MIR pause)")
    print("   2. compact (no MIR pause)")
    print("⏳ Wait 30 seconds for sequence...")
    
    for i in range(30, 0, -1):
        if i % 5 == 0:
            print(f"   {i}...")
        time.sleep(1)
    
    print("✅ P_start sequence test complete")

def cleanup(robot_process):
    """Clean up processes"""
    if robot_process and robot_process.poll() is None:
        print("\n🛑 Stopping robot control...")
        robot_process.terminate()
        robot_process.wait(timeout=5)
        print("✅ Robot control stopped")

def main():
    print("🧪 COMPLETE PIPELINE TEST")
    print("=" * 30)
    print("This will test:")
    print("  1. Robot control system startup")
    print("  2. Basic robot movement")
    print("  3. P_start sequence (pickup + compact)")
    
    robot_process = None
    
    try:
        # Start robot control
        robot_process = start_robot_control()
        if not robot_process:
            print("❌ Cannot continue without robot control")
            return
        
        # Test basic movement
        test_robot_movement()
        
        # Test P_start sequence
        test_p_start_sequence()
        
        print("\n🎉 PIPELINE TEST COMPLETE!")
        print("📋 If you saw robot movement, the system is working!")
        print("📋 You can now use the automation systems:")
        print("   - Manual: simple_mission_controller.py")
        print("   - File-based: file_auto_controller.py") 
        print("   - API-based: improved_auto_controller.py")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted")
    finally:
        cleanup(robot_process)

if __name__ == "__main__":
    main()