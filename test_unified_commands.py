#!/usr/bin/env python3
"""
Test the Simple Unified Robot Control System
Demonstrates all unified commands and external control
"""

import time
import subprocess
import sys
from pathlib import Path

def test_interactive_commands():
    """Test interactive terminal commands"""
    print("🎯 INTERACTIVE TERMINAL COMMANDS:")
    print("=" * 40)
    print("When the unified system is running, try these commands:")
    print()
    
    print("📋 BASIC COMMANDS:")
    print("  help                          # Show all commands")
    print("  status                        # Show unified system status")  
    print("  list                          # List available UR functions")
    print()
    
    print("🤖 UR ROBOT COMMANDS:")
    print("  add home                      # Add UR function (no MIR pause)")
    print("  add pickup 0.15               # Add UR function with custom speed")
    print("  add dropoff 0.1 true          # Add UR function with MIR pause")
    print("  collab pickup                 # Add UR function with auto MIR pause")
    print("  collab square 0.2             # Collaborative function with speed")
    print("  speed 0.2                     # Set UR base speed")
    print("  multiplier 1.5                # Set UR speed multiplier")
    print("  slow                          # Halve current speed")
    print("  fast                          # Double current speed")
    print()
    
    print("🚁 MIR BASE COMMANDS:")
    print("  mir pause                     # Pause MIR base")
    print("  mir resume                    # Resume MIR base")
    print("  mir status                    # Show MIR status")
    print("  mir auto true                 # Enable auto-pause during UR functions")
    print("  mir auto false                # Disable auto-pause")
    print()
    
    print("⚡ SYSTEM COMMANDS:")
    print("  pause                         # Pause entire system")
    print("  resume                        # Resume entire system") 
    print("  stop                          # Stop and clear all queues")
    print("  quit                          # Exit program")

def test_external_cli():
    """Test external CLI commands"""
    print("\\n🎯 EXTERNAL CLI COMMANDS:")
    print("=" * 40)
    print("Use these commands from another terminal:")
    print()
    
    print("📋 SYSTEM CONTROL:")
    print("  python3 simple_unified_cli.py system --status")
    print("  python3 simple_unified_cli.py system --pause")
    print("  python3 simple_unified_cli.py system --resume")
    print("  python3 simple_unified_cli.py system --stop")
    print()
    
    print("🤖 UR ROBOT CONTROL:")
    print("  python3 simple_unified_cli.py ur --add home")
    print("  python3 simple_unified_cli.py ur --add pickup --function-speed 0.15")
    print("  python3 simple_unified_cli.py ur --add dropoff --function-speed 0.1 --pause-mir")
    print("  python3 simple_unified_cli.py ur --speed 0.2")
    print("  python3 simple_unified_cli.py ur --multiplier 1.5")
    print("  python3 simple_unified_cli.py ur --slow")
    print("  python3 simple_unified_cli.py ur --fast")
    print()
    
    print("🚁 MIR BASE CONTROL:")
    print("  python3 simple_unified_cli.py mir --pause")
    print("  python3 simple_unified_cli.py mir --resume")
    print("  python3 simple_unified_cli.py mir --status")
    print("  python3 simple_unified_cli.py mir --auto true")
    print("  python3 simple_unified_cli.py mir --auto false")
    print()
    
    print("🤝 COLLABORATIVE OPERATIONS:")
    print("  python3 simple_unified_cli.py collab pickup")
    print("  python3 simple_unified_cli.py collab square --speed 0.2")
    print("  python3 simple_unified_cli.py collab pick_and_place --speed 0.1")

def test_file_based_control():
    """Test file-based external control"""
    print("\\n🎯 FILE-BASED CONTROL:")
    print("=" * 40)
    print("Write commands directly to control files:")
    print()
    
    print("📝 COMMAND FILE EXAMPLES:")
    commands = [
        "status",
        "mir_status", 
        "ur_add home 0.15",
        "collab pickup 0.1",
        "mir_pause",
        "add square 0.2 false",
        "mir_resume",
        "pause",
        "resume"
    ]
    
    for cmd in commands:
        print(f"  echo '{cmd}' >> control/robot_commands.txt")
    
    print()
    print("📄 MONITORING FILES:")
    print("  tail -f control/robot_response.txt    # Watch responses")
    print("  cat control/robot_status.json         # Check system status")

def demo_workflow():
    """Demonstrate a complete collaborative workflow"""
    print("\\n🎯 COMPLETE COLLABORATIVE WORKFLOW:")
    print("=" * 40)
    print("Example sequence for pick and place with MIR coordination:")
    print()
    
    workflow = [
        ("Check system status", "status"),
        ("Check MIR status", "mir status"),
        ("Enable MIR auto-pause", "mir auto true"),
        ("Collaborative pickup", "collab pickup 0.1"),
        ("Fast movement pattern", "add square 0.3 false"),
        ("Collaborative dropoff", "collab dropoff 0.1"),
        ("Return home", "add home 0.2"),
        ("Final status check", "status")
    ]
    
    print("INTERACTIVE SEQUENCE:")
    for i, (desc, cmd) in enumerate(workflow, 1):
        print(f"  {i}. {desc:<25} → {cmd}")
    
    print("\\nEXTERNAL CLI SEQUENCE:")
    for i, (desc, cmd) in enumerate(workflow, 1):
        # Convert to CLI format
        if cmd.startswith("collab"):
            parts = cmd.split()
            cli_cmd = f"python3 simple_unified_cli.py collab {parts[1]}"
            if len(parts) > 2:
                cli_cmd += f" --speed {parts[2]}"
        elif cmd.startswith("mir"):
            parts = cmd.split()
            if parts[1] == "auto":
                cli_cmd = f"python3 simple_unified_cli.py mir --auto {parts[2]}"
            else:
                cli_cmd = f"python3 simple_unified_cli.py mir --{parts[1]}"
        elif cmd.startswith("add"):
            parts = cmd.split()
            cli_cmd = f"python3 simple_unified_cli.py ur --add {parts[1]}"
            if len(parts) > 2:
                cli_cmd += f" --function-speed {parts[2]}"
        elif cmd == "status":
            cli_cmd = "python3 simple_unified_cli.py system --status"
        else:
            cli_cmd = f"# {cmd}"
            
        print(f"  {i}. {desc:<25} → {cli_cmd}")

def main():
    print("🚀 Simple Unified Robot Control System - Test Guide")
    print("=" * 60)
    
    # Test interactive commands
    test_interactive_commands()
    
    # Test external CLI
    test_external_cli()
    
    # Test file-based control
    test_file_based_control()
    
    # Demo complete workflow
    demo_workflow()
    
    print("\\n🎯 QUICK START:")
    print("=" * 40)
    print("1. Start the unified system:")
    print("   python3 unified_robot_control_simple.py --robot-ip 192.168.1.6 --mir-ip mir.com")
    print()
    print("2. Or with MIR disabled:")
    print("   python3 unified_robot_control_simple.py --robot-ip 192.168.1.6 --mir-ip offline")
    print()
    print("3. Test with CLI tool:")
    print("   python3 simple_unified_cli.py system --status")
    print()
    print("4. Monitor via files:")
    print("   watch -n 1 'cat control/robot_status.json | jq .'")
    
    print("\\n✨ Ready for unified UR + MIR collaborative robotics! 🤖🚁")

if __name__ == "__main__":
    main()
