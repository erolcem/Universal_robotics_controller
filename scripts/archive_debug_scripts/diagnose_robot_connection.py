#!/usr/bin/env python3
"""
UR Robot Connection Diagnostic Tool

This script helps diagnose connection issues with physical UR robots
and provides detailed information about what's needed for RTDE connections.
"""

import sys
import socket
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

try:
    import dashboard_client
    dashboard_available = True
    print("✅ Dashboard client is available")
except ImportError:
    dashboard_available = False
    print("⚠️  Dashboard client not available")


def check_network_connectivity(ip: str) -> dict:
    """Check basic network connectivity to robot."""
    print(f"\n🔍 Checking network connectivity to {ip}...")
    
    results = {
        'ping': False,
        'dashboard_port': False,
        'rtde_port': False,
        'interface_port': False
    }
    
    # Check common UR ports
    ports_to_check = {
        'dashboard_port': 29999,  # Dashboard server
        'rtde_port': 30004,       # RTDE
        'interface_port': 30002   # Interface port
    }
    
    for port_name, port in ports_to_check.items():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)
            result = sock.connect_ex((ip, port))
            sock.close()
            
            if result == 0:
                print(f"✅ Port {port} ({port_name}): Open")
                results[port_name] = True
            else:
                print(f"❌ Port {port} ({port_name}): Closed")
                results[port_name] = False
        except Exception as e:
            print(f"❌ Port {port} ({port_name}): Error - {e}")
            results[port_name] = False
    
    return results


def check_dashboard_connection(ip: str):
    """Check dashboard connection and get robot status."""
    if not dashboard_available:
        print("⚠️  Dashboard client not available, skipping dashboard checks")
        return None
        
    print(f"\n🔍 Checking dashboard connection to {ip}...")
    
    try:
        # Try to connect to dashboard
        dashboard = dashboard_client.DashboardClient(ip)
        dashboard.connect()
        
        print("✅ Dashboard connected successfully")
        
        # Get robot status
        try:
            robot_mode = dashboard.robotmode()
            print(f"📊 Robot mode: {robot_mode}")
            
            safety_status = dashboard.safetymode()
            print(f"🛡️  Safety status: {safety_status}")
            
            program_state = dashboard.programState()
            print(f"🔧 Program state: {program_state}")
            
            # Check if robot is ready for external control
            if "RUNNING" in robot_mode:
                print("✅ Robot is running - good for external control")
            else:
                print("⚠️  Robot is not in running mode")
                
        except Exception as e:
            print(f"⚠️  Could not get robot status: {e}")
        
        dashboard.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Dashboard connection failed: {e}")
        return False


def test_rtde_connection(ip: str, timeout: int = 10):
    """Test RTDE connection with different approaches."""
    print(f"\n🔍 Testing RTDE connection to {ip}...")
    
    # Test 1: Basic RTDE receive connection
    print("\n📡 Test 1: RTDE Receive Interface")
    try:
        rtde_r = rtde_receive.RTDEReceiveInterface(ip, 500.0)
        if rtde_r.isConnected():
            print("✅ RTDE Receive connected successfully")
            
            # Try to get basic data
            try:
                robot_mode = rtde_r.getRobotMode()
                safety_mode = rtde_r.getSafetyMode()
                print(f"📊 Robot mode: {robot_mode}")
                print(f"🛡️  Safety mode: {safety_mode}")
            except Exception as e:
                print(f"⚠️  Could not get robot data: {e}")
                
            rtde_r.disconnect()
        else:
            print("❌ RTDE Receive connection failed")
    except Exception as e:
        print(f"❌ RTDE Receive error: {e}")
    
    # Test 2: RTDE Control connection
    print("\n🎮 Test 2: RTDE Control Interface")
    try:
        print(f"⏱️  Attempting connection with {timeout}s timeout...")
        rtde_c = rtde_control.RTDEControlInterface(ip, 500.0, 
                                                  rtde_control.RTDEControlInterface.FLAG_VERBOSE)
        
        if rtde_c.isConnected():
            print("✅ RTDE Control connected successfully!")
            rtde_c.disconnect()
        else:
            print("❌ RTDE Control connection failed")
            print("💡 This usually means External Control program is not running")
            
    except Exception as e:
        print(f"❌ RTDE Control error: {e}")
        if "not running on controller" in str(e):
            print("\n❗ SOLUTION NEEDED:")
            print("   The robot needs an External Control program running!")
            print("   See instructions below.")


