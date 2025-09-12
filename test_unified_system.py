#!/usr/bin/env python3
"""
Unified Robot System Demonstration
Test script showing integrated UR + MIR control capabilities
"""

import time
import subprocess
import sys
from pathlib import Path

def test_unified_system():
    """Test the unified robot control system"""
    print("🚀 Unified Robot System Test")
    print("=" * 50)
    
    # Test 1: Check if control directory exists
    control_dir = Path("control")
    if not control_dir.exists():
        print("📁 Creating control directory...")
        control_dir.mkdir(exist_ok=True)
    
    # Test 2: Test CLI tool functionality
    print("\\n🔧 Testing CLI tool...")
    try:
        # Test system status
        result = subprocess.run([
            "python3", "unified_robot_cli.py", "system", "--status"
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ CLI tool working")
        else:
            print(f"⚠️  CLI tool error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⚠️  CLI tool timeout (system may not be running)")
    except Exception as e:
        print(f"❌ CLI tool test failed: {e}")
    
    # Test 3: Check function files
    print("\\n📁 Checking UR function files...")
    functions_dir = Path("functions")
    if functions_dir.exists():
        function_files = list(functions_dir.glob("*.jsonl"))
        print(f"✅ Found {len(function_files)} UR function files:")
        for func_file in sorted(function_files):
            print(f"   • {func_file.stem}")
    else:
        print("❌ Functions directory not found")
    
    # Test 4: Check MIR system files
    print("\\n🚁 Checking MIR system files...")
    mir_dir = Path("YW_MiR")
    if mir_dir.exists():
        mir_files = [
            "simple_mir_control.py",
            "mir_api_control.py", 
            "requirements.txt"
        ]
        
        for mir_file in mir_files:
            file_path = mir_dir / mir_file
            if file_path.exists():
                print(f"✅ {mir_file}")
            else:
                print(f"❌ {mir_file} missing")
    else:
        print("❌ YW_MiR directory not found")
    
    # Test 5: Show usage examples
    print("\\n📋 Usage Examples:")
    print("   # Start unified system:")
    print("   python3 unified_robot_control.py")
    print()
    print("   # External CLI control:")
    print("   python3 unified_robot_cli.py system --status")
    print("   python3 unified_robot_cli.py ur --add home")
    print("   python3 unified_robot_cli.py mir --pause")
    print("   python3 unified_robot_cli.py collab pickup --speed 0.15")
    print()
    print("   # Interactive commands (once system running):")
    print("   🤖 unified> status")
    print("   🤖 unified> collab pickup")
    print("   🤖 unified> mir pause") 
    print("   🤖 unified> add square 0.2")
    
    print("\\n✨ Unified Robot System Test Complete!")
    print("\\n🎯 Next Steps:")
    print("1. Start the unified system: python3 unified_robot_control.py")
    print("2. Use 'status' command to verify both UR and MIR connections")
    print("3. Try 'collab pickup' for collaborative operation")
    print("4. Use CLI tool for external program integration")

def test_mir_connection():
    """Test MIR connection specifically"""
    print("\\n🚁 Testing MIR Connection...")
    
    try:
        # Add YW_MiR to path and test import
        sys.path.append(str(Path("YW_MiR")))
        from simple_mir_control import SimpleMiRControl
        
        print("✅ MIR control module imported successfully")
        
        # Test connection (with timeout)
        print("🔗 Testing MIR connection...")
        mir = SimpleMiRControl("mir.com")
        
        # Quick status check
        status = mir._get_status()
        if status:
            print("✅ MIR connection successful!")
            print(f"   Robot: {status.get('robot_name', 'Unknown')}")
            print(f"   State: {status.get('state_text', 'Unknown')}")
            return True
        else:
            print("⚠️  MIR connection failed (robot may be offline)")
            return False
            
    except ImportError as e:
        print(f"❌ MIR import error: {e}")
        print("   Make sure 'requests' is installed: pip install requests")
        return False
    except Exception as e:
        print(f"⚠️  MIR connection error: {e}")
        print("   This is normal if MIR robot is not available")
        return False

def test_ur_connection():
    """Test UR connection specifically"""
    print("\\n🤖 Testing UR Connection...")
    
    try:
        import socket
        
        ur_ip = "192.168.1.6"
        ur_port = 30002
        
        print(f"🔗 Testing UR connection to {ur_ip}:{ur_port}...")
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        
        result = sock.connect_ex((ur_ip, ur_port))
        sock.close()
        
        if result == 0:
            print("✅ UR robot connection successful!")
            return True
        else:
            print("⚠️  UR robot connection failed (robot may be offline)")
            return False
            
    except Exception as e:
        print(f"❌ UR connection error: {e}")
        return False

if __name__ == "__main__":
    # Run comprehensive test
    test_unified_system()
    
    # Test individual connections
    ur_ok = test_ur_connection()
    mir_ok = test_mir_connection()
    
    print("\\n🏁 Test Summary:")
    print(f"   UR Robot: {'✅' if ur_ok else '⚠️ '}")
    print(f"   MIR Base: {'✅' if mir_ok else '⚠️ '}")
    
    if ur_ok or mir_ok:
        print("\\n🚀 Ready to start unified system!")
    else:
        print("\\n⚠️  No robots connected - system will run in simulation mode")
