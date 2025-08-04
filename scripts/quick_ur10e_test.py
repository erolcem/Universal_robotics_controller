#!/usr/bin/env python3
"""
Quick UR10e Test - Verify Working Setup

This is the minimal test that proved everything works.
Use this to quickly verify your robot connection.
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
    
    print("🎯 Quick UR10e Connection Test")
    print("=" * 30)
    print("🔧 Make sure External Control is running on robot!")
    print()
    
    try:
        # Test connection
        print("🔗 Connecting to robot...")
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        
        if rtde_c.isConnected():
            print("✅ Connected successfully!")
            
            # Get current position
            rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
            current_pose = rtde_r.getActualTCPPose()
            print(f"📍 TCP position: {[round(p, 3) for p in current_pose]}")
            
            # Test small movement
            response = input("\n🎯 Test 1cm movement? (y/N): ")
            if response.lower() == 'y':
                print("➡️  Moving +1cm in X...")
                new_pose = current_pose.copy()
                new_pose[0] += 0.01
                rtde_c.moveL(new_pose, 0.05, 0.1)
                
                print("⬅️  Returning to start...")
                rtde_c.moveL(current_pose, 0.05, 0.1)
                
                print("✅ Movement test complete!")
            
            rtde_r.disconnect()
            rtde_c.disconnect()
            
            print("\n🎉 SUCCESS! Robot is working properly!")
            
        else:
            print("❌ Connection failed")
            print("🔧 Check External Control is running")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
