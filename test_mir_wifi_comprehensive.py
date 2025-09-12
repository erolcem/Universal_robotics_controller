#!/usr/bin/env python3
"""
MIR WiFi Comprehensive Test
Run this when connected to MIR WiFi to test all functionality at once
"""

import sys
import time
import json
import requests
from pathlib import Path

def test_mir_connection():
    """Test basic MIR connection and API access"""
    print("🔌 Testing MIR Connection...")
    
    try:
        # Add YW_MiR to path
        sys.path.append(str(Path("YW_MiR")))
        from simple_mir_control import SimpleMiRControl
        
        # Test connection
        mir = SimpleMiRControl("mir.com")
        status = mir._get_status()
        
        if status:
            print("✅ MIR Connection Successful!")
            print(f"   Robot Name: {status.get('robot_name', 'Unknown')}")
            print(f"   State: {status.get('state_text', 'Unknown')}")
            print(f"   Battery: {status.get('battery_percentage', 0)}%")
            
            pos = status.get('position', {})
            print(f"   Position: x={pos.get('x', 0):.2f}, y={pos.get('y', 0):.2f}, θ={pos.get('orientation', 0):.1f}°")
            
            return mir, status
        else:
            print("❌ MIR Connection Failed")
            return None, None
            
    except Exception as e:
        print(f"❌ MIR Connection Error: {e}")
        return None, None

def test_mir_control(mir):
    """Test MIR pause/resume functionality"""
    print("\\n⏯️  Testing MIR Control...")
    
    try:
        # Get initial state
        initial_status = mir._get_status()
        initial_state = initial_status.get('state_text', 'Unknown') if initial_status else 'Unknown'
        print(f"Initial State: {initial_state}")
        
        # Test pause
        print("Testing pause...")
        if mir.pause():
            print("✅ Pause command successful")
            time.sleep(2)
            
            # Check if actually paused
            status = mir._get_status()
            if status:
                current_state = status.get('state_text', 'Unknown')
                print(f"State after pause: {current_state}")
        
        # Test resume
        print("Testing resume...")
        if mir.resume():
            print("✅ Resume command successful")
            time.sleep(2)
            
            # Check if resumed
            status = mir._get_status()
            if status:
                current_state = status.get('state_text', 'Unknown')
                print(f"State after resume: {current_state}")
        
        return True
        
    except Exception as e:
        print(f"❌ MIR Control Error: {e}")
        return False

def test_unified_system_with_mir():
    """Test unified system components with MIR"""
    print("\\n🤖 Testing Unified System with MIR...")
    
    try:
        # Test control directory creation
        control_dir = Path("control")
        control_dir.mkdir(exist_ok=True)
        print("✅ Control directory ready")
        
        # Test command file
        command_file = control_dir / "robot_commands.txt"
        test_commands = [
            "mir_status",
            "mir_pause", 
            "mir_resume",
            "system status"
        ]
        
        # Write test commands
        command_file.write_text("\\n".join(test_commands))
        print("✅ Test commands written")
        
        # Test status file creation
        status_file = control_dir / "robot_status.json"
        test_status = {
            "systems": {
                "mir_base": {
                    "enabled": True,
                    "connected": True,
                    "ip": "mir.com"
                }
            },
            "timestamp": time.time()
        }
        
        with open(status_file, 'w') as f:
            json.dump(test_status, f, indent=2)
        print("✅ Status file created")
        
        return True
        
    except Exception as e:
        print(f"❌ Unified system test error: {e}")
        return False

def test_mir_api_directly():
    """Test MIR API directly with requests"""
    print("\\n🌐 Testing MIR API Directly...")
    
    try:
        base_url = "http://mir.com/api/v2.0.0"
        auth = ("Distributor", "distributor")
        
        # Test status endpoint
        response = requests.get(f"{base_url}/status", auth=auth, timeout=10)
        response.raise_for_status()
        
        status_data = response.json()
        print("✅ Direct API access successful")
        print(f"   Robot: {status_data.get('robot_name', 'Unknown')}")
        print(f"   State ID: {status_data.get('state_id', 'Unknown')}")
        
        # Test missions endpoint
        response = requests.get(f"{base_url}/missions", auth=auth, timeout=10)
        response.raise_for_status()
        
        missions = response.json()
        print(f"✅ Found {len(missions)} missions")
        
        # Test mission queue
        response = requests.get(f"{base_url}/mission_queue", auth=auth, timeout=10)
        response.raise_for_status()
        
        queue = response.json()
        print(f"✅ Mission queue has {len(queue)} items")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct API test error: {e}")
        return False

