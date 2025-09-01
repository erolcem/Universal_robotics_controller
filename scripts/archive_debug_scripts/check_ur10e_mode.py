#!/usr/bin/env python3
"""
Check UR10e Robot State and Mode
"""

import rtde_receive

def check_ur10e_state():
    """Check what mode the UR10e is in"""
    print("🤖 UR10e Robot State Check")
    print("=" * 30)
    
    robot_ip = "192.168.1.6"
    
    try:
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        robot_mode = rtde_r.getRobotMode()
        safety_mode = rtde_r.getSafetyMode()
        
        # UR mode meanings
        modes = {
            0: "NO_CONTROLLER",
            1: "DISCONNECTED",
            2: "CONFIRM_SAFETY", 
            3: "BOOTING",
            4: "POWER_OFF",
            5: "POWER_ON",
            6: "IDLE",
            7: "BACKDRIVE",  # Manual/Freedrive
            8: "RUNNING",    # What we need!
            9: "UPDATING_FIRMWARE"
        }
        
        mode_name = modes.get(robot_mode, f"Unknown({robot_mode})")
        
        print(f"📊 Current State:")
        print(f"   Robot Mode: {robot_mode} ({mode_name})")
        print(f"   Safety Mode: {safety_mode}")
        
        if robot_mode == 8:
            print("✅ Perfect! Robot is in RUNNING mode")
            print("   RTDE control should work for poses")
        elif robot_mode == 7:
            print("⚠️  Robot is in BACKDRIVE/Manual mode")
            print("   This is why poses don't work")
            print("💡 To fix: Start a program on the teach pendant")
        elif robot_mode == 6:
            print("⚠️  Robot is IDLE")
            print("💡 To fix: Load and start a program")
        else:
            print(f"❓ Robot mode {robot_mode} - check robot status")
        
        rtde_r.disconnect()
        
    except Exception as e:
        print(f"❌ Cannot check state: {e}")

if __name__ == "__main__":
    check_ur10e_state()
