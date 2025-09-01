#!/usr/bin/env python3
"""
Quick Robot Diagnostics
"""

import socket
import rtde_receive

def test_socket_connection(robot_ip="192.168.1.6"):
    """Test basic socket connection"""
    print("🔌 Testing socket connection...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((robot_ip, 30002))
        sock.send("# test\n".encode('utf-8'))
        sock.close()
        print("✅ Socket connection OK")
        return True
    except Exception as e:
        print(f"❌ Socket connection failed: {e}")
        return False

def test_robot_state(robot_ip="192.168.1.6"):
    """Test robot state via RTDE"""
    print("🤖 Checking robot state...")
    try:
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        robot_mode = rtde_r.getRobotMode()
        safety_mode = rtde_r.getSafetyMode()
        
        mode_names = {
            0: "NO_CONTROLLER", 1: "DISCONNECTED", 2: "CONFIRM_SAFETY",
            3: "BOOTING", 4: "POWER_OFF", 5: "POWER_ON", 6: "IDLE", 
            7: "BACKDRIVE", 8: "RUNNING", 9: "UPDATING_FIRMWARE"
        }
        
        safety_names = {
            1: "NORMAL", 2: "REDUCED", 3: "PROTECTIVE_STOP", 
            4: "RECOVERY", 5: "SAFEGUARD_STOP", 6: "SYSTEM_EMERGENCY_STOP",
            7: "ROBOT_EMERGENCY_STOP", 8: "VIOLATION", 9: "FAULT"
        }
        
        mode_name = mode_names.get(robot_mode, f"Unknown({robot_mode})")
        safety_name = safety_names.get(safety_mode, f"Unknown({safety_mode})")
        
        print(f"   Robot mode: {robot_mode} ({mode_name})")
        print(f"   Safety mode: {safety_mode} ({safety_name})")
        
        rtde_r.disconnect()
        
        # Check for problems
        if safety_mode == 3:
            print("⚠️  ROBOT IS IN PROTECTIVE STOP!")
            print("   Solution: Check teach pendant for errors, press 'Continue' if safe")
        elif safety_mode != 1:
            print(f"⚠️  Safety issue detected: {safety_name}")
        elif robot_mode == 4:
            print("⚠️  Robot is powered off!")
        elif robot_mode in [1, 2]:
            print("⚠️  Robot connection issue!")
        else:
            print("✅ Robot state looks normal")
        
        return True
        
    except Exception as e:
        print(f"❌ Cannot check robot state: {e}")
        return False

def test_simple_gripper(robot_ip="192.168.1.6"):
    """Test simple gripper command"""
    print("🤏 Testing gripper command...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        sock.connect((robot_ip, 30002))
        sock.send("set_tool_digital_out(0, False)\n".encode('utf-8'))
        sock.close()
        print("✅ Gripper command sent")
        return True
    except Exception as e:
        print(f"❌ Gripper command failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Robot Diagnostics")
    print("=" * 30)
    
    test_socket_connection()
    print()
    test_robot_state()
    print()
    test_simple_gripper()
    
    print("\n💡 Common solutions:")
    print("   1. Check teach pendant for error messages")
    print("   2. Press 'Continue' if robot is in protective stop")
    print("   3. Check if robot is still powered on")
    print("   4. Restart robot if necessary")
