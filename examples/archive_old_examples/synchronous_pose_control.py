#!/usr/bin/env python3
"""
UR Robot Synchronous Pose Control

Executes absolute pose commands from a JSONL file sequentially with fixed timing.
Each line in the file represents an absolute pose target (x, y, z, rx, ry, rz).

Usage:
    python examples/synchronous_pose_control.py [options]
"""

import sys
import argparse
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ur_controller import URRobotController, URCommandProcessor


def main():
    """Main synchronous pose control function."""
    parser = argparse.ArgumentParser(
        description="Execute absolute pose movements with fixed timing"
    )
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--robot-ip", default="127.0.0.1", help="Robot IP address")
    parser.add_argument("--robot-type", choices=["simulation", "physical"], 
                       default="simulation", help="Robot type")
    parser.add_argument("--json-source", default="examples/synchronous_poses.jsonl",
                       help="Path to JSONL file with pose commands")
    parser.add_argument("--json-log", help="Path to log file (optional)")
    parser.add_argument("--speed", type=float, default=0.2, help="Movement speed (m/s)")
    parser.add_argument("--acceleration", type=float, default=0.5, 
                       help="Movement acceleration (m/s²)")
    parser.add_argument("--responsiveness", type=float, default=2.0,
                       help="Time between commands (seconds)")
    
    args = parser.parse_args()
    
    print("🤖 UR Robot Controller - Synchronous Pose Mode")
    print("=" * 45)
    print(f"📁 Command file: {args.json_source}")
    print(f"⏱️  Responsiveness: {args.responsiveness}s")
    print(f"🏃 Speed: {args.speed} m/s")
    print(f"⚡ Acceleration: {args.acceleration} m/s²")
    
    # Check if command file exists
    if not Path(args.json_source).exists():
        print(f"❌ Error: Command file '{args.json_source}' not found!")
        return 1
    
    # Use default config if none specified
    config_path = args.config
    if not config_path:
        default_config = Path(__file__).parent.parent / "config" / "robot_config.yaml"
        if default_config.exists():
            config_path = str(default_config)
            print(f"📋 Using default config: {config_path}")
    
    print("\n🔄 Initializing robot controller...")
    
    # Initialize robot controller
    controller = URRobotController(
        config_path=config_path,
        robot_ip=args.robot_ip,
        robot_type=args.robot_type
    )
    
    # Configure movement parameters
    controller.default_speed = args.speed
    controller.default_acceleration = args.acceleration
    
    print("🔌 Connecting to robot...")
    if not controller.connect():
        print("❌ Failed to connect to robot!")
        return 1
    
    print("✅ Connected successfully!")
    
    # Get initial pose
    initial_pose = controller.get_tcp_pose()
    if initial_pose:
        print(f"📍 Initial TCP pose: [{initial_pose[0]:.3f}, {initial_pose[1]:.3f}, "
              f"{initial_pose[2]:.3f}, {initial_pose[3]:.3f}, {initial_pose[4]:.3f}, {initial_pose[5]:.3f}]")
    
    print(f"\n🎯 Starting pose sequence from '{args.json_source}'...")
    print("Press Ctrl+C to stop")
    print("-" * 45)
    
    try:
        # Initialize command processor
        processor = URCommandProcessor(controller)
        
        # Process pose commands
        processor.process_synchronous_poses(
            json_file=args.json_source,
            log_file=args.json_log,
            responsiveness=args.responsiveness
        )
        
    except KeyboardInterrupt:
        print("\n⏹️  Stopping robot...")
        controller.emergency_stop()
    except Exception as e:
        print(f"\n❌ Error during operation: {e}")
        controller.emergency_stop()
    finally:
        # Get final pose
        final_pose = controller.get_tcp_pose()
        if final_pose:
            print(f"📍 Final TCP pose: [{final_pose[0]:.3f}, {final_pose[1]:.3f}, "
                  f"{final_pose[2]:.3f}, {final_pose[3]:.3f}, {final_pose[4]:.3f}, {final_pose[5]:.3f}]")
        
        print("🔌 Disconnecting...")
        controller.disconnect()
        print("✅ Operation completed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
