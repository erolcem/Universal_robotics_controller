#!/usr/bin/env python3
"""
Quick Gripper Control Test - Checks robot state before attempting control
"""

import sys
import time
import rtde_control
import rtde_receive

def check_robot_ready():
    """Check if robot is ready for control commands"""
    print("🔍 Checking robot state...")
    
    robot_ip = "192.168.1.6"
    
    try:
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        robot_mode = rtde_r.getRobotMode()
        safety_mode = rtde_r.getSafetyMode()
        
        print(f"   Robot mode: {robot_mode}")
        print(f"   Safety mode: {safety_mode}")
        
        # Check tool outputs
        tool_out_0 = rtde_r.getToolDigitalOut(0)
        tool_out_1 = rtde_r.getToolDigitalOut(1)
        print(f"   Tool Digital Output 0: {tool_out_0}")
        print(f"   Tool Digital Output 1: {tool_out_1}")
        
        rtde_r.disconnect()
        
        # Robot mode codes:
        # 0: ROBOT_MODE_NO_CONTROLLER
        # 1: ROBOT_MODE_DISCONNECTED  
        # 2: ROBOT_MODE_CONFIRM_SAFETY
        # 3: ROBOT_MODE_BOOTING
        # 4: ROBOT_MODE_POWER_OFF
        # 5: ROBOT_MODE_POWER_ON
        # 6: ROBOT_MODE_IDLE
        # 7: ROBOT_MODE_BACKDRIVE
        # 8: ROBOT_MODE_RUNNING
        # 9: ROBOT_MODE_UPDATING_FIRMWARE
        
        if robot_mode == 8:  # RUNNING
            print("✅ Robot is RUNNING - ready for commands!")
            return True
        elif robot_mode == 6:  # IDLE
            print("⚠️  Robot is IDLE - may need to start a program")
            return False
        elif robot_mode == 5:  # POWER_ON
            print("⚠️  Robot is POWERED ON but not running")
            return False
        else:
            print(f"❌ Robot mode {robot_mode} not suitable for control")
            return False
            
    except Exception as e:
        print(f"❌ Cannot check robot state: {e}")
        return False

def quick_gripper_test():
    """Quick test of gripper control"""
    print("🤖 Quick Gripper Control Test")
    print("=" * 35)
    
    if not check_robot_ready():
        print("\n💡 To fix this:")
        print("   1. On the teach pendant, go to 'Program' tab")
        print("   2. Load or create a simple program")
        print("   3. Press 'Play' to start the program")
        print("   4. Try this test again")
        return
    
    robot_ip = "192.168.1.6"
    
    try:
        print("\n🎮 Connecting for control...")
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        print("✅ Control connection established!")
        
        print("\n🤏 Testing gripper control...")
        
        # Test open (False)
        print("1️⃣ Opening gripper...")
        script = "set_tool_digital_out(0, False)"
        result = rtde_c.sendCustomScript(script)
        print(f"   Command result: {result}")
        
        response = input("   Did gripper open? (y/n): ").strip().lower()
        if response == 'y':
            print("   ✅ Open works!")
            
            # Test close (True)
            print("\n2️⃣ Closing gripper...")
            script = "set_tool_digital_out(0, True)"
            result = rtde_c.sendCustomScript(script)
            print(f"   Command result: {result}")
            
            response2 = input("   Did gripper close? (y/n): ").strip().lower()
            if response2 == 'y':
                print("   ✅ Close works!")
                print("\n🎉 SUCCESS! Gripper control is working!")
            else:
                print("   ❌ Close didn't work")
        else:
            print("   ❌ Open didn't work")
            print("   🔄 Trying Tool Digital Output 1...")
            script = "set_tool_digital_out(1, False)"
            result = rtde_c.sendCustomScript(script)
            print(f"   Pin 1 result: {result}")
        
        rtde_c.disconnect()
        
    except Exception as e:
        print(f"❌ Control test failed: {e}")

if __name__ == "__main__":
    quick_gripper_test()
