#!/usr/bin/env python3
"""
Quick Test Script - Verify UR Robot Controller Setup

This script performs basic checks to ensure everything is working correctly.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def main():
    print("🧪 UR Robot Controller - Quick Test")
    print("=" * 35)
    
    # Test 1: Library Import
    try:
        from ur_controller import URRobotController
        print("✅ Library import successful")
    except ImportError as e:
        print(f"❌ Library import failed: {e}")
        return 1
    
    # Test 2: ur_rtde availability
    try:
        import rtde_control
        import rtde_receive
        print("✅ ur_rtde library available")
    except ImportError:
        print("❌ ur_rtde library not found")
        return 1
    
    # Test 3: YAML support
    try:
        import yaml
        print("✅ PyYAML library available")
    except ImportError:
        print("⚠️  PyYAML not available (configuration files disabled)")
    
    # Test 4: Basic controller initialization
    try:
        controller = URRobotController(robot_ip="127.0.0.1", robot_type="simulation")
        print("✅ Controller initialization successful")
    except Exception as e:
        print(f"❌ Controller initialization failed: {e}")
        return 1
    
    # Test 5: Check if simulator is accessible (don't actually connect)
    print("\n🔍 Quick connection test...")
    try:
        # This will fail if simulator isn't configured, but we can catch the specific error
        if controller.connect():
            print("✅ Successfully connected to simulator!")
            pose = controller.get_tcp_pose()
            if pose:
                print(f"📍 Robot TCP pose: {[round(p, 3) for p in pose]}")
            controller.disconnect()
        else:
            print("ℹ️  Simulator not ready (normal - needs configuration via web interface)")
    except Exception as e:
        if "Connection refused" in str(e):
            print("ℹ️  Simulator not running or not accessible")
        elif "could not connect" in str(e).lower():
            print("ℹ️  Simulator running but needs configuration via web interface")
            print("   Go to: http://localhost:6080/vnc.html")
        else:
            print(f"ℹ️  Connection test: {e}")
    
    print("\n🎉 Setup verification complete!")
    print("\nNext steps:")
    print("1. Open simulator: http://localhost:6080/vnc.html")
    print("2. Configure robot (see README for details)")
    print("3. Run: python examples/basic_example.py")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
