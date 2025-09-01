#!/usr/bin/env python3
"""
UR Robot Tool I/O Gripper Test

Tests gripper control using Tool Digital Outputs (as identified from teach pendant).
Based on user confirmation that Tool Digital Output 0 and 1 control the gripper.
"""

import sys
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    import rtde_control
    import rtde_receive
    print("✅ ur_rtde library is available")
except ImportError:
    print("❌ ur_rtde library not found")
    sys.exit(1)

def test_tool_gripper_control(robot_ip: str = "192.168.1.6"):
    """Test gripper control using Tool Digital Outputs."""
    print(f"\n🤖 Testing Tool Digital Output Gripper Control")
    print("=" * 60)
    print("Based on teach pendant: Tool Digital Output 0 and 1 control gripper")
    
    try:
        # Connect to robot
        print("🔌 Connecting to robot...")
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        if not (rtde_c.isConnected() and rtde_r.isConnected()):
            print("❌ Connection failed")
            return False
        
        print("✅ Connected successfully!")
        
        # Test Tool Digital Output commands
        print("\n🧪 Testing Tool Digital Output Commands:")
        
        # Method 1: set_tool_digital_out() - This is the correct command for tool I/O
        print("\n1️⃣ Testing set_tool_digital_out() commands:")
        
        try:
            # Open gripper (assuming pin 0 controls open/close)
            print("  🔓 Opening gripper (Tool Digital Output 0 = True)...")
            script_open = "set_tool_digital_out(0, True)"
            result = rtde_c.sendCustomScript(script_open)
            print(f"     Result: {result}")
            time.sleep(2)
            
            # Close gripper
            print("  🔒 Closing gripper (Tool Digital Output 0 = False)...")
            script_close = "set_tool_digital_out(0, False)"
            result = rtde_c.sendCustomScript(script_close)
            print(f"     Result: {result}")
            time.sleep(2)
            
            # Test second pin if needed
            print("  🔧 Testing Tool Digital Output 1...")
            script_pin1_on = "set_tool_digital_out(1, True)"
            result = rtde_c.sendCustomScript(script_pin1_on)
            print(f"     Pin 1 ON Result: {result}")
            time.sleep(1)
            
            script_pin1_off = "set_tool_digital_out(1, False)"
            result = rtde_c.sendCustomScript(script_pin1_off)
            print(f"     Pin 1 OFF Result: {result}")
            time.sleep(1)
            
        except Exception as e:
            print(f"     ❌ Tool digital output test failed: {e}")
        
        # Test reading tool digital inputs (if available)
        print("\n2️⃣ Testing Tool Digital Input Reading:")
        try:
            for pin in range(2):
                script_read = f"global tool_input_{pin} = get_tool_digital_in({pin})"
                result = rtde_c.sendCustomScript(script_read)
                print(f"  📍 Tool Digital Input {pin} read command sent: {result}")
        except Exception as e:
            print(f"     ❌ Tool digital input test failed: {e}")
        
        # Test combined gripper function
        print("\n3️⃣ Testing Complete Gripper Sequence:")
        try:
            print("  🎬 Running gripper open-close-open sequence...")
            
            # Open
            print("     Step 1: Open gripper")
            rtde_c.sendCustomScript("set_tool_digital_out(0, True)")
            time.sleep(1.5)
            
            # Close  
            print("     Step 2: Close gripper")
            rtde_c.sendCustomScript("set_tool_digital_out(0, False)")
            time.sleep(1.5)
            
            # Open again
            print("     Step 3: Open gripper again")
            rtde_c.sendCustomScript("set_tool_digital_out(0, True)")
            time.sleep(1)
            
            print("  ✅ Gripper sequence completed!")
            
        except Exception as e:
            print(f"     ❌ Gripper sequence failed: {e}")
        
        # Clean up
        rtde_c.disconnect()
        rtde_r.disconnect()
        print("\n✅ Tool I/O test complete!")
        return True
        
    except Exception as e:
        print(f"❌ Tool I/O test failed: {e}")
        return False

def test_different_gripper_patterns():
    """Test different gripper control patterns based on common configurations."""
    print(f"\n🔍 Testing Different Gripper Control Patterns")
    print("=" * 60)
    
    patterns = [
        {"name": "Pattern A: Pin 0 True=Open, False=Close", "pin": 0, "open_state": True, "close_state": False},
        {"name": "Pattern B: Pin 0 False=Open, True=Close", "pin": 0, "open_state": False, "close_state": True},
        {"name": "Pattern C: Pin 1 True=Open, False=Close", "pin": 1, "open_state": True, "close_state": False},
        {"name": "Pattern D: Pin 1 False=Open, True=Close", "pin": 1, "open_state": False, "close_state": True},
    ]
    
    robot_ip = "192.168.1.6"
    
    try:
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        
        if not rtde_c.isConnected():
            print("❌ Connection failed")
            return
        
        print("✅ Connected for pattern testing")
        
        for i, pattern in enumerate(patterns, 1):
            print(f"\n{i}️⃣ Testing {pattern['name']}")
            
            try:
                # Open
                print(f"   🔓 Open: set_tool_digital_out({pattern['pin']}, {pattern['open_state']})")
                script = f"set_tool_digital_out({pattern['pin']}, {pattern['open_state']})"
                result = rtde_c.sendCustomScript(script)
                print(f"      Result: {result}")
                time.sleep(1.5)
                
                # Close
                print(f"   🔒 Close: set_tool_digital_out({pattern['pin']}, {pattern['close_state']})")
                script = f"set_tool_digital_out({pattern['pin']}, {pattern['close_state']})"
                result = rtde_c.sendCustomScript(script)
                print(f"      Result: {result}")
                time.sleep(1.5)
                
                print(f"   ✅ Pattern {i} completed")
                
            except Exception as e:
                print(f"   ❌ Pattern {i} failed: {e}")
        
        rtde_c.disconnect()
        print("\n✅ Pattern testing complete!")
        
    except Exception as e:
        print(f"❌ Pattern testing failed: {e}")

if __name__ == "__main__":
    print("🤖 UR Robot Tool I/O Gripper Test")
    print("=" * 60)
    
    # Test basic tool I/O
    success = test_tool_gripper_control()
    
    if success:
        # Ask if user wants to test different patterns
        print("\n" + "="*60)
        response = input("❓ Test different gripper control patterns? (y/n): ").strip().lower()
        if response == 'y':
            test_different_gripper_patterns()
    
    print("\n🎯 Key Findings:")
    print("   ✅ Use set_tool_digital_out() instead of set_digital_out()")
    print("   ✅ Tool Digital Outputs 0 and 1 control gripper")
    print("   ✅ Test different pin/state combinations to find correct pattern")
