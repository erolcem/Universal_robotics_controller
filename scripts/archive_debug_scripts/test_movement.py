#!/usr/bin/env python3
"""
Simple Robot Movement Test

This script tests basic robot movement with proper External Control.
"""

import sys
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    import rtde_control
    import rtde_receive
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_robot_movement():
    """Test basic robot movement."""
    robot_ip = "192.168.1.5"
    
    print("🤖 Simple Robot Movement Test")
    print("=" * 40)
    print(f"Connecting to robot at {robot_ip}...")
    
    # Connect to robot
    try:
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        if not rtde_c.isConnected():
            print("❌ RTDE Control not connected")
            print("   Make sure External Control is running on robot!")
            return False
            
        if not rtde_r.isConnected():
            print("❌ RTDE Receive not connected")
            return False
            
        print("✅ Connected to robot!")
        
        # Get current position
        current_pose = rtde_r.getActualTCPPose()
        print(f"📍 Current TCP pose: {[round(p, 3) for p in current_pose]}")
        
        # Check robot mode
        robot_mode = rtde_r.getRobotMode()
        safety_mode = rtde_r.getSafetyMode()
        print(f"🤖 Robot mode: {robot_mode}")
        print(f"🛡️  Safety mode: {safety_mode}")
        
        if robot_mode != 7:  # 7 = RUNNING
            print("⚠️  Robot is not in RUNNING mode")
            print("   Switch robot to Remote Control mode")
            return False
            
        # Test a very small movement
        print("\n🎯 Testing small movement...")
        print("   Moving 1cm in X direction...")
        
        # Calculate new pose (1cm = 0.01m in X)
        new_pose = current_pose.copy()
        new_pose[0] += 0.01  # Move 1cm in X
        
        print(f"📍 Target pose: {[round(p, 3) for p in new_pose]}")
        
        # Move robot
        success = rtde_c.moveL(new_pose, 0.05, 0.05)  # Very slow movement
        
        if success:
            print("✅ Movement command sent successfully!")
            
            # Wait for movement to complete
            print("⏳ Waiting for movement to complete...")
            time.sleep(3)
            
            # Check final position
            final_pose = rtde_r.getActualTCPPose()
            print(f"📍 Final pose: {[round(p, 3) for p in final_pose]}")
            
            # Check if robot moved
            distance_moved = abs(final_pose[0] - current_pose[0])
            if distance_moved > 0.005:  # 5mm tolerance
                print(f"🎉 SUCCESS! Robot moved {distance_moved*1000:.1f}mm")
                
                # Move back to original position
                print("🔄 Moving back to original position...")
                rtde_c.moveL(current_pose, 0.05, 0.05)
                time.sleep(3)
                print("✅ Returned to start position")
                
            else:
                print("❌ Robot did not move significantly")
                print(f"   Distance moved: {distance_moved*1000:.1f}mm")
                
        else:
            print("❌ Movement command failed")
            print("   Check robot safety systems and workspace limits")
            
        # Disconnect
        rtde_c.disconnect()
        rtde_r.disconnect()
        print("📡 Disconnected from robot")
        
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚨 SAFETY WARNING:")
    print("Make sure the robot workspace is clear!")
    print("Keep emergency stop accessible!")
    print()
    
    input("Press Enter when ready and External Control is running...")
    
    success = test_robot_movement()
    
    if success:
        print("\n🎉 Robot movement test completed!")
    else:
        print("\n❌ Robot movement test failed")
        print("Check that:")
        print("- External Control program is running")
        print("- Robot is in Remote Control mode")
        print("- Robot safety systems are OK")
        print("- No workspace violations")

if __name__ == "__main__":
    main()
