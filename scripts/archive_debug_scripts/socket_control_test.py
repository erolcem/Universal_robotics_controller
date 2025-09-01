#!/usr/bin/env python3
"""
Socket-Based Robot Control - Uses sockets for both poses and gripper
Like remote_gripper_control.py but for everything
"""

import socket
import time

def send_urscript_command(robot_ip: str, script: str, port: int = 30002) -> bool:
    """Send URScript command via socket"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)
        
        sock.connect((robot_ip, port))
        sock.send((script + "\n").encode('utf-8'))
        sock.close()
        
        return True
    except Exception as e:
        print(f"❌ Socket command failed: {e}")
        return False

def test_socket_poses():
    """Test poses using socket URScript commands"""
    print("🎯 Socket-Based Pose Test")
    print("=" * 30)
    
    robot_ip = "192.168.1.6"
    
    # URScript for movement
    print("1️⃣ Moving UP 3cm...")
    move_up_script = """
movej(get_inverse_kin(pose_trans(get_forward_kin(), p[0, 0, 0.03, 0, 0, 0])), 1.0, 0.5)
"""
    result1 = send_urscript_command(robot_ip, move_up_script)
    print(f"   Command sent: {result1}")
    
    if result1:
        time.sleep(3)  # Wait for movement
        
        print("2️⃣ Moving back down...")
        move_down_script = """
movej(get_inverse_kin(pose_trans(get_forward_kin(), p[0, 0, -0.03, 0, 0, 0])), 1.0, 0.5)
"""
        result2 = send_urscript_command(robot_ip, move_down_script)
        print(f"   Command sent: {result2}")
        
        if result2:
            print("✅ Socket pose commands completed!")
            return True
    
    return False

def test_socket_gripper():
    """Test gripper using socket URScript commands"""
    print("🤏 Socket-Based Gripper Test") 
    print("=" * 35)
    
    robot_ip = "192.168.1.6"
    
    print("1️⃣ Opening gripper...")
    result1 = send_urscript_command(robot_ip, "set_tool_digital_out(0, False)")
    print(f"   Command sent: {result1}")
    
    if result1:
        time.sleep(2)
        
        print("2️⃣ Closing gripper...")
        result2 = send_urscript_command(robot_ip, "set_tool_digital_out(0, True)")
        print(f"   Command sent: {result2}")
        
        if result2:
            time.sleep(2)
            print("✅ Socket gripper commands completed!")
            return True
    
    return False

def test_socket_combined():
    """Test combined poses and gripper using socket"""
    print("🤖 Socket-Based Combined Test")
    print("=" * 35)
    
    robot_ip = "192.168.1.6"
    
    # Complete pick-and-place sequence via socket
    sequence = [
        ("Move down", "movej(get_inverse_kin(pose_trans(get_forward_kin(), p[0, 0, -0.05, 0, 0, 0])), 0.5, 0.3)"),
        ("Open gripper", "set_tool_digital_out(0, False)"),
        ("Close gripper", "set_tool_digital_out(0, True)"),
        ("Move up", "movej(get_inverse_kin(pose_trans(get_forward_kin(), p[0, 0, 0.05, 0, 0, 0])), 0.5, 0.3)"),
        ("Move right", "movej(get_inverse_kin(pose_trans(get_forward_kin(), p[0.1, 0, 0, 0, 0, 0])), 0.5, 0.3)"),
        ("Move down", "movej(get_inverse_kin(pose_trans(get_forward_kin(), p[0, 0, -0.05, 0, 0, 0])), 0.5, 0.3)"),
        ("Open gripper", "set_tool_digital_out(0, False)"),
        ("Move up", "movej(get_inverse_kin(pose_trans(get_forward_kin(), p[0, 0, 0.05, 0, 0, 0])), 0.5, 0.3)"),
        ("Move back", "movej(get_inverse_kin(pose_trans(get_forward_kin(), p[-0.1, 0, 0, 0, 0, 0])), 0.5, 0.3)"),
    ]
    
    for i, (name, script) in enumerate(sequence):
        print(f"{i+1}️⃣ {name}...")
        result = send_urscript_command(robot_ip, script)
        print(f"   Command sent: {result}")
        
        if not result:
            print(f"❌ Failed at step: {name}")
            return False
        
        # Wait between commands
        wait_time = 3 if "move" in name.lower() else 1
        time.sleep(wait_time)
    
    print("✅ Complete socket-based sequence completed!")
    return True

if __name__ == "__main__":
    print("🔬 Socket-Based Robot Control Test")
    print("=" * 40)
    
    print("\nWhich test?")
    print("1. Socket poses only")
    print("2. Socket gripper only")
    print("3. Socket combined sequence")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        test_socket_poses()
    elif choice == "2":
        test_socket_gripper()
    elif choice == "3":
        test_socket_combined()
    else:
        print("❌ Invalid choice")
