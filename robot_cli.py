#!/usr/bin/env python3
"""
Robot Command Line Interface
Quick command-line control for the robot system
"""

import sys
import json
from pathlib import Path

def send_command(command: str, control_dir: str = "control"):
    """Send a single command to the robot"""
    command_file = Path(control_dir) / "robot_commands.txt"
    with open(command_file, 'a') as f:
        f.write(f"{command}\n")
    print(f"✅ Command sent: {command}")

def get_status(control_dir: str = "control"):
    """Get and display robot status"""
    status_file = Path(control_dir) / "robot_status.json"
    try:
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        print("📊 Robot Status:")
        print(f"   Running: {'✅' if status.get('running', False) else '❌'}")
        print(f"   Paused: {'⏸️' if status.get('paused', False) else '▶️'}")
        print(f"   Speed: {status.get('current_speed', 0)} m/s")
        print(f"   Multiplier: {status.get('speed_multiplier', 1)}x")
        print(f"   Effective Speed: {status.get('effective_speed', 0):.3f} m/s")
        print(f"   Functions Executed: {status.get('functions_executed', 0)}")
        print(f"   Commands Executed: {status.get('commands_executed', 0)}")
        print(f"   Queue Size: {status.get('queue_size', 0)}")
        if 'uptime' in status:
            print(f"   Uptime: {status['uptime']:.1f}s")
            
    except Exception as e:
        print(f"❌ Could not read status: {e}")

def show_help():
    """Show available commands"""
    print("""
🤖 Robot Command Line Interface

Usage: python robot_cli.py <command> [args]

Commands:
  status                    - Show robot status
  pause                     - Pause robot execution
  resume                    - Resume robot execution
  stop                      - Stop robot and clear queues
  slow                      - Slow down robot (halve speed)
  fast                      - Speed up robot (double speed)
  speed <value>            - Set base speed (0.01-1.0 m/s)
  multiplier <value>       - Set speed multiplier (0.1-5.0x)
  add <function> [speed]   - Add function to queue
  help                     - Show this help

Examples:
  python robot_cli.py status
  python robot_cli.py pause
  python robot_cli.py speed 0.1
  python robot_cli.py add pickup 0.05
  python robot_cli.py fast
    """)

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "help":
        show_help()
    elif command == "status":
        get_status()
    elif command in ["pause", "resume", "stop", "slow", "fast"]:
        send_command(command)
    elif command == "speed" and len(sys.argv) > 2:
        try:
            speed = float(sys.argv[2])
            send_command(f"speed {speed}")
        except ValueError:
            print("❌ Invalid speed value")
    elif command == "multiplier" and len(sys.argv) > 2:
        try:
            multiplier = float(sys.argv[2])
            send_command(f"multiplier {multiplier}")
        except ValueError:
            print("❌ Invalid multiplier value")
    elif command == "add" and len(sys.argv) > 2:
        function_name = sys.argv[2]
        if len(sys.argv) > 3:
            try:
                speed = float(sys.argv[3])
                send_command(f"add {function_name} {speed}")
            except ValueError:
                print("❌ Invalid speed value")
        else:
            send_command(f"add {function_name}")
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python robot_cli.py help' for available commands")

if __name__ == "__main__":
    main()
