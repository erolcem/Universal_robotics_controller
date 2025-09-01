#!/usr/bin/env python3
"""
Direct RTDE Test - Mimics visual_test.py approach exactly
"""

import rtde_control
import rtde_receive
import time

def test_direct_rtde_poses():
    """Test poses using direct RTDE like visual_test.py"""
    print("🎯 Direct RTDE Pose Test (Like visual_test.py)")
    print("=" * 50)
    
    robot_ip = "192.168.1.6"
    
    try:
        # Connect exactly like visual_test.py
        print("🔌 Connecting...")
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        if not (rtde_c.isConnected() and rtde_r.isConnected()):
            print("❌ Connection failed!")
            return
            
        print("✅ Connected!")
        
        # Get initial pose (this works in visual_test.py)
        initial_pose = rtde_r.getActualTCPPose()
        print(f"📍 Starting pose: {[round(p, 3) for p in initial_pose]}")
        
        # Wait for user input like visual_test.py does
        input("Press Enter to test poses...")
        
        # Test simple movements
        print("\n1️⃣ Moving UP 3cm...")
        target1 = [initial_pose[0], initial_pose[1], initial_pose[2] + 0.03, 
                  initial_pose[3], initial_pose[4], initial_pose[5]]
        
        rtde_c.moveL(target1, 0.1, 0.5)  # Same as visual_test.py
        time.sleep(2)
        
        actual1 = rtde_r.getActualTCPPose()
        print(f"   Result: {[round(p, 3) for p in actual1]}")
        
        print("\n2️⃣ Moving back to start...")
        rtde_c.moveL(initial_pose, 0.1, 0.5)
        time.sleep(2)
        
        actual2 = rtde_r.getActualTCPPose()
        print(f"   Result: {[round(p, 3) for p in actual2]}")
        
        print("✅ Direct RTDE pose test completed!")
        
        rtde_c.disconnect()
        rtde_r.disconnect()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_direct_rtde_gripper():
    """Test gripper using direct RTDE"""
    print("🤏 Direct RTDE Gripper Test")
    print("=" * 35)
    
    robot_ip = "192.168.1.6"
    
    try:
        print("🔌 Connecting...")
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        
        if not rtde_c.isConnected():
            print("❌ Connection failed!")
            return
            
        print("✅ Connected!")
        
        input("Press Enter to test gripper...")
        
        print("\n1️⃣ Opening gripper...")
        result1 = rtde_c.sendCustomScript("set_tool_digital_out(0, False)")
        print(f"   Result: {result1}")
        time.sleep(2)
        
        print("\n2️⃣ Closing gripper...")
        result2 = rtde_c.sendCustomScript("set_tool_digital_out(0, True)")
        print(f"   Result: {result2}")
        time.sleep(2)
        
        print("✅ Direct RTDE gripper test completed!")
        
        rtde_c.disconnect()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_direct_rtde_combined():
    """Test poses and gripper together using direct RTDE"""
    print("🤖 Direct RTDE Combined Test")
    print("=" * 35)
    
    robot_ip = "192.168.1.6"
    
    try:
        print("🔌 Connecting...")
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        if not (rtde_c.isConnected() and rtde_r.isConnected()):
            print("❌ Connection failed!")
            return
            
        print("✅ Connected!")
        
        initial_pose = rtde_r.getActualTCPPose()
        print(f"📍 Starting pose: {[round(p, 3) for p in initial_pose]}")
        
        input("Press Enter to test combined movement...")
        
        print("\n1️⃣ Move down + open gripper...")
        target = [initial_pose[0], initial_pose[1], initial_pose[2] - 0.03, 
                 initial_pose[3], initial_pose[4], initial_pose[5]]
        
        # Move first
        rtde_c.moveL(target, 0.1, 0.5)
        time.sleep(1)
        
        # Then gripper
        rtde_c.sendCustomScript("set_tool_digital_out(0, False)")
        time.sleep(2)
        
        print("\n2️⃣ Close gripper + move up...")
        
        # Close gripper first
        rtde_c.sendCustomScript("set_tool_digital_out(0, True)")
        time.sleep(1)
        
        # Then move
        rtde_c.moveL(initial_pose, 0.1, 0.5)
        time.sleep(2)
        
        final_pose = rtde_r.getActualTCPPose()
        print(f"📍 Final pose: {[round(p, 3) for p in final_pose]}")
        
        print("✅ Combined test completed!")
        
        rtde_c.disconnect()
        rtde_r.disconnect()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    print("🔬 Direct RTDE Testing (Like visual_test.py)")
    print("=" * 50)
    
    print("\nWhich test?")
    print("1. Poses only")
    print("2. Gripper only") 
    print("3. Combined")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        test_direct_rtde_poses()
    elif choice == "2":
        test_direct_rtde_gripper()
    elif choice == "3":
        test_direct_rtde_combined()
    else:
        print("❌ Invalid choice")
