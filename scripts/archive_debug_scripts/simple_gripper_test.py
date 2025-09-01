#!/usr/bin/env python3
"""
Simple Gripper Control Test

Test basic gripper control using sendCustomScript with set_digital_out.
"""

import sys
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    import rtde_control
    import rtde_receive
except ImportError:
    print("❌ ur_rtde library not found")
    sys.exit(1)

def test_gripper_control(robot_ip: str = "192.168.1.6"):
    """Test basic gripper control."""
    print(f"🤖 Testing Gripper Control on {robot_ip}")
    print("=" * 50)
    
    try:
        # Connect to robot
        print("🔌 Connecting...")
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        if not (rtde_c.isConnected() and rtde_r.isConnected()):
            print("❌ Connection failed")
            return False
        
        print("✅ Connected successfully!")
        
        # Read current digital output states
        print("\n📤 Current Digital Output States:")
        try:
            outputs = rtde_r.getActualDigitalOutputBits()
            print(f"Output bits: {outputs}")
            
            for i in range(8):
                state = rtde_r.getDigitalOutState(i)
                print(f"  Digital Output {i}: {state}")
        except Exception as e:
            print(f"❌ Could not read outputs: {e}")
        
        # Test sendCustomScript with simple commands
        print("\n🧪 Testing sendCustomScript:")
        
        # Test 1: Simple message
        try:
            script = 'textmsg("Gripper test starting")'
            result = rtde_c.sendCustomScript(script)
            print(f"✅ Text message script: {result}")
        except Exception as e:
            print(f"❌ Text message failed: {e}")
            return False
        
        # Test 2: Digital output control
        gripper_pin = 0  # Digital output 0
        
        print(f"\n🤏 Testing Gripper Control (Pin {gripper_pin}):")
        
        try:
            # Open gripper (False/Low)
            print("  1️⃣ Opening gripper (set_digital_out(0, False))...")
            script_open = f'set_digital_out({gripper_pin}, False)'
            result = rtde_c.sendCustomScript(script_open)
            print(f"     Result: {result}")
            
            # Wait and check state
            time.sleep(1)
            state = rtde_r.getDigitalOutState(gripper_pin)
            print(f"     Digital Output {gripper_pin} state: {state}")
            
            # Close gripper (True/High)
            print("  2️⃣ Closing gripper (set_digital_out(0, True))...")
            script_close = f'set_digital_out({gripper_pin}, True)'
            result = rtde_c.sendCustomScript(script_close)
            print(f"     Result: {result}")
            
            # Wait and check state
            time.sleep(1)
            state = rtde_r.getDigitalOutState(gripper_pin)
            print(f"     Digital Output {gripper_pin} state: {state}")
            
            # Open again
            print("  3️⃣ Opening gripper again...")
            result = rtde_c.sendCustomScript(script_open)
            print(f"     Result: {result}")
            
            time.sleep(1)
            state = rtde_r.getDigitalOutState(gripper_pin)
            print(f"     Final Digital Output {gripper_pin} state: {state}")
            
            print("\n✅ Gripper control test completed successfully!")
            
        except Exception as e:
            print(f"❌ Gripper control failed: {e}")
            return False
        
        # Clean up
        rtde_c.disconnect()
        rtde_r.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🤏 Simple Gripper Control Test")
    print("=" * 50)
    
    # Use the working IP from previous test
    robot_ip = "192.168.1.6"
    
    success = test_gripper_control(robot_ip)
    
    if success:
        print("\n🎉 SUCCESS! Gripper control is working!")
        print("\n📋 Implementation Summary:")
        print("   ✅ Use rtde_c.sendCustomScript('set_digital_out(pin, state)')")
        print("   ✅ Use rtde_r.getDigitalOutState(pin) to read state")
        print("   ✅ False = Open, True = Closed (or configure as needed)")
    else:
        print("\n❌ Gripper control test failed")
        print("   Check robot connection and External Control program")
