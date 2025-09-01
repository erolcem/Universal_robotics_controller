#!/usr/bin/env python3
"""
UR Robot I/O Diagnostic Tool

This script tests all available I/O methods to understand gripper control capabilities.
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
    print("❌ ur_rtde library not found. Please install with: pip install ur-rtde")
    sys.exit(1)

def test_digital_io_methods(robot_ip: str = "192.168.1.5"):
    """Test all available digital I/O methods."""
    print(f"\n🔍 Testing Digital I/O Methods on {robot_ip}")
    print("=" * 60)
    
    try:
        # Connect to robot
        print("🔌 Connecting to robot...")
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        if not rtde_c.isConnected():
            print("❌ RTDE Control connection failed")
            return False
        
        if not rtde_r.isConnected():
            print("❌ RTDE Receive connection failed")
            return False
        
        print("✅ Connected successfully!")
        
        # Test 1: Check available RTDE Control methods
        print("\n📋 Available RTDE Control Methods:")
        control_methods = [method for method in dir(rtde_c) if not method.startswith('_')]
        io_methods = [method for method in control_methods if 'digital' in method.lower() or 'analog' in method.lower()]
        
        if io_methods:
            for method in io_methods:
                print(f"  ✅ {method}")
        else:
            print("  ❌ No direct I/O methods found in RTDE Control")
        
        # Test 2: Check available RTDE Receive methods
        print("\n📋 Available RTDE Receive Methods:")
        receive_methods = [method for method in dir(rtde_r) if not method.startswith('_')]
        io_receive_methods = [method for method in receive_methods if 'digital' in method.lower() or 'analog' in method.lower()]
        
        if io_receive_methods:
            for method in io_receive_methods:
                print(f"  ✅ {method}")
        else:
            print("  ❌ No direct I/O methods found in RTDE Receive")
        
        # Test 3: Test sendCustomScript capability
        print("\n🧪 Testing sendCustomScript Method:")
        try:
            # Test simple script that should always work
            test_script = "popup('Test script executed successfully', 'Test', False, False, blocking=False)"
            result = rtde_c.sendCustomScript(test_script)
            print(f"  ✅ sendCustomScript available: {result}")
        except Exception as e:
            print(f"  ❌ sendCustomScript failed: {e}")
        
        # Test 4: Test reading digital inputs
        print("\n📥 Testing Digital Input Reading:")
        try:
            for pin in range(8):  # UR10e has 8 digital inputs
                try:
                    state = rtde_r.getDigitalInState(pin)
                    print(f"  📍 Digital Input {pin}: {state}")
                except Exception as e:
                    print(f"  ❌ Digital Input {pin}: {e}")
        except Exception as e:
            print(f"  ❌ Digital input reading failed: {e}")
        
        # Test 5: Test reading digital outputs (current state)
        print("\n📤 Testing Digital Output Reading:")
        try:
            # Try to read current digital output states
            outputs = rtde_r.getActualDigitalOutputBits()
            print(f"  📍 Digital Output Bits: {outputs}")
            
            # Try individual output states
            for pin in range(8):
                try:
                    state = rtde_r.getDigitalOutState(pin)
                    print(f"  📍 Digital Output {pin}: {state}")
                except Exception as e:
                    print(f"  ❌ Digital Output {pin}: {e}")
        except Exception as e:
            print(f"  ❌ Digital output reading failed: {e}")
        
        # Test 6: Test setting digital outputs (SAFE TEST)
        print("\n⚠️  Testing Digital Output Control (Safe Test):")
        print("    WARNING: This will briefly toggle digital outputs!")
        
        try:
            for pin in range(2):  # Only test first 2 pins for safety
                try:
                    # Get current state first
                    print(f"  🧪 Testing Digital Output {pin}...")
                    
                    # Turn on
                    script_on = f"set_digital_out({pin}, True)"
                    result_on = rtde_c.sendCustomScript(script_on)
                    print(f"    ↗️  Set HIGH: {result_on}")
                    time.sleep(0.5)
                    
                    # Check state after setting
                    try:
                        state_after_on = rtde_r.getDigitalOutState(pin)
                        print(f"    📍 State after HIGH: {state_after_on}")
                    except:
                        pass
                    
                    # Turn off
                    script_off = f"set_digital_out({pin}, False)"
                    result_off = rtde_c.sendCustomScript(script_off)
                    print(f"    ↘️  Set LOW: {result_off}")
                    time.sleep(0.5)
                    
                    # Check state after setting
                    try:
                        state_after_off = rtde_r.getDigitalOutState(pin)
                        print(f"    📍 State after LOW: {state_after_off}")
                    except:
                        pass
                    
                except Exception as e:
                    print(f"    ❌ Pin {pin} control failed: {e}")
        except Exception as e:
            print(f"  ❌ Digital output control test failed: {e}")
        
        # Test 7: Check robot configuration
        print("\n⚙️  Robot Configuration Info:")
        try:
            robot_mode = rtde_r.getRobotMode()
            safety_mode = rtde_r.getSafetyMode()
            print(f"  🤖 Robot Mode: {robot_mode}")
            print(f"  🛡️  Safety Mode: {safety_mode}")
        except Exception as e:
            print(f"  ❌ Configuration check failed: {e}")
        
        # Clean up
        rtde_c.disconnect()
        rtde_r.disconnect()
        print("\n✅ Diagnostic complete!")
        return True
        
    except Exception as e:
        print(f"❌ Diagnostic failed: {e}")
        return False

def test_gripper_simulation(robot_ip: str = "192.168.1.5"):
    """Test a complete gripper control simulation."""
    print(f"\n🤖 Testing Complete Gripper Control Simulation")
    print("=" * 60)
    
    try:
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        if not (rtde_c.isConnected() and rtde_r.isConnected()):
            print("❌ Connection failed")
            return False
        
        print("✅ Connected for gripper simulation")
        
        # Simulate gripper control sequence
        gripper_pin = 0  # Use digital output 0
        
        print(f"\n🦾 Gripper Control Sequence (Pin {gripper_pin}):")
        
        # Step 1: Open gripper
        print("  1️⃣  Opening gripper...")
        script_open = f"set_digital_out({gripper_pin}, False)"
        result = rtde_c.sendCustomScript(script_open)
        print(f"     Result: {result}")
        time.sleep(1)
        
        # Check state
        try:
            state = rtde_r.getDigitalOutState(gripper_pin)
            print(f"     State: {state} (should be False)")
        except Exception as e:
            print(f"     State check failed: {e}")
        
        # Step 2: Close gripper
        print("  2️⃣  Closing gripper...")
        script_close = f"set_digital_out({gripper_pin}, True)"
        result = rtde_c.sendCustomScript(script_close)
        print(f"     Result: {result}")
        time.sleep(1)
        
        # Check state
        try:
            state = rtde_r.getDigitalOutState(gripper_pin)
            print(f"     State: {state} (should be True)")
        except Exception as e:
            print(f"     State check failed: {e}")
        
        # Step 3: Open gripper again
        print("  3️⃣  Opening gripper again...")
        script_open = f"set_digital_out({gripper_pin}, False)"
        result = rtde_c.sendCustomScript(script_open)
        print(f"     Result: {result}")
        
        # Final state check
        try:
            state = rtde_r.getDigitalOutState(gripper_pin)
            print(f"     Final state: {state} (should be False)")
        except Exception as e:
            print(f"     Final state check failed: {e}")
        
        rtde_c.disconnect()
        rtde_r.disconnect()
        print("\n✅ Gripper simulation complete!")
        return True
        
    except Exception as e:
        print(f"❌ Gripper simulation failed: {e}")
        return False

def main():
    print("🔍 UR Robot I/O Diagnostic Tool")
    print("=" * 60)
    
    # Auto-detect robot IP from previous successful connections
    robot_ips = ["192.168.1.5", "192.168.1.6", "127.0.0.1"]
    
    robot_ip = None
    for test_ip in robot_ips:
        print(f"\n🔍 Testing connection to {test_ip}...")
        try:
            rtde_c = rtde_control.RTDEControlInterface(test_ip, timeout=2.0)
            if rtde_c.isConnected():
                print(f"✅ Found robot at {test_ip}")
                robot_ip = test_ip
                rtde_c.disconnect()
                break
            else:
                print(f"❌ No robot at {test_ip}")
        except:
            print(f"❌ Connection failed to {test_ip}")
    
    if not robot_ip:
        robot_ip = input("\nEnter robot IP manually: ").strip()
        if not robot_ip:
            print("❌ No robot IP provided")
            return 1
    
    print(f"\n🎯 Using robot IP: {robot_ip}")
    
    # Run comprehensive tests
    success = test_digital_io_methods(robot_ip)
    
    if success:
        # Ask user if they want to test gripper simulation
        response = input("\n❓ Test gripper control simulation? (y/n): ").strip().lower()
        if response == 'y':
            test_gripper_simulation(robot_ip)
    
    print("\n🎯 Diagnostic Summary:")
    print("   - Use getDigitalInState() to read inputs")
    print("   - Use getDigitalOutState() to read output states")
    print("   - Use sendCustomScript() with set_digital_out() to control outputs")
    print("   - Test with actual gripper hardware connected to verify functionality")
    print("\n💡 Next Steps:")
    print("   1. Connect gripper to digital output pin (typically pin 0)")
    print("   2. Test with actual gripper hardware")
    print("   3. Implement proper gripper control in your robot scripts")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
