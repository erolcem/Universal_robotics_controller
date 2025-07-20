#!/usr/bin/env python3
"""
Simple debug script to test RTDE connection like your original script.
This mimics your working ur_example.py approach.
"""

import rtde_control
import rtde_receive
import time

# Test with different IPs
test_ips = ["127.0.0.1", "localhost", "172.17.0.3"]

for robot_ip in test_ips:
    print(f"\n🔗 Testing connection to {robot_ip}...")
    
    try:
        # Test RTDEControlInterface first (like your original script)
        print(f"  Trying RTDEControlInterface...")
        rtde_c = rtde_control.RTDEControlInterface(robot_ip)
        
        if rtde_c.isConnected():
            print(f"  ✅ RTDEControlInterface connected to {robot_ip}")
            
            # Try to get some basic info
            try:
                # Test RTDEReceiveInterface
                print(f"  Trying RTDEReceiveInterface...")
                rtde_r = rtde_receive.RTDEReceiveInterface(robot_ip)
                
                if rtde_r.isConnected():
                    print(f"  ✅ RTDEReceiveInterface connected to {robot_ip}")
                    
                    # Get current pose (like your script)
                    pose = rtde_r.getActualTCPPose()
                    print(f"  📍 Current TCP pose: {[round(p, 3) for p in pose]}")
                    
                    rtde_r.disconnect()
                    print(f"  ✅ Connection test successful for {robot_ip}")
                    break
                else:
                    print(f"  ❌ RTDEReceiveInterface failed for {robot_ip}")
            except Exception as e:
                print(f"  ❌ RTDEReceiveInterface error: {e}")
                
            rtde_c.disconnect()
        else:
            print(f"  ❌ RTDEControlInterface failed for {robot_ip}")
            
    except Exception as e:
        print(f"  ❌ Connection error for {robot_ip}: {e}")

print("\n🧪 Connection test complete!")
