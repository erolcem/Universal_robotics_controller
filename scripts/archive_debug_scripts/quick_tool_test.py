#!/usr/bin/env python3
"""
Simple Tool I/O Test - Minimal version to avoid freezing
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import rtde_control

def quick_test():
    """Quick test with timeout"""
    print("🔧 Quick Tool I/O Test")
    try:
        # Short timeout to avoid hanging
        rtde_c = rtde_control.RTDEControlInterface("192.168.1.6", 125.0, 0)  # Low frequency, no flags
        
        if rtde_c.isConnected():
            print("✅ Connected")
            
            # Test tool digital output 0
            print("Testing tool_digital_out(0, True)...")
            result1 = rtde_c.sendCustomScript("set_tool_digital_out(0, True)")
            print(f"Result: {result1}")
            
            # Quick disconnect to avoid hanging
            rtde_c.disconnect()
            print("✅ Test complete")
        else:
            print("❌ Connection failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
