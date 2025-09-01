#!/usr/bin/env python3
"""
Remote Gripper Control - Just like pose control but for gripper
Uses socket connection to send URScript directly to robot
"""

import socket
import time
import sys
from pathlib import Path

def send_urscript_directly(robot_ip: str, script: str, port: int = 30002) -> bool:
    """
    Send URScript directly to robot via socket connection.
    This bypasses RTDE and works in any robot mode.
    """
    try:
        # Create socket connection to robot
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5.0)  # 5 second timeout
        
        print(f"🔌 Connecting to {robot_ip}:{port}...")
        sock.connect((robot_ip, port))
        print("✅ Connected!")
        
        # Send URScript command
        script_with_newline = script + "\n"
        sock.send(script_with_newline.encode('utf-8'))
        print(f"📤 Sent: {script}")
        
        # Close connection
        sock.close()
        print("✅ Command sent successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send command: {e}")
        return False

def control_gripper_remotely():
    """Control gripper remotely using direct socket connection"""
    print("🤖 Remote Gripper Control")
    print("=" * 30)
    print("💡 This works in ANY robot mode (Manual/Auto)!")
    print("=" * 30)
    
    robot_ip = "192.168.1.6"
    
    while True:
        print("\n🤏 Gripper Control Options:")
        print("1. Open gripper")
        print("2. Close gripper") 
        print("3. Test sequence (open → close → open)")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            print("\n🔓 Opening gripper...")
            script = "set_tool_digital_out(0, False)"
            if send_urscript_directly(robot_ip, script):
                print("✅ Gripper should be opening now!")
                
        elif choice == "2":
            print("\n🔒 Closing gripper...")
            script = "set_tool_digital_out(0, True)"
            if send_urscript_directly(robot_ip, script):
                print("✅ Gripper should be closing now!")
                
        elif choice == "3":
            print("\n🔄 Running test sequence...")
            
            # Open
            print("   1/3: Opening...")
            send_urscript_directly(robot_ip, "set_tool_digital_out(0, False)")
            time.sleep(2)
            
            # Close
            print("   2/3: Closing...")
            send_urscript_directly(robot_ip, "set_tool_digital_out(0, True)")
            time.sleep(2)
            
            # Open again
            print("   3/3: Opening again...")
            send_urscript_directly(robot_ip, "set_tool_digital_out(0, False)")
            
            print("✅ Test sequence complete!")
            
        elif choice == "4":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    control_gripper_remotely()
