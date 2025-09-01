#!/usr/bin/env python3
"""
Manual Mode Gripper Test - Works even in manual/freedrive mode
"""

import rtde_receive
import time

def test_gripper_manual_mode():
    """Test gripper without requiring AUTO mode"""
    print("🤖 Manual Mode Gripper Test")
    print("=" * 35)
    
    robot_ip = "192.168.1.6"
    
    try:
        # Use only receive interface - this works in any mode
        print("🔍 Connecting for monitoring...")
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        robot_mode = rtde_r.getRobotMode()
        print(f"   Robot mode: {robot_mode} (Manual mode is OK)")
        
        print("\n📊 Current I/O state:")
        
        # Monitor digital outputs
        digital_bits = rtde_r.getDigitalOutBits()
        print(f"   All digital output bits: {digital_bits}")
        
        # Check specific outputs
        try:
            # These might work depending on ur_rtde version
            out_0 = rtde_r.getDigitalOut(0)
            out_1 = rtde_r.getDigitalOut(1)
            print(f"   Digital Output 0: {out_0}")
            print(f"   Digital Output 1: {out_1}")
        except:
            print("   (Cannot read individual outputs with this ur_rtde version)")
        
        rtde_r.disconnect()
        
        print("\n💡 Manual Gripper Control Options:")
        print("   1. Use the teach pendant I/O tab (you confirmed this works)")
        print("   2. Create a simple URScript program that controls gripper")
        print("   3. Put robot in AUTO mode for RTDE control")
        
        print("\n📝 Let's create a URScript program for you:")
        
        urscript_program = '''
# Simple gripper control program
def gripper_test():
    # Open gripper
    set_tool_digital_out(0, False)
    sleep(2)
    
    # Close gripper  
    set_tool_digital_out(0, True)
    sleep(2)
    
    # Open again
    set_tool_digital_out(0, False)
end

gripper_test()
'''
        
        print("🔧 URScript Program to Test Gripper:")
        print("=" * 40)
        print(urscript_program)
        print("=" * 40)
        
        print("\n📋 To use this:")
        print("   1. Go to 'Program' tab on teach pendant")
        print("   2. Create a new program")
        print("   3. Add 'Script' command")
        print("   4. Paste the URScript above")
        print("   5. Run the program")
        print("   6. Watch gripper open/close/open")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_gripper_manual_mode()
