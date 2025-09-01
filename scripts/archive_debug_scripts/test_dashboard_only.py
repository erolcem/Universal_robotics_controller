#!/usr/bin/env python3
"""
Simple dashboard test - no External Control needed
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

try:
    import dashboard_client
    import rtde_receive
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def test_dashboard_only(robot_ip):
    """Test basic robot communication without External Control."""
    print(f"🔍 Testing basic robot communication with {robot_ip}")
    print("(No External Control program needed)")
    print("-" * 50)
    
    # Test dashboard connection
    try:
        print("📊 Connecting to dashboard...")
        dashboard = dashboard_client.DashboardClient(robot_ip)
        dashboard.connect()
        
        print("✅ Dashboard connected!")
        
        # Get robot information
        robot_mode = dashboard.robotmode()
        safety_mode = dashboard.safetymode() 
        program_state = dashboard.programState()
        
        print(f"🤖 Robot mode: {robot_mode}")
        print(f"🛡️  Safety mode: {safety_mode}")
        print(f"🔧 Program state: {program_state}")
        
        dashboard.disconnect()
        
    except Exception as e:
        print(f"❌ Dashboard failed: {e}")
        return False
    
    # Test RTDE receive (read-only)
    try:
        print("\n📡 Connecting to RTDE (read-only)...")
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        if rtde_r.isConnected():
            print("✅ RTDE Receive connected!")
            
            # Get current position
            joint_pos = rtde_r.getActualQ()
            tcp_pos = rtde_r.getActualTCPPose()
            
            print(f"🦾 Joint positions: {[round(j, 3) for j in joint_pos]}")
            print(f"📍 TCP position: {[round(p, 3) for p in tcp_pos]}")
            
            rtde_r.disconnect()
            print("✅ Basic robot communication works!")
            return True
        else:
            print("❌ RTDE Receive failed")
            return False
            
    except Exception as e:
        print(f"❌ RTDE Receive failed: {e}")
        return False

if __name__ == "__main__":
    robot_ip = "192.168.1.5"
    
    print("🚀 Dashboard-Only Robot Test")
    print("=" * 30)
    print("This test doesn't require External Control")
    print("It only reads robot status and position")
    print()
    
    success = test_dashboard_only(robot_ip)
    
    if success:
        print("\n🎉 SUCCESS! Basic communication works.")
        print("Now you can set up External Control for full control.")
    else:
        print("\n❌ Basic communication failed.")
        print("Check network connection and robot status.")