def print_setup_instructions():
    """Print detailed setup instructions."""
    print("""
🚀 SETUP INSTRUCTIONS FOR PHYSICAL UR ROBOT
==========================================

The error "RTDE control program is not running on controller" means you need to:

1. 📱 ON THE ROBOT TEACH PENDANT:
   
   Step 1: Check if External Control URCap is installed
   - Go to: Settings → System → URCaps
   - Look for "External Control" in the list
   - If not found, you need to install it first
   
   Step 2: Create an External Control Program
   - Go to "Program" tab
   - Click "+" to create new program
   - In the program tree, add: Structure → URCaps → External Control
   - Configure External Control node:
     * Host IP: Your computer's IP (e.g., 192.168.1.100)
     * Custom Port: 50002 (default)
   - Save the program
   
   Step 3: Run the External Control Program
   - Make sure robot is in "Manual" mode initially
   - Load and RUN the External Control program
   - Robot should switch to "Remote Control" mode
   - The pendant should show "External Control Active"

2. 🖥️  ON YOUR COMPUTER:
   
   - Make sure your computer and robot are on same network
   - Your computer's IP should match what you set in External Control
   - Run your Python script while External Control is active

3. 🔐 ALTERNATIVE (Dashboard Only):
   
   If you only need to read robot status (not control), you can use:
   - Dashboard client (no External Control needed)
   - This is read-only but can get robot position, status, etc.

4. 🛡️  SAFETY NOTES:
   
   - Physical robots can cause injury!
   - Keep emergency stop accessible
   - Start with slow movements
   - Test in controlled environment

💡 QUICK TEST:
Try running this diagnostic script again after setting up External Control.
""")


def main():
    """Main diagnostic function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="UR Robot Connection Diagnostic Tool")
    parser.add_argument("ip", help="Robot IP address to diagnose")
    parser.add_argument("--timeout", type=int, default=10, 
                       help="Connection timeout in seconds")
    
    args = parser.parse_args()
    
    print("🔍 UR Robot Connection Diagnostic Tool")
    print("=" * 40)
    print(f"Target robot: {args.ip}")
    
    # Run diagnostics
    network_results = check_network_connectivity(args.ip)
    dashboard_result = check_dashboard_connection(args.ip)
    test_rtde_connection(args.ip, args.timeout)
    
    # Summary
    print(f"\n📋 DIAGNOSTIC SUMMARY for {args.ip}")
    print("=" * 40)
    
    if network_results['dashboard_port']:
        print("✅ Basic network connectivity: OK")
    else:
        print("❌ Basic network connectivity: FAILED")
        print("   Check that robot is powered on and on same network")
        return 1
    
    if dashboard_result:
        print("✅ Dashboard connection: OK")
    else:
        print("❌ Dashboard connection: FAILED")
    
    if network_results['rtde_port']:
        print("✅ RTDE port accessible: OK")
    else:
        print("❌ RTDE port accessible: FAILED")
    
    print("\n🎯 NEXT STEPS:")
    if not network_results['dashboard_port']:
        print("1. Check network connection and robot power")
    elif not dashboard_result:
        print("1. Check robot network settings and firewall")
    else:
        print("1. Set up External Control program on robot (see instructions below)")
        print("2. Run External Control program on robot")
        print("3. Try your connection script again")
    
    print_setup_instructions()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
