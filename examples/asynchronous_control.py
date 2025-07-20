#!/usr/bin/env python3
"""
UR Robot Asynchronous Control

Streams commands from a JSONL file continuously. The robot applies the
most recent command from the file at regular intervals.

Usage:
    python examples/asynchronous_control.py [options]
"""

import sys
import argparse
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ur_controller import URRobotController, URCommandProcessor


def main():
    """Main asynchronous control function."""
    parser = argparse.ArgumentParser(
        description="Stream robot control from JSONL file tail"
    )
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--robot-ip", default="127.0.0.1", help="Robot IP address")
    parser.add_argument("--robot-type", choices=["simulation", "physical"], 
                       default="simulation", help="Robot type")
    parser.add_argument("--json-file", default="examples/asynchronous_deltas.jsonl",
                       help="Path to JSONL file with delta commands")
    parser.add_argument("--acceleration", type=float, default=0.5, 
                       help="Movement acceleration (m/s²)")
    parser.add_argument("--responsiveness", type=float, default=1.0,
                       help="Time between command reads (seconds)")
    
    args = parser.parse_args()
    
    print("🤖 UR Robot Controller - Asynchronous Mode")
    print("=" * 40)
    print(f"📁 Command file: {args.json_file}")
    print(f"⏱️  Responsiveness: {args.responsiveness}s")
    print(f"⚡ Acceleration: {args.acceleration} m/s²")
    print("\n💡 Tip: Add new commands to the file while this is running!")
    
    # Use default config if none specified
    config_path = args.config
    if not config_path:
        default_config = Path(__file__).parent.parent / "config" / "robot_config.yaml"
        if default_config.exists():
            config_path = str(default_config)
            print(f"📁 Using default config: {config_path}")
    
    # Initialize controller
    if config_path:
        controller = URRobotController(config_path=config_path)
    else:
        controller = URRobotController(
            robot_ip=args.robot_ip, 
            robot_type=args.robot_type
        )
    
    # Set movement parameters
    controller.default_acceleration = args.acceleration
    
    try:
        # Connect to robot
        if not controller.connect():
            print("❌ Failed to connect to robot")
            return 1
        
        print("✅ Connected to robot")
        
        # Initialize command processor
        processor = URCommandProcessor(controller)
        
        print("🚀 Starting streaming mode...")
        print("Press Ctrl+C to stop")
        
        # Process commands asynchronously
        processor.process_asynchronous_commands(
            args.json_file, 
            args.responsiveness
        )
        
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