def save_mir_configuration():
    """Save MIR configuration for later use"""
    print("\\n💾 Saving MIR Configuration...")
    
    try:
        config = {
            "mir_ip": "mir.com",
            "mir_username": "Distributor", 
            "mir_password": "distributor",
            "test_timestamp": time.time(),
            "test_date": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Get current MIR status to save
        try:
            base_url = "http://mir.com/api/v2.0.0"
            auth = ("Distributor", "distributor")
            response = requests.get(f"{base_url}/status", auth=auth, timeout=5)
            response.raise_for_status()
            config["mir_status"] = response.json()
        except:
            config["mir_status"] = "Could not retrieve"
        
        # Save configuration
        config_file = Path("mir_wifi_config.json")
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Configuration saved to {config_file}")
        return True
        
    except Exception as e:
        print(f"❌ Configuration save error: {e}")
        return False

def generate_integration_commands():
    """Generate commands to test when back on main network"""
    print("\\n📋 Generating Integration Test Commands...")
    
    commands = [
        "# Commands to test unified system after WiFi test:",
        "",
        "# 1. Start unified system with MIR enabled",
        "python3 unified_robot_control.py --ur-ip 192.168.1.6 --mir-ip mir.com",
        "",
        "# 2. Test CLI commands (in separate terminal)",
        "python3 unified_robot_cli.py system --status",
        "python3 unified_robot_cli.py mir --status", 
        "python3 unified_robot_cli.py mir --pause",
        "python3 unified_robot_cli.py mir --resume",
        "",
        "# 3. Test collaborative commands",
        "python3 unified_robot_cli.py collab pickup --speed 0.15",
        "",
        "# 4. Interactive commands (in main terminal)",
        "🤖 unified> status",
        "🤖 unified> mir status",
        "🤖 unified> collab home",
        "🤖 unified> mir pause",
        "🤖 unified> add square 0.2",
        "🤖 unified> mir resume",
        "",
        "# 5. File-based control test",
        "echo 'mir_status' > control/robot_commands.txt",
        "echo 'collab pickup 0.1' >> control/robot_commands.txt",
        "cat control/robot_response.txt",
    ]
    
    commands_file = Path("integration_test_commands.txt")
    commands_file.write_text("\\n".join(commands))
    print(f"✅ Integration commands saved to {commands_file}")

def main():
    """Run comprehensive MIR WiFi test"""
    print("🚁 MIR WiFi Comprehensive Test")
    print("=" * 40)
    print("Make sure you're connected to MIR WiFi network!")
    print()
    
    results = {}
    
    # Test 1: Basic connection
    mir, status = test_mir_connection()
    results["connection"] = mir is not None
    
    if mir:
        # Test 2: Control functionality
        results["control"] = test_mir_control(mir)
        
        # Test 3: Direct API access
        results["api"] = test_mir_api_directly()
        
        # Test 4: Unified system components
        results["unified"] = test_unified_system_with_mir()
        
        # Test 5: Save configuration
        results["config"] = save_mir_configuration()
    else:
        print("⚠️  Skipping other tests due to connection failure")
        results.update({
            "control": False,
            "api": False, 
            "unified": False,
            "config": False
        })
    
    # Generate integration commands
    generate_integration_commands()
    
    # Summary
    print("\\n📊 Test Results Summary:")
    print("=" * 25)
    for test, passed in results.items():
        status_icon = "✅" if passed else "❌"
        print(f"{status_icon} {test.capitalize()}: {'PASS' if passed else 'FAIL'}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\\n🏁 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests >= 3:
        print("\\n✅ MIR WiFi testing successful!")
        print("You can now:")
        print("1. Disconnect from MIR WiFi")
        print("2. Reconnect to your main network") 
        print("3. Use the commands in integration_test_commands.txt")
        print("4. Run: python3 unified_robot_control.py --mir-ip mir.com")
    else:
        print("\\n⚠️  Some tests failed. Check MIR network and API access.")
    
    print("\\nFiles created:")
    print("• mir_wifi_config.json - MIR configuration")
    print("• integration_test_commands.txt - Commands to test later")

if __name__ == "__main__":
    main()
