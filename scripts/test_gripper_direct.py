#!/usr/bin/env python3
"""
Direct Gripper Test - Using known working Tool Digital Output
"""

import sys
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ur_controller import URRobotController

def test_gripper_directly():
    """Test gripper using our updated URRobotController"""
    print("🤖 Testing Gripper Control with URRobotController")
    print("=" * 50)
    
    # Initialize controller
    controller = URRobotController(
        config_path="config/robot_config.yaml",
        robot_type="physical"
    )
    
    try:
        print("🔌 Connecting to robot...")
        if not controller.connect():
            print("❌ Connection failed")
            return
        
        print("✅ Connected successfully!")
        
        # Test gripper control
        print("\n🤏 Testing gripper control...")
        
        print("1️⃣  Opening gripper (state=0)...")
        result1 = controller.set_gripper(0, pin=0)
        print(f"   Result: {result1}")
        
        if result1:
            print("   ✅ Open command sent successfully!")
            response1 = input("   ❓ Did you see the gripper open? (y/n): ").strip().lower()
            
            if response1 == 'y':
                print("   🎉 Gripper OPEN command works!")
                
                print("\n2️⃣  Closing gripper (state=1)...")
                result2 = controller.set_gripper(1, pin=0)
                print(f"   Result: {result2}")
                
                if result2:
                    response2 = input("   ❓ Did you see the gripper close? (y/n): ").strip().lower()
                    if response2 == 'y':
                        print("   🎉 Gripper CLOSE command works!")
                        print("\n✅ SUCCESS! Gripper control is fully functional!")
                    else:
                        print("   ❌ Close command didn't work")
                else:
                    print("   ❌ Close command failed to send")
            else:
                print("   ❌ Open command didn't work")
        else:
            print("   ❌ Open command failed to send")
        
        # Test different pins if pin 0 doesn't work
        if not result1:
            print("\n🔄 Trying Tool Digital Output pin 1...")
            result3 = controller.set_gripper(0, pin=1)
            print(f"   Pin 1 result: {result3}")
            
            if result3:
                response3 = input("   ❓ Did pin 1 work? (y/n): ").strip().lower()
                if response3 == 'y':
                    print("   🎉 Gripper works on Tool Digital Output 1!")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        print("\n🔌 Disconnecting...")
        controller.disconnect()
        print("✅ Test complete!")

if __name__ == "__main__":
    test_gripper_directly()
