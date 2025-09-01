#!/usr/bin/env python3
"""
Test Pose vs Gripper Interference
Separate tests to isolate the issue
"""

import sys
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ur_controller import URRobotController

def test_poses_only():
    """Test poses without any gripper commands"""
    print("🎯 Test 1: Poses Only (No Gripper)")
    print("=" * 40)
    
    controller = URRobotController(
        config_path="config/robot_config.yaml",
        robot_type="physical"
    )
    
    try:
        if not controller.connect():
            print("❌ Connection failed")
            return
        
        print("✅ Connected for pose testing")
        
        # Get current position
        current = controller.get_current_pose()
        print(f"📍 Current pose: {[round(p, 3) for p in current]}")
        
        # Simple pose movements
        moves = [
            [current[0], current[1], current[2] + 0.05, current[3], current[4], current[5]],  # Up 5cm
            [current[0], current[1], current[2], current[3], current[4], current[5]],         # Back to start
        ]
        
        for i, pose in enumerate(moves):
            print(f"🎯 Move {i+1}: {[round(p, 3) for p in pose]}")
            result = controller.move_to_pose(pose, speed=0.1)
            print(f"   Result: {result}")
            time.sleep(1)
            
            # Check if we actually moved
            actual = controller.get_current_pose()
            print(f"   Actual: {[round(p, 3) for p in actual]}")
            print()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        controller.disconnect()

def test_gripper_only():
    """Test gripper without any pose commands"""
    print("🤏 Test 2: Gripper Only (No Poses)")
    print("=" * 40)
    
    controller = URRobotController(
        config_path="config/robot_config.yaml",
        robot_type="physical"
    )
    
    try:
        if not controller.connect():
            print("❌ Connection failed")
            return
        
        print("✅ Connected for gripper testing")
        
        # Simple gripper movements
        print("🔓 Opening gripper...")
        result1 = controller.set_gripper(0)
        print(f"   Result: {result1}")
        time.sleep(2)
        
        print("🔒 Closing gripper...")
        result2 = controller.set_gripper(1)
        print(f"   Result: {result2}")
        time.sleep(2)
        
        print("🔓 Opening gripper again...")
        result3 = controller.set_gripper(0)
        print(f"   Result: {result3}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        controller.disconnect()

def test_combined_carefully():
    """Test poses and gripper with careful timing"""
    print("🤖 Test 3: Combined with Careful Timing")
    print("=" * 45)
    
    controller = URRobotController(
        config_path="config/robot_config.yaml",
        robot_type="physical"
    )
    
    try:
        if not controller.connect():
            print("❌ Connection failed")
            return
        
        print("✅ Connected for combined testing")
        
        # Get current position
        current = controller.get_current_pose()
        print(f"📍 Starting pose: {[round(p, 3) for p in current]}")
        
        # Test sequence with longer delays
        print("\n1️⃣ First: Move pose only...")
        pose1 = [current[0], current[1], current[2] + 0.03, current[3], current[4], current[5]]
        result1 = controller.move_to_pose(pose1, speed=0.1)
        print(f"   Pose result: {result1}")
        time.sleep(3)  # Longer delay
        
        actual1 = controller.get_current_pose()
        print(f"   Actual pose: {[round(p, 3) for p in actual1]}")
        
        print("\n2️⃣ Second: Gripper only...")
        result2 = controller.set_gripper(1)
        print(f"   Gripper result: {result2}")
        time.sleep(3)  # Longer delay
        
        print("\n3️⃣ Third: Move pose again...")
        result3 = controller.move_to_pose(current, speed=0.1)
        print(f"   Pose result: {result3}")
        time.sleep(3)
        
        actual2 = controller.get_current_pose()
        print(f"   Actual pose: {[round(p, 3) for p in actual2]}")
        
        print("\n4️⃣ Fourth: Gripper again...")
        result4 = controller.set_gripper(0)
        print(f"   Gripper result: {result4}")
        
        print("\n📊 Results Summary:")
        print(f"   Move 1: {result1}")
        print(f"   Gripper 1: {result2}")
        print(f"   Move 2: {result3}")
        print(f"   Gripper 2: {result4}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        controller.disconnect()

if __name__ == "__main__":
    print("🔬 Pose vs Gripper Interference Analysis")
    print("=" * 50)
    
    print("\nWhich test would you like to run?")
    print("1. Poses only (no gripper)")
    print("2. Gripper only (no poses)")
    print("3. Combined with careful timing")
    print("4. All tests")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        test_poses_only()
    elif choice == "2":
        test_gripper_only()
    elif choice == "3":
        test_combined_carefully()
    elif choice == "4":
        test_poses_only()
        print("\n" + "="*50 + "\n")
        test_gripper_only()
        print("\n" + "="*50 + "\n")
        test_combined_carefully()
    else:
        print("❌ Invalid choice")
