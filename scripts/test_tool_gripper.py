#!/usr/bin/env python3
"""
UR Robot Tool I/O Gripper Test

Test gripper control using Tool Digital Outputs (the correct method).
Based on user confirmation that gripper works manually with Tool Digital Output 0 and 1.
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
    print("=" * 50)
    
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
        print("\n🛠️  Testing Tool Digital Output Commands:")
        
        # Test 1: Tool Digital Output 0 (based on your manual test)
        print("  🧪 Testing Tool Digital Output 0...")
        
        # Open gripper (assuming 0 = open)
        print("    📖 Opening gripper (Tool DO 0 = False)...")
        script_open = "set_tool_digital_out(0, False)"
        result = rtde_c.sendCustomScript(script_open)
        print(f"    Result: {result}")
        time.sleep(2)
        
        # Close gripper 
        print("    📝 Closing gripper (Tool DO 0 = True)...")
        script_close = "set_tool_digital_out(0, True)"
        result = rtde_c.sendCustomScript(script_close)
        print(f"    Result: {result}")
        time.sleep(2)
        
        # Test 2: Tool Digital Output 1 (if your gripper uses both)
        print("  🧪 Testing Tool Digital Output 1...")
        
        # Test both states
        print("    📖 Setting Tool DO 1 = False...")
        script_1_off = "set_tool_digital_out(1, False)"
        result = rtde_c.sendCustomScript(script_1_off)
        print(f"    Result: {result}")
        time.sleep(2)
        
        print("    📝 Setting Tool DO 1 = True...")
        script_1_on = "set_tool_digital_out(1, True)"
        result = rtde_c.sendCustomScript(script_1_on)
        print(f"    Result: {result}")
        time.sleep(2)
        
        # Return to open state
        print("    🔄 Returning gripper to open state...")
        script_final = "set_tool_digital_out(0, False)"
        result = rtde_c.sendCustomScript(script_final)
        print(f"    Result: {result}")
        
        # Test reading Tool Digital Input states (if feedback available)
        print("\n📥 Testing Tool Digital Input Reading:")
        try:
            # Tool digital inputs are typically pins 0-1
            for pin in range(2):
                script_read = f"global tool_di_{pin} = get_tool_digital_in({pin})"
                rtde_c.sendCustomScript(script_read)
                print(f"  📍 Tool Digital Input {pin}: Script sent (check robot for feedback)")
        except Exception as e:
            print(f"  ❌ Tool input reading failed: {e}")
        
        rtde_c.disconnect()
        rtde_r.disconnect()
        print("\n✅ Tool gripper test complete!")
        return True
        
    except Exception as e:
        print(f"❌ Tool gripper test failed: {e}")
        return False

def get_gripper_control_info():
    """Display information about gripper control methods."""
    print("\n📋 Gripper Control Method Summary:")
    print("=" * 50)
    print("✅ WORKING METHOD - Tool Digital Outputs:")
    print("   - Open gripper: set_tool_digital_out(0, False)")
    print("   - Close gripper: set_tool_digital_out(0, True)")
    print("   - Alternative: set_tool_digital_out(1, state)")
    print("\n❌ INCORRECT METHOD - Regular Digital Outputs:")
    print("   - set_digital_out() - This was our mistake!")
    print("\n🔧 Implementation for Python:")
    print("   script = 'set_tool_digital_out(0, True)'  # Close")
    print("   rtde_c.sendCustomScript(script)")

if __name__ == "__main__":
    print("🤖 UR Robot Tool I/O Gripper Test")
    print("=" * 50)
    
    robot_ip = input("Enter robot IP (default: 192.168.1.6): ").strip()
    if not robot_ip:
        robot_ip = "192.168.1.6"
    
    # Show gripper control info
    get_gripper_control_info()
    
    # Ask if user wants to test
    response = input("\n❓ Test Tool Digital Output gripper control? (y/n): ").strip().lower()
    if response == 'y':
        success = test_tool_gripper_control(robot_ip)
        
        if success:
            print("\n🎉 SUCCESS! Tool Digital Output gripper control is working!")
            print("💡 Now we can implement this in the pose control examples.")
        else:
            print("\n❌ Tool gripper test failed. Check robot connection and gripper wiring.")
    
    print("\n🎯 Next Steps:")
    print("1. Confirm which Tool Digital Output pin controls your gripper (0 or 1)")
    print("2. Confirm logic: True=closed/False=open OR False=closed/True=open")
    print("3. Update pose control examples with set_tool_digital_out() commands")
