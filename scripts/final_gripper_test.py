#!/usr/bin/env python3
"""
Robot State and Simple Gripper Test
"""

import rtde_receive
import rtde_control
import time

def test_robot_and_gripper():
    """Test robot state and gripper control"""
    print("🤖 Robot State & Gripper Test")
    print("=" * 35)
    
    robot_ip = "192.168.1.6"
    
    try:
        # Check robot state
        print("🔍 Checking robot state...")
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        robot_mode = rtde_r.getRobotMode()
        safety_mode = rtde_r.getSafetyMode()
        
        print(f"   Robot mode: {robot_mode}")
        print(f"   Safety mode: {safety_mode}")
        
        # Robot mode explanations
        mode_names = {
            0: "NO_CONTROLLER",
            1: "DISCONNECTED", 
            2: "CONFIRM_SAFETY",
            3: "BOOTING",
            4: "POWER_OFF",
            5: "POWER_ON",
            6: "IDLE", 
            7: "BACKDRIVE",  # Manual/freedrive mode
            8: "RUNNING",
            9: "UPDATING_FIRMWARE"
        }
        
        mode_name = mode_names.get(robot_mode, f"Unknown({robot_mode})")
        print(f"   Mode name: {mode_name}")
        
        rtde_r.disconnect()
        
        # Robot mode 7 (BACKDRIVE) means manual mode - we need it in RUNNING mode
        if robot_mode == 7:
            print("\n⚠️  Robot is in MANUAL/FREEDRIVE mode")
            print("💡 To enable RTDE control:")
            print("   1. On teach pendant, switch to AUTO mode")
            print("   2. Load a program (even an empty one)")
            print("   3. Press PLAY")
            print("   4. Then try gripper control")
            
            choice = input("\nPress Enter to try gripper control anyway, or 'q' to quit: ")
            if choice.lower() == 'q':
                return
        
        # Try gripper control
        print("\n🎮 Attempting gripper control...")
        print("⚠️  Note: This might hang if robot isn't in RUNNING mode")
        
        # Try with timeout approach
        try:
            rtde_c = rtde_control.RTDEControlInterface(robot_ip)
            print("✅ Control connection established!")
            
            print("\n🤏 Testing gripper...")
            
            # Simple gripper test
            print("Opening gripper...")
            script = "set_tool_digital_out(0, False)"
            result = rtde_c.sendCustomScript(script)
            print(f"Open result: {result}")
            
            time.sleep(1)
            
            print("Closing gripper...")
            script = "set_tool_digital_out(0, True)"
            result = rtde_c.sendCustomScript(script)
            print(f"Close result: {result}")
            
            rtde_c.disconnect()
            print("✅ Gripper test completed!")
            
        except Exception as control_e:
            print(f"❌ Control failed: {control_e}")
            print("This is expected if robot is not in AUTO mode with a running program")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_robot_and_gripper()
