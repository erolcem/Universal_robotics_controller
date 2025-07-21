#!/usr/bin/env python3
"""
Simple External Control Debug Tool

This tool helps debug External Control connection issues step by step.
"""

import socket
import time
import subprocess

def check_network_reachability():
    """Check if robot can reach our computer."""
    print("🔍 Checking network reachability...")
    
    # Check if we can reach robot
    try:
        result = subprocess.run(['ping', '-c', '3', '192.168.1.5'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ Computer can reach robot")
        else:
            print("❌ Computer cannot reach robot")
            return False
    except Exception as e:
        print(f"❌ Ping test failed: {e}")
        return False
    
    return True

def test_simple_server():
    """Run a very simple server to test robot connection."""
    print("\n🎧 Starting simple server on port 50002...")
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Bind to all interfaces
        server.bind(('', 50002))
        server.listen(1)
        server.settimeout(60.0)  # 60 second timeout
        
        print("✅ Server listening on all interfaces, port 50002")
        print("📋 Robot Instructions:")
        print("1. Make sure robot is in LOCAL mode")
        print("2. Start External Control program")
        print("3. Switch to REMOTE mode")
        print("4. External Control should try to connect")
        print()
        print("⏳ Waiting 60 seconds for robot connection...")
        print("   (You should see connection attempt even if it fails)")
        
        try:
            client, addr = server.accept()
            print(f"🎉 SUCCESS! Robot connected from {addr}")
            
            # Read any data the robot sends
            client.settimeout(5.0)
            try:
                data = client.recv(1024)
                print(f"📨 Received data: {data}")
            except socket.timeout:
                print("📭 No immediate data from robot (normal)")
            
            # Send a simple response
            try:
                client.send(b"Hello from computer\n")
                print("📤 Sent response to robot")
            except:
                pass
                
            # Keep connection open briefly
            time.sleep(5)
            client.close()
            
            return True
            
        except socket.timeout:
            print("⏰ Timeout - no connection from robot")
            print("\n🔧 This means:")
            print("- Robot External Control program is not running, OR")
            print("- Robot External Control has wrong IP/port, OR") 
            print("- Robot is not in Remote mode, OR")
            print("- Network connectivity issue")
            return False
            
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False
        
    finally:
        server.close()

def check_port_availability():
    """Check if port 50002 is available."""
    print("🔍 Checking if port 50002 is available...")
    
    test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        test_socket.bind(('', 50002))
        test_socket.close()
        print("✅ Port 50002 is available")
        return True
    except OSError:
        print("❌ Port 50002 is in use")
        return False

def main():
    print("🔧 External Control Debug Tool")
    print("=" * 40)
    print("This tool will help diagnose External Control connection issues.")
    print()
    
    # Step 1: Check network
    if not check_network_reachability():
        print("\n❌ Network connectivity issue - fix this first")
        return 1
    
    # Step 2: Check port
    if not check_port_availability():
        print("\n❌ Port 50002 is busy - close other applications")
        return 1
    
    # Step 3: Test connection
    print("\n" + "="*50)
    print("🚀 STARTING CONNECTION TEST")
    print("="*50)
    
    success = test_simple_server()
    
    if success:
        print("\n🎉 EXTERNAL CONTROL CONNECTION WORKS!")
        print("The issue is likely in the ur-rtde library integration.")
        print("Try running your robot control scripts now.")
    else:
        print("\n❌ EXTERNAL CONTROL CONNECTION FAILED")
        print("The robot is not connecting to your computer.")
        print("Check the robot's External Control configuration.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
