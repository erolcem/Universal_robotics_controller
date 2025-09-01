#!/usr/bin/env python3
"""
Simple Movement Test - This is the script that WORKED!

This is the exact script that successfully moved the robot 1cm
and established the working connection.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    import rtde_control
    import rtde_receive
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def main():
    robot_ip = "192.168.1.5"
    
    print("🎯 Simple Movement Test - WORKING VERSION")
    print("=" * 45)
    print("This is the exact script that worked!")
    print()
    
    print("🔧 Make sure External Control is running on robot first!")
    input("Press Enter when External Control is active...")
    
    try:
        print("🔗 Connecting to robot...")
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        
        if rtde_c.isConnected():
            print("✅ Connected successfully!")
            
            # Get current position using receive interface
            rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
            current_pose = rtde_r.getActualTCPPose()
            print(f"📍 Current position: {[round(p, 3) for p in current_pose]}")
            
            # Move 1cm in X direction
            new_pose = current_pose.copy()
            new_pose[0] += 0.01  # +1cm in X
            
            print("➡️  Moving +1cm in X direction...")
            rtde_c.moveL(new_pose, 0.1, 0.3)  # speed=0.1, accel=0.3
            
            print("⬅️  Moving back to start...")
            rtde_c.moveL(current_pose, 0.1, 0.3)
            
            print("✅ Movement completed successfully!")
            
            rtde_r.disconnect()
            rtde_c.disconnect()
            
            print("🎉 SUCCESS! Robot control is working!")
            
        else:
            print("❌ Failed to connect")
            print("🔧 Check External Control is running")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
