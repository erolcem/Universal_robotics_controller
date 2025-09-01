#!/usr/bin/env python3
"""
Robot Mode Recovery Script
Fixes common robot mode issues like BACKDRIVE mode
"""

import socket
import time
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    import rtde_control
    import rtde_receive
except ImportError:
    print("❌ Please activate virtual environment: source ur_venv/bin/activate")
    sys.exit(1)

def send_urscript_command(robot_ip: str, command: str) -> bool:
    """Send URScript command via socket"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((robot_ip, 30002))
        sock.send((command + "\n").encode('utf-8'))
        sock.close()
        print(f"✅ Sent command: {command}")
        return True
    except Exception as e:
        print(f"❌ Socket error: {e}")
        return False

def check_robot_mode(robot_ip: str = "192.168.1.6"):
    """Check current robot mode"""
    print("🔍 Checking robot mode...")
    
    try:
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        robot_mode = rtde_r.getRobotMode()
        safety_mode = rtde_r.getSafetyMode()
        rtde_r.disconnect()
        
        mode_names = {
            -1: "NO_CONTROLLER",
            0: "DISCONNECTED", 
            1: "CONFIRM_SAFETY",
            2: "BOOTING",
            3: "POWER_OFF",
            4: "POWER_ON", 
            5: "IDLE",
            6: "BACKDRIVE",
            7: "RUNNING",
            8: "UPDATING_FIRMWARE"
        }
        
        safety_names = {
            1: "NORMAL",
            2: "REDUCED", 
            3: "PROTECTIVE_STOP",
            4: "RECOVERY",
            5: "SAFEGUARD_STOP",
            6: "SYSTEM_EMERGENCY_STOP",
            7: "ROBOT_EMERGENCY_STOP",
            8: "VIOLATION"
        }
        
        mode_name = mode_names.get(robot_mode, f"UNKNOWN({robot_mode})")
        safety_name = safety_names.get(safety_mode, f"UNKNOWN({safety_mode})")
        
        print(f"🤖 Robot Mode: {robot_mode} ({mode_name})")
        print(f"🛡️  Safety Mode: {safety_mode} ({safety_name})")
        
        return robot_mode, safety_mode
        
    except Exception as e:
        print(f"❌ Could not check robot mode: {e}")
        return None, None

def fix_backdrive_mode(robot_ip: str = "192.168.1.6"):
    """Fix robot stuck in BACKDRIVE mode"""
    print("\n🔧 Attempting to fix BACKDRIVE mode...")
    
    # Method 1: Send power on command
    print("📡 Sending power on command...")
    if send_urscript_command(robot_ip, "poweroff()"):
        time.sleep(2)
        if send_urscript_command(robot_ip, "poweron()"):
            print("⏳ Waiting for robot to power on...")
            time.sleep(5)
    
    # Method 2: Try to unlock protective stop
    print("🔓 Attempting to unlock protective stop...")
    send_urscript_command(robot_ip, "unlock_protective_stop()")
    time.sleep(1)
    
    # Method 3: Close safety popup and restart program
    print("🔄 Attempting to close popup and restart...")
    send_urscript_command(robot_ip, "close_safety_popup()")
    time.sleep(1)
    
    # Method 4: Try to set the robot to remote control mode
    print("📻 Setting remote control mode...")
    send_urscript_command(robot_ip, "set_robot_mode(7)")  # RUNNING mode
    time.sleep(2)

def test_movement(robot_ip: str = "192.168.1.6"):
    """Test if robot can move after recovery"""
    print("\n🎯 Testing robot movement...")
    
    try:
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        current_pose = rtde_r.getActualTCPPose()
        rtde_r.disconnect()
        
        if current_pose:
            print(f"📍 Current pose: {[round(p, 3) for p in current_pose]}")
            
            # Try a small movement
            test_pose = current_pose.copy()
            test_pose[2] += 0.01  # Move 1cm up in Z
            
            command = f"movel(p{test_pose}, 0.05, 0.1)"
            print(f"🚀 Testing small movement: {command}")
            
            if send_urscript_command(robot_ip, command):
                time.sleep(3)
                
                # Check if robot moved
                rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
                new_pose = rtde_r.getActualTCPPose()
                rtde_r.disconnect()
                
                if new_pose and abs(new_pose[2] - current_pose[2]) > 0.005:
                    print("✅ Robot movement successful!")
                    
                    # Move back to original position
                    command = f"movel(p{current_pose}, 0.05, 0.1)"
                    send_urscript_command(robot_ip, command)
                    print("🔄 Returned to original position")
                    return True
                else:
                    print("❌ Robot did not move as expected")
                    return False
        
    except Exception as e:
        print(f"❌ Movement test failed: {e}")
        return False

def main():
    robot_ip = "192.168.1.6"
    
    print("🛠️  Robot Recovery Tool")
    print("=" * 40)
    
    # Check current mode
    robot_mode, safety_mode = check_robot_mode(robot_ip)
    
    if robot_mode is None:
        print("❌ Cannot connect to robot. Check IP address and network connection.")
        return
    
    # If robot is in BACKDRIVE mode (6) or other problematic modes
    if robot_mode in [6]:  # BACKDRIVE
        print(f"\n⚠️  Robot is in BACKDRIVE mode - this prevents programmed movement!")
        print("💡 This usually happens when:")
        print("   - Someone manually moved the robot arm")
        print("   - Robot detected unexpected force/collision")
        print("   - Robot was put into manual mode")
        
        # Try to fix it
        fix_backdrive_mode(robot_ip)
        
        # Wait and check again
        print("\n⏳ Waiting for robot to recover...")
        time.sleep(3)
        
        robot_mode, safety_mode = check_robot_mode(robot_ip)
        
        if robot_mode == 7:  # RUNNING
            print("✅ Robot is now in RUNNING mode!")
            
            # Test movement
            if test_movement(robot_ip):
                print("\n🎉 Robot recovery successful!")
                print("💡 You can now use your robot control scripts again.")
            else:
                print("\n⚠️  Robot mode fixed but movement test failed.")
                print("💡 Try manually checking the teach pendant for any error messages.")
        else:
            mode_names = {6: "BACKDRIVE", 7: "RUNNING", 5: "IDLE", 4: "POWER_ON"}
            current_mode = mode_names.get(robot_mode, f"MODE_{robot_mode}")
            print(f"⚠️  Robot is still in {current_mode} mode.")
            print("💡 Manual intervention may be required:")
            print("   1. Check the teach pendant for error messages")
            print("   2. Press 'Continue' or 'OK' on any popups")
            print("   3. Ensure robot is in 'Remote Control' mode")
            print("   4. Check that robot is properly powered and initialized")
            
    elif robot_mode == 7:  # RUNNING
        print("✅ Robot is in RUNNING mode - should be able to move normally")
        
        # Test movement anyway
        if not test_movement(robot_ip):
            print("⚠️  Robot is in RUNNING mode but cannot move.")
            print("💡 Check:")
            print("   - Teach pendant for any active popups or messages")
            print("   - Robot is in 'Remote Control' mode")
            print("   - No protective stops are active")
            
    elif robot_mode == 5:  # IDLE
        print("⚠️  Robot is in IDLE mode")
        print("💡 Try sending a power on command...")
        send_urscript_command(robot_ip, "poweron()")
        time.sleep(3)
        check_robot_mode(robot_ip)
        
    else:
        mode_names = {
            1: "CONFIRM_SAFETY", 2: "BOOTING", 3: "POWER_OFF", 
            4: "POWER_ON", 5: "IDLE", 8: "UPDATING_FIRMWARE"
        }
        current_mode = mode_names.get(robot_mode, f"MODE_{robot_mode}")
        print(f"ℹ️  Robot is in {current_mode} mode")
        print("💡 This may be normal depending on robot state.")
    
    print("\n🔍 Additional Troubleshooting:")
    print("💡 If robot acknowledges commands but doesn't move:")
    print("   1. Check for concurrent ROS2/other robot control systems")
    print("   2. Toggle Remote Control OFF then ON on teach pendant")
    print("   3. Ensure only ONE control system is active at a time")
    print("   4. ROS2 UR drivers can interfere with direct socket control")
    print("   5. Always disconnect cleanly from previous control systems")

if __name__ == "__main__":
    main()
