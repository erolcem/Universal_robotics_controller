#!/usr/bin/env python3
"""
Simple Unified Robot CLI Tool
External command-line interface for the simple unified robot control system

Provides direct command access to both UR robot and MIR base systems
"""

import argparse
import sys
import time
from pathlib import Path

def send_command(command: str, control_dir: str = "control"):
    """Send command to the unified robot control system"""
    control_path = Path(control_dir)
    command_file = control_path / "robot_commands.txt"
    response_file = control_path / "robot_response.txt"
    
    # Ensure control directory exists
    control_path.mkdir(exist_ok=True)
    
    # Clear old response
    if response_file.exists():
        response_file.write_text("")
    
    # Send command
    with open(command_file, 'a') as f:
        f.write(command + "\\n")
    
    print(f"📤 Command sent: {command}")
    
    # Wait for response (optional)
    if "--wait" in sys.argv:
        print("⏳ Waiting for response...")
        start_time = time.time()
        
        while time.time() - start_time < 5.0:  # 5 second timeout
            if response_file.exists():
                response = response_file.read_text().strip()
                if response:
                    print("📨 Response:")
                    print(response)
                    break
            time.sleep(0.1)
        else:
            print("⚠️  No response received within timeout")

def main():
    parser = argparse.ArgumentParser(description="Simple Unified Robot CLI Tool")
    parser.add_argument("--control-dir", default="control", help="Control directory path")
    parser.add_argument("--wait", action="store_true", help="Wait for response")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # System commands
    system_parser = subparsers.add_parser("system", help="System control commands")
    system_group = system_parser.add_mutually_exclusive_group(required=True)
    system_group.add_argument("--pause", action="store_true", help="Pause entire system")
    system_group.add_argument("--resume", action="store_true", help="Resume entire system")
    system_group.add_argument("--stop", action="store_true", help="Stop system and clear queues")
    system_group.add_argument("--status", action="store_true", help="Show system status")
    
    # UR robot commands
    ur_parser = subparsers.add_parser("ur", help="UR robot commands")
    ur_group = ur_parser.add_mutually_exclusive_group(required=True)
    ur_group.add_argument("--add", metavar="FUNCTION", help="Add UR function to queue")
    ur_group.add_argument("--speed", metavar="VALUE", type=float, help="Set UR speed (0.01-1.0)")
    ur_group.add_argument("--multiplier", metavar="VALUE", type=float, help="Set UR speed multiplier (0.1-5.0)")
    ur_group.add_argument("--slow", action="store_true", help="Halve current speed")
    ur_group.add_argument("--fast", action="store_true", help="Double current speed")
    ur_parser.add_argument("--function-speed", metavar="SPEED", type=float, help="Speed for specific function")
    ur_parser.add_argument("--pause-mir", action="store_true", help="Pause MIR during function execution")
    
    # MIR base commands
    mir_parser = subparsers.add_parser("mir", help="MIR base commands")
    mir_group = mir_parser.add_mutually_exclusive_group(required=True)
    mir_group.add_argument("--pause", action="store_true", help="Pause MIR base")
    mir_group.add_argument("--resume", action="store_true", help="Resume MIR base")
    mir_group.add_argument("--status", action="store_true", help="Show MIR status")
    mir_group.add_argument("--auto", metavar="TRUE/FALSE", help="Enable/disable auto-pause")
    
    # Collaborative commands
    collab_parser = subparsers.add_parser("collab", help="Collaborative operation commands")
    collab_parser.add_argument("function", help="UR function name")
    collab_parser.add_argument("--speed", metavar="SPEED", type=float, help="UR function speed")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Build command string
    command = ""
    
    if args.command == "system":
        if args.pause:
            command = "pause"
        elif args.resume:
            command = "resume"
        elif args.stop:
            command = "stop"
        elif args.status:
            command = "status"
    
    elif args.command == "ur":
        if args.add:
            command = f"ur_add {args.add}"
            if args.function_speed:
                command += f" {args.function_speed}"
            if args.pause_mir:
                command += " true"
        elif args.speed:
            command = f"speed {args.speed}"
        elif args.multiplier:
            command = f"multiplier {args.multiplier}"
        elif args.slow:
            command = "slow"
        elif args.fast:
            command = "fast"
    
    elif args.command == "mir":
        if args.pause:
            command = "mir_pause"
        elif args.resume:
            command = "mir_resume"
        elif args.status:
            command = "mir_status"
        elif args.auto:
            command = f"mir_auto {args.auto.lower()}"
    
    elif args.command == "collab":
        command = f"collab {args.function}"
        if args.speed:
            command += f" {args.speed}"
    
    if command:
        send_command(command, args.control_dir)
    else:
        print("❌ Invalid command combination")
        parser.print_help()

if __name__ == "__main__":
    main()
