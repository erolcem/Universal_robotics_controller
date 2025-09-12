#!/usr/bin/env python3
"""
MIR Connection Test for IP: 118.138.127.231
Tests connection and basic functionality with your specific MIR robot
"""

import sys
import os

# Add YW_MiR directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'YW_MiR'))

try:
    from simple_mir_control import SimpleMiRControl
    MIR_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  MIR control not available: {e}")
    MIR_AVAILABLE = False

def test_mir_connection():
    if not MIR_AVAILABLE:
        print("❌ MIR control library not available")
        print("   Please check YW_MiR/simple_mir_control.py exists")
        return False
        
    print("🚁 Testing MIR Connection")
    print("=" * 40)
    
    # Your MIR IP address
    mir_ip = "118.138.127.231"
    print(f"🔗 Connecting to MIR at: {mir_ip}")
    
    try:
        # Create MIR control instance
        mir = SimpleMiRControl(robot_ip=mir_ip)
        
        print("\n📊 MIR Status:")
        print("-" * 20)
        mir.status_summary()
        
        print("\n🧪 Testing Basic Functions:")
        print("-" * 30)
        
        # Test status checks
        print(f"✓ Is Ready: {mir.is_ready()}")
        print(f"✓ Is Paused: {mir.is_paused()}")
        print(f"✓ Battery: {mir.get_battery():.1f}%")
        
        position = mir.get_position()
        print(f"✓ Position: x={position['x']:.2f}m, y={position['y']:.2f}m, θ={position['orientation']:.1f}°")
        
        print("\n🎯 Ready for collaborative operations!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("   • Check if MIR is reachable: ping 118.138.127.231")
        print("   • Verify MIR API is enabled")
        print("   • Check network connectivity")
        print("   • Ensure correct credentials (Distributor/distributor)")
        return False

def show_integration_commands():
    print("\n🚀 MIR INTEGRATION COMMANDS:")
    print("=" * 40)
    
    print("1. Start unified system with your MIR:")
    print("   python3 unified_robot_control_simple.py --robot-ip 192.168.1.6 --mir-ip 118.138.127.231")
    print()
    
    print("2. Use collaborative commands:")
    print("   collab pickup          # Auto-pause MIR during UR pickup")
    print("   collab dropoff1        # Auto-pause MIR during UR dropoff")
    print("   mir pause              # Manual MIR pause")
    print("   mir resume             # Manual MIR resume")
    print("   mir status             # Check MIR status")
    print("   mir auto true          # Enable auto-pause for all UR functions")
    print()
    
    print("3. External CLI control:")
    print("   python3 simple_unified_cli.py mir --pause")
    print("   python3 simple_unified_cli.py mir --resume")
    print("   python3 simple_unified_cli.py mir --status")
    print("   python3 simple_unified_cli.py collab pickup")
    print()
    
    print("4. File-based control:")
    print("   echo 'mir_pause' >> control/robot_commands.txt")
    print("   echo 'collab dropoff1' >> control/robot_commands.txt")
    print("   echo 'mir_resume' >> control/robot_commands.txt")

def main():
    test_mir_connection()
    show_integration_commands()
    
    print("\n✨ MIR Integration Ready!")
    print("Your MIR at 118.138.127.231 can now be controlled")
    print("alongside your UR robot for collaborative operations! 🤖🚁")

if __name__ == "__main__":
    main()
