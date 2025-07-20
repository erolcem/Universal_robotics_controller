#!/usr/bin/env python3
"""
UR Robot Synchronous Control

Executes commands from a JSONL file sequentially with fixed timing.
Each line in the file represents a delta movement command.

Usage:
    python examples/synchronous_control.py [options]
"""

import sys
import argparse
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ur_controller import URRobotController, URCommandProcessor


def main():
    """Main synchronous control function."""
    parser = argparse.ArgumentParser(
        description="Stream JSON delta movements with fixed timing"
    )
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--robot-ip", default="127.0.0.1", help="Robot IP address")
    parser.add_argument("--robot-type", choices=["simulation", "physical"], 
                       default="simulation", help="Robot type")
    parser.add_argument("--json-source", default="examples/synchronous_deltas.jsonl",
                       help="Path to JSONL file with delta commands")
    parser.add_argument("--json-log", help="Path to log file (optional)")
    parser.add_argument("--speed", type=float, default=0.2, help="Movement speed (m/s)")
    parser.add_argument("--acceleration", type=float, default=0.5, 
                       help="Movement acceleration (m/s²)")
    parser.add_argument("--responsiveness", type=float, default=1.0,
                       help="Time between commands (seconds)")
    
    args = parser.parse_args()
    
    print("🤖 UR Robot Controller - Synchronous Mode")
    print("=" * 40)
    print(f"📁 Command file: {args.json_source}")
    print(f"⏱️  Responsiveness: {args.responsiveness}s")
    print(f"🏃 Speed: {args.speed} m/s")
    print(f"⚡ Acceleration: {args.acceleration} m/s²")
    
    # Check if command file exists
    if not Path(args.json_source).exists():
        print(f"❌ Command file not found: {args.json_source}")
        return 1
    
    # Initialize controller
    if args.config:
        controller = URRobotController(config_path=args.config)
    else:
        controller = URRobotController(
            robot_ip=args.robot_ip, 
            robot_type=args.robot_type
        )
    
    # Set movement parameters
    controller.default_speed = args.speed
    controller.default_acceleration = args.acceleration
    
    try:
        # Connect to robot
        if not controller.connect():
            print("❌ Failed to connect to robot")
            return 1
        
        print("✅ Connected to robot")
        
        # Initialize command processor
        processor = URCommandProcessor(controller)
        
        print("🚀 Starting command execution...")
        print("Press Ctrl+C to stop")
        
        # Process commands
        processor.process_synchronous_commands(
            args.json_source, 
            args.json_log, 
            args.responsiveness
        )
        
        print("✅ Command execution completed")
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    finally:
        controller.disconnect()
        print("👋 Disconnected from robot")


if __name__ == "__main__":
    sys.exit(main())
