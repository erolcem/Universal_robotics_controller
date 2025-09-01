#!/usr/bin/env python3
"""
UR Robot Diagnostic Script
Checks robot status and provides guidance for simulator setup.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    import rtde_receive
    import rtde_control
except ImportError:
    print("❌ ur_rtde library not found. Please run:")
    print("   source ur_venv/bin/activate")
    print("   pip install ur-rtde PyYAML")
    sys.exit(1)

def check_simulator_status():
    """Check simulator connection and status."""
    robot_ip = "127.0.0.1" # this is the robot IP in the simulator
    
    print("UR Robot Diagnostic Tool")
    print("=" * 40)
    
    try:
        print(f"Connecting to robot at {robot_ip}...")
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        if not rtde_r.isConnected():
            print("❌ Connection failed!")
            print("\n  Troubleshooting steps:")
            print("1. Is Docker simulator running? (./scripts/startDocker.sh)")
            print("2. Can you access http://localhost:6080/vnc.html ?")
            print("3. Try: docker ps | grep ursim")
            return False
            
        print("✅ Connection successful!")
        
        # Check robot status
        print("\n Robot Status:")
        print("-" * 20)
        
        # Robot mode
        robot_mode = rtde_r.getRobotMode()
        mode_names = {
            0: "ROBOT_MODE_DISCONNECTED",
            1: "ROBOT_MODE_CONFIRM_SAFETY",
            2: "ROBOT_MODE_BOOTING",
            3: "ROBOT_MODE_POWER_OFF",
            4: "ROBOT_MODE_POWER_ON",
            5: "ROBOT_MODE_IDLE",
            6: "ROBOT_MODE_BACKDRIVE",
            7: "ROBOT_MODE_RUNNING",
            8: "ROBOT_MODE_UPDATING_FIRMWARE"
        }
        print(f" Robot Mode: {mode_names.get(robot_mode, 'UNKNOWN')} ({robot_mode})")
        
        # Safety mode
        safety_mode = rtde_r.getSafetyMode()
        safety_names = {
            1: "NORMAL",
            2: "REDUCED",
            3: "PROTECTIVE_STOP",
            4: "RECOVERY",
            5: "SAFEGUARD_STOP",
            6: "SYSTEM_EMERGENCY_STOP",
            7: "ROBOT_EMERGENCY_STOP",
            8: "VIOLATION",
            9: "FAULT"
        }
        print(f"  Safety Mode: {safety_names.get(safety_mode, 'UNKNOWN')} ({safety_mode})")
        
        # Current pose
        pose = rtde_r.getActualTCPPose()
        print(f" TCP Pose: {[round(p, 3) for p in pose]}")
        
        # Try to get program state (different method names in different versions)
        try:
            program_running = rtde_r.isProgramRunning()
            print(f"▶️  Program Running: {program_running}")
        except AttributeError:
            try:
                # Alternative method name
                program_running = rtde_r.isRunning()
                print(f"▶️  Program Running: {program_running}")
            except AttributeError:
                print("▶️  Program Running: Unable to check (method not available)")
                program_running = None
        
        # Analysis and recommendations
        print("\n Analysis:")
        print("-" * 12)
        
        if robot_mode == 1:  # CONFIRM_SAFETY
            print("❗ Robot needs safety confirmation")
            print("   → In simulator: Press 'Confirm Safety Configuration'")
        elif robot_mode == 5:  # IDLE
            print("⚠️  Robot is idle - program not running")
            print("   → In simulator: Go to Program → Graphics → Turn ON simulation")
            print("   → Then: Move → Press 'ON' → Press 'START'")
        elif robot_mode == 7:  # RUNNING
            print("✅ Robot is ready for control!")
        else:
            print(f"⚠️  Robot in mode {robot_mode} - may need configuration")
            
        if safety_mode != 1:  # Not NORMAL
            print(f"⚠️  Safety mode is {safety_names.get(safety_mode, 'UNKNOWN')}")
            print("   → Check simulator safety panel")
            
        if not program_running and program_running is not None:
            print("⚠️  No program running - robot may not respond to commands")
            print("   → In simulator: Make sure to start the robot program")
            
        rtde_r.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n  Troubleshooting steps:")
        print("1. Start simulator: ./scripts/startDocker.sh")
        print("2. Wait for startup (30-60 seconds)")
        print("3. Open web interface: http://localhost:6080/vnc.html")
        print("4. Configure simulator as described in README")
        return False

if __name__ == "__main__":
    check_simulator_status()
