#!/usr/bin/env python3
"""
Advanced Robot Diagnostics
More detailed checking for movement issues
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
        response = sock.recv(1024).decode('utf-8').strip()
        sock.close()
        print(f"✅ Command: {command}")
        if response:
            print(f"📝 Response: {response}")
        return True
    except Exception as e:
        print(f"❌ Socket error: {e}")
        return False

def detailed_robot_check(robot_ip: str = "192.168.1.6"):
    """Detailed robot status check"""
    print("🔍 Detailed Robot Diagnostics")
    print("=" * 40)
    
    try:
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        # Basic status
        robot_mode = rtde_r.getRobotMode()
        safety_mode = rtde_r.getSafetyMode()
        
        print(f"🤖 Robot Mode: {robot_mode}")
        print(f"🛡️  Safety Mode: {safety_mode}")
        
        # Check if robot is operational
        is_program_running = rtde_r.isProgramRunning()
        is_protective_stopped = rtde_r.isProtectiveStopped()
        is_emergency_stopped = rtde_r.isEmergencyStopped()
        
        print(f"🏃 Program Running: {is_program_running}")
        print(f"🛑 Protective Stop: {is_protective_stopped}")
        print(f"🚨 Emergency Stop: {is_emergency_stopped}")
        
        # Joint information
        joint_positions = rtde_r.getActualQ()
        joint_speeds = rtde_r.getActualQd()
        
        print(f"🔧 Joint Positions: {[round(j, 3) for j in joint_positions]}")
        print(f"⚡ Joint Speeds: {[round(j, 3) for j in joint_speeds]}")
        
        # TCP pose
        tcp_pose = rtde_r.getActualTCPPose()
        print(f"📍 TCP Pose: {[round(p, 3) for p in tcp_pose]}")
        
        rtde_r.disconnect()
        
        return {
            'robot_mode': robot_mode,
            'safety_mode': safety_mode,
            'program_running': is_program_running,
            'protective_stopped': is_protective_stopped,
            'emergency_stopped': is_emergency_stopped,
            'tcp_pose': tcp_pose
        }
        
    except Exception as e:
        print(f"❌ Diagnostic error: {e}")
        return None

def try_rtde_control(robot_ip: str = "192.168.1.6"):
    """Try using RTDE control interface"""
    print("\n🎮 Testing RTDE Control Interface")
    print("=" * 40)
    
    try:
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        
        # Get current pose
        current_pose = rtde_c.getActualTCPPose()
        print(f"📍 Current pose: {[round(p, 3) for p in current_pose]}")
        
        # Try a very small movement
        test_pose = current_pose.copy()
        test_pose[2] += 0.005  # Move 5mm up
        
        print(f"🚀 Attempting 5mm upward movement...")
        success = rtde_c.moveL(test_pose, 0.05, 0.1)
        
        if success:
            print("✅ RTDE movement command accepted")
            time.sleep(2)
            
            # Move back
            rtde_c.moveL(current_pose, 0.05, 0.1)
            print("🔄 Returned to original position")
        else:
            print("❌ RTDE movement command rejected")
            
        rtde_c.disconnect()
        return success
        
    except Exception as e:
        print(f"❌ RTDE control error: {e}")
        return False

def try_simple_urscript_commands(robot_ip: str = "192.168.1.6"):
    """Try very simple URScript commands"""
    print("\n📜 Testing Simple URScript Commands")
    print("=" * 40)
    
    # Try to get robot status via URScript
    commands = [
        "get_robot_mode()",
        "get_safety_mode()", 
        "is_protective_stopped()",
        "is_emergency_stopped()",
        "get_actual_tcp_pose()"
    ]
    
    for cmd in commands:
        send_urscript_command(robot_ip, cmd)
        time.sleep(0.5)

def try_force_remote_mode(robot_ip: str = "192.168.1.6"):
    """Try to force robot into remote control mode"""
    print("\n📡 Attempting to Force Remote Control Mode")
    print("=" * 40)
    
    commands = [
        "set_robot_mode(7)",  # RUNNING mode
        "close_popup()",      # Close any popups
        "clear_operational_mode()",  # Clear operational mode
        "set_operational_mode('manual')",  # Set manual mode first
        "set_operational_mode('automatic')"  # Then automatic mode
    ]
    
    for cmd in commands:
        send_urscript_command(robot_ip, cmd)
        time.sleep(1)

def main():
    robot_ip = "192.168.1.6"
    
    print("🔧 Advanced Robot Movement Diagnostics")
    print("=" * 50)
    
    # Detailed check
    status = detailed_robot_check(robot_ip)
    
    if not status:
        print("❌ Cannot get robot status")
        return
    
    # Try different movement methods
    if status['emergency_stopped']:
        print("\n🚨 EMERGENCY STOP ACTIVE!")
        print("💡 Release emergency stop button and restart robot")
        return
        
    if status['protective_stopped']:
        print("\n🛑 PROTECTIVE STOP ACTIVE!")
        print("💡 Check teach pendant and press 'Continue' if safe")
        
        # Try to unlock
        send_urscript_command(robot_ip, "unlock_protective_stop()")
        time.sleep(2)
    
    # Try to force remote mode
    try_force_remote_mode(robot_ip)
    time.sleep(2)
    
    # Try simple URScript commands
    try_simple_urscript_commands(robot_ip)
    
    # Try RTDE control
    rtde_success = try_rtde_control(robot_ip)
    
    if not rtde_success:
        print("\n💡 Troubleshooting Steps:")
        print("1. Check teach pendant for any popups or messages")
        print("2. Ensure robot is in 'Remote Control' mode on teach pendant")
        print("3. Check that no protective stops are active")
        print("4. Try manually moving robot arm slightly to clear any issues")
        print("5. Restart robot program on teach pendant")
        print("6. If all else fails, power cycle the robot")

if __name__ == "__main__":
    main()
