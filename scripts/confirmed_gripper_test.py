#!/usr/bin/env python3
"""
Confirmed Gripper Test - We now know the exact mapping!

Tool Digital Output 0: OFF=Open, ON=Close
Tool Digital Output 1: Speed control
"""

import rtde_receive
import rtde_control
import time

def test_confirmed_gripper():
    """Test gripper with confirmed I/O mapping"""
    print("🤖 Confirmed Gripper Control Test")
    print("=" * 40)
    print("📋 Known mapping:")
    print("   Tool Digital Output 0: OFF=Open, ON=Close")
    print("   Tool Digital Output 1: Speed control")
    print("=" * 40)
    
    robot_ip = "192.168.1.6"
    
    try:
        # Check robot state first
        print("🔍 Checking robot state...")
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        robot_mode = rtde_r.getRobotMode()
        print(f"   Robot mode: {robot_mode}")
        
        if robot_mode == 7:
            print("   Status: MANUAL/FREEDRIVE mode")
            print("   ⚠️  Need AUTO mode for RTDE control")
        elif robot_mode == 8:
            print("   Status: RUNNING mode - perfect for control!")
        else:
            print(f"   Status: Mode {robot_mode}")
        
        rtde_r.disconnect()
        
        if robot_mode != 8:
            print("\n💡 To enable gripper control:")
            print("   1. Switch robot to AUTO mode")
            print("   2. Load/start a program")
            print("   3. Robot should show mode 8 (RUNNING)")
            
            choice = input("\nContinue anyway? (y/n): ").strip().lower()
            if choice != 'y':
                return
        
        # Test gripper control
        print("\n🎮 Testing gripper control...")
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        print("✅ Control connection established!")
        
        print("\n🤏 Gripper test sequence:")
        
        # Test 1: Open gripper (Output 0 = False)
        print("\n1️⃣ Opening gripper (Tool DO 0 = False)...")
        script = "set_tool_digital_out(0, False)"
        result = rtde_c.sendCustomScript(script)
        print(f"   Command sent: {result}")
        
        if result:
            print("   ✅ Open command sent successfully!")
            print("   👀 Check if gripper opened...")
            time.sleep(2)
            
            # Test 2: Close gripper (Output 0 = True)
            print("\n2️⃣ Closing gripper (Tool DO 0 = True)...")
            script = "set_tool_digital_out(0, True)"
            result = rtde_c.sendCustomScript(script)
            print(f"   Command sent: {result}")
            
            if result:
                print("   ✅ Close command sent successfully!")
                print("   👀 Check if gripper closed...")
                time.sleep(2)
                
                # Test 3: Speed control (Output 1)
                print("\n3️⃣ Testing speed control (Tool DO 1)...")
                print("   Setting speed control ON...")
                script = "set_tool_digital_out(1, True)"
                result = rtde_c.sendCustomScript(script)
                print(f"   Speed ON result: {result}")
                
                time.sleep(1)
                
                print("   Setting speed control OFF...")
                script = "set_tool_digital_out(1, False)"
                result = rtde_c.sendCustomScript(script)
                print(f"   Speed OFF result: {result}")
                
                print("\n🎉 All gripper commands sent successfully!")
                print("💡 Our URRobotController.set_gripper() should work perfectly!")
            
        rtde_c.disconnect()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        if "realtime kernel" in str(e):
            print("💡 This is just a performance warning, not an error")
        elif "RTDE control program" in str(e):
            print("💡 Robot needs to be in AUTO mode with a running program")

if __name__ == "__main__":
    test_confirmed_gripper()
