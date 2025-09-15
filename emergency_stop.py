#!/usr/bin/env python3
"""
EMERGENCY STOP AND RESET SYSTEM
Stops all automation and resets the system to a safe state
"""

import subprocess
import time
import requests
from pathlib import Path

def emergency_stop():
    """Emergency stop all systems"""
    print("🚨 EMERGENCY STOP - Stopping all systems")
    print("=" * 40)
    
    # 1. Stop all robot control processes
    print("🛑 Stopping robot control systems...")
    try:
        subprocess.run(["pkill", "-f", "unified_robot_control"], check=False)
        subprocess.run(["pkill", "-f", "integrated_mir"], check=False)
        subprocess.run(["pkill", "-f", "true_auto"], check=False)
        print("✅ Processes stopped")
    except Exception as e:
        print(f"⚠️ Process stop error: {e}")
    
    # 2. Clear command queue
    print("🧹 Clearing command queue...")
    try:
        control_dir = Path("control")
        control_dir.mkdir(exist_ok=True)
        command_file = control_dir / "robot_commands.txt"
        with open(command_file, "w") as f:
            f.write("# Commands cleared by emergency stop\n")
        print("✅ Command queue cleared")
    except Exception as e:
        print(f"⚠️ Command clear error: {e}")
    
    # 3. Check MIR status
    print("🔍 Checking MIR status...")
    try:
        response = requests.get('http://118.138.107.60/api/v2.0.0/status', timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"📊 MIR State: {status.get('state_text', 'unknown')}")
            print(f"📊 MIR Mission: {status.get('mission_text', 'none')}")
            print(f"📊 MIR Battery: {status.get('battery_percentage', 0):.1f}%")
            
            errors = status.get('errors', [])
            if errors:
                print(f"⚠️ MIR Errors: {errors}")
            else:
                print("✅ No MIR errors")
        else:
            print(f"❌ MIR connection failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ MIR check error: {e}")
    
    print("\n🎯 EMERGENCY STOP COMPLETE")
    print("=" * 30)
    print("📋 System Status:")
    print("   🤖 UR Robot: STOPPED")
    print("   🔍 Automation: STOPPED") 
    print("   📁 Command Queue: CLEARED")
    print("   🤖 MIR: Status checked above")
    
    print("\n💡 To restart safely:")
    print("1. Check MIR manually and clear any errors")
    print("2. Start robot control: python3 unified_robot_control_simple.py --robot-ip 192.168.1.6 --mir-ip offline")
    print("3. Test with manual commands first")
    print("4. Only then restart automation")

def safe_restart():
    """Provide safe restart instructions"""
    print("\n🔧 SAFE RESTART PROCEDURE")
    print("=" * 30)
    print("1. 🤖 Start UR Robot Control:")
    print("   python3 unified_robot_control_simple.py --robot-ip 192.168.1.6 --mir-ip offline")
    print()
    print("2. 🧪 Test UR Robot manually:")
    print("   echo 'add home 0.05' >> control/robot_commands.txt")
    print()
    print("3. 🔍 Check MIR manually:")
    print("   - Clear any MIR errors via the website")
    print("   - Ensure MIR is in a good position")
    print("   - Test MIR movement manually")
    print()
    print("4. 🚀 Only after everything works, restart automation:")
    print("   ./ur_venv/bin/python3 integrated_mir_ur_controller.py")
    print()
    print("⚠️ IMPORTANT: The loop issue was caused by repeated position detection.")
    print("   Make sure to test each step before proceeding!")

if __name__ == "__main__":
    emergency_stop()
    safe_restart()