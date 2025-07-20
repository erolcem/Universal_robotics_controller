#!/usr/bin/env python3
"""
Visual movement test - moves robot slowly so you can see it in the simulator
"""

import sys
from pathlib import Path
import time

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    import rtde_control
    import rtde_receive
except ImportError:
    print("❌ Please activate virtual environment: source ur_venv/bin/activate")
    sys.exit(1)

def visual_movement_test():
    """Perform slow, visible movements for verification."""
    robot_ip = "127.0.0.1"
    
    print("🎬 Visual Movement Test")
    print("=" * 30)
    print("Watch the robot in the simulator web interface!")
    print("URL: http://localhost:6080/vnc.html")
    print()
    
    try:
        # Connect
        print("🔗 Connecting...")
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
        
        if not (rtde_c.isConnected() and rtde_r.isConnected()):
            print("❌ Connection failed!")
            return
            
        print("✅ Connected!")
        
        # Get initial pose
        initial_pose = rtde_r.getActualTCPPose()
        print(f"📍 Starting pose: {[round(p, 3) for p in initial_pose]}")
        
        input("\n🎯 Press Enter to start slow movements (watch the simulator)...")
        
        # Slow movements that should be clearly visible
        moves = [
            {"name": "Move UP 10cm", "pose": [initial_pose[0], initial_pose[1], initial_pose[2] + 0.1, initial_pose[3], initial_pose[4], initial_pose[5]]},
            {"name": "Move DOWN to start", "pose": initial_pose},
            {"name": "Move RIGHT 15cm", "pose": [initial_pose[0] + 0.15, initial_pose[1], initial_pose[2], initial_pose[3], initial_pose[4], initial_pose[5]]},
            {"name": "Move LEFT to start", "pose": initial_pose},
            {"name": "Move FORWARD 10cm", "pose": [initial_pose[0], initial_pose[1] + 0.1, initial_pose[2], initial_pose[3], initial_pose[4], initial_pose[5]]},
            {"name": "Move BACK to start", "pose": initial_pose}
        ]
        
        for i, move in enumerate(moves, 1):
            print(f"\n{i}/6 🔄 {move['name']}...")
            print(f"     Target: {[round(p, 3) for p in move['pose']]}")
            
            # Very slow movement so it's clearly visible
            rtde_c.moveL(move['pose'], speed=0.05, acceleration=0.1)
            
            # Show current position
            current = rtde_r.getActualTCPPose()
            print(f"     Result: {[round(p, 3) for p in current]}")
            
            time.sleep(1)  # Pause between movements
        
        print("\n✅ Movement test completed!")
        print("Did you see the robot move in the simulator?")
        
        rtde_c.disconnect()
        rtde_r.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    visual_movement_test()
