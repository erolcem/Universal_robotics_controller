#!/usr/bin/env python3
"""
Tool I/O Discovery Script

Step-by-step testing to understand how Tool Digital Outputs work
"""

import sys
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    import rtde_control
    import rtde_receive
    print("✅ ur_rtde library loaded")
except ImportError:
    print("❌ ur_rtde library not found")
    sys.exit(1)

def test_tool_io_step_by_step(robot_ip: str = "192.168.1.6"):
    """Test tool I/O commands step by step"""
    print(f"\n🔧 Testing Tool I/O Commands on {robot_ip}")
    print("=" * 50)
    
    try:
        # Connect
        print("🔌 Connecting...")
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        if not (rtde_c.isConnected() and rtde_r.isConnected()):
            print("❌ Connection failed")
            return False
        
        print("✅ Connected successfully!")
        
        # Test 1: Check current tool I/O state
        print("\n📋 Step 1: Check current Tool I/O state")
        try:
            # Try to read tool digital inputs/outputs if available
            digital_outputs = rtde_r.getActualDigitalOutputBits()
            print(f"   All Digital Output Bits: {digital_outputs}")
            
            # Check individual tool digital outputs (if method exists)
            for pin in range(2):
                try:
                    # This might work for tool outputs
                    state = rtde_r.getDigitalOutState(pin)
                    print(f"   Tool Digital Output {pin}: {state}")
                except Exception as e:
                    print(f"   Tool Digital Output {pin}: Not readable ({e})")
        except Exception as e:
            print(f"   ❌ Could not read current state: {e}")
        
        # Test 2: Try different Tool I/O command variations
        print("\n🧪 Step 2: Testing Tool I/O command variations")
        
        commands_to_test = [
            # Standard tool commands
            ("set_tool_digital_out(0, True)", "Tool Digital Out 0 = True"),
            ("set_tool_digital_out(0, False)", "Tool Digital Out 0 = False"),
            ("set_tool_digital_out(1, True)", "Tool Digital Out 1 = True"), 
            ("set_tool_digital_out(1, False)", "Tool Digital Out 1 = False"),
            
            # Alternative command formats
            ("set_tool_output(0, 1)", "Tool Output 0 = 1"),
            ("set_tool_output(0, 0)", "Tool Output 0 = 0"),
            ("set_tool_output(1, 1)", "Tool Output 1 = 1"),
            ("set_tool_output(1, 0)", "Tool Output 1 = 0"),
            
            # Check if it's actually regular digital outputs with offset
            ("set_digital_out(8, True)", "Digital Out 8 = True (tool offset?)"),
            ("set_digital_out(8, False)", "Digital Out 8 = False"),
            ("set_digital_out(9, True)", "Digital Out 9 = True"),
            ("set_digital_out(9, False)", "Digital Out 9 = False"),
        ]
        
        for i, (command, description) in enumerate(commands_to_test):
            print(f"\n   Test {i+1}: {description}")
            print(f"   Command: {command}")
            
            try:
                result = rtde_c.sendCustomScript(command)
                print(f"   Result: {result}")
                
                if result:
                    print("   ✅ Command executed successfully!")
                    time.sleep(1)  # Wait to see effect
                    
                    # Ask user if they saw any effect
                    user_input = input("   ❓ Did you see the gripper move? (y/n/s=skip): ").strip().lower()
                    
                    if user_input == 'y':
                        print(f"   🎉 SUCCESS! '{command}' works!")
                        return command
                    elif user_input == 's':
                        print("   ⏭️  Skipping to next test...")
                        continue
                    else:
                        print("   ➡️  No movement detected, trying next...")
                else:
                    print("   ❌ Command failed to execute")
                    
            except Exception as e:
                print(f"   ❌ Command error: {e}")
        
        print("\n📝 Step 3: Manual verification")
        print("Since you can control it manually from the teach pendant:")
        print("1. Go to I/O tab on teach pendant")
        print("2. Find the working Tool Digital Output")
        print("3. Note the exact pin number and state that works")
        
        # Test 4: Try to read the URScript documentation approach
        print("\n📖 Step 4: Testing documentation-based commands")
        doc_commands = [
            "set_tool_digital_out(0, True)",
            "sleep(0.5)",
            "set_tool_digital_out(0, False)",
        ]
        
        full_script = "\n".join(doc_commands)
        print(f"   Testing full script:\n{full_script}")
        
        try:
            result = rtde_c.sendCustomScript(full_script)
            print(f"   Multi-line script result: {result}")
        except Exception as e:
            print(f"   Multi-line script error: {e}")
        
        rtde_c.disconnect()
        rtde_r.disconnect()
        return None
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return None

def manual_test_sequence(robot_ip: str = "192.168.1.6"):
    """Let user manually specify what command to test"""
    print(f"\n✏️  Manual Command Testing")
    print("=" * 50)
    
    try:
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        
        if not rtde_c.isConnected():
            print("❌ Connection failed")
            return
        
        print("✅ Connected - ready for manual testing")
        print("\nYou can now enter URScript commands to test.")
        print("Examples:")
        print("  set_tool_digital_out(0, True)")
        print("  set_tool_digital_out(0, False)")
        print("  set_digital_out(0, True)")
        print("Type 'quit' to exit")
        
        while True:
            command = input("\n🤖 Enter URScript command: ").strip()
            
            if command.lower() in ['quit', 'exit', 'q']:
                break
            
            if not command:
                continue
            
            try:
                print(f"   Executing: {command}")
                result = rtde_c.sendCustomScript(command)
                print(f"   Result: {result}")
                
                if result:
                    response = input("   Did you see any effect? (y/n): ").strip().lower()
                    if response == 'y':
                        print(f"   🎉 WORKING COMMAND: {command}")
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        rtde_c.disconnect()
        
    except Exception as e:
        print(f"❌ Manual test failed: {e}")

if __name__ == "__main__":
    print("🔧 Tool I/O Discovery Script")
    print("=" * 50)
    
    robot_ip = input("Enter robot IP (default: 192.168.1.6): ").strip()
    if not robot_ip:
        robot_ip = "192.168.1.6"
    
    print("\nChoose test mode:")
    print("1. Automatic step-by-step testing")
    print("2. Manual command testing")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "2":
        manual_test_sequence(robot_ip)
    else:
        working_command = test_tool_io_step_by_step(robot_ip)
        
        if working_command:
            print(f"\n🎯 DISCOVERY: Working command is '{working_command}'")
        else:
            print("\n🤔 No working command found in automatic test")
            print("Try manual testing mode to discover the right command")
