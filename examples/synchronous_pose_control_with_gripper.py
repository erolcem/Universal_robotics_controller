#!/usr/bin/env python3
"""
UR Robot Synchronous Pose Control with Gripper

Executes absolute pose commands with gripper control from a JSONL file sequentially 
with fixed timing. Each line in the file represents an absolute pose target 
(x, y, z, rx, ry, rz) with optional gripper control (0=open, 1=closed).

Usage:
    python examples/synchronous_pose_control_with_gripper.py [options]
"""

import sys
import argparse
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ur_controller import URRobotController, URCommandProcessor


def main():
    """Main synchronous pose control with gripper function."""
    parser = argparse.ArgumentParser(
        description="Execute absolute pose movements with gripper control and fixed timing"
    )
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--robot-ip", default="127.0.0.1", help="Robot IP address")
    parser.add_argument("--robot-type", choices=["simulation", "physical"], 
                       default="simulation", help="Robot type")
    parser.add_argument("--json-source", default="examples/synchronous_poses_with_gripper.jsonl",
                       help="Path to JSONL file with pose and gripper commands")
    parser.add_argument("--json-log", help="Path to log file (optional)")
    parser.add_argument("--speed", type=float, default=0.2, help="Movement speed (m/s)")
    parser.add_argument("--acceleration", type=float, default=0.5, 
                       help="Movement acceleration (m/s²)")
    parser.add_argument("--responsiveness", type=float, default=2.0,
                       help="Time between commands (seconds)")
    parser.add_argument("--gripper-pin", type=int, default=0,
                       help="Digital output pin for gripper control (default: 0)")
    parser.add_argument("--no-gripper", action="store_true",
                       help="Skip gripper initialization and control (pose-only mode)")
    
    args = parser.parse_args()
    
    print("🤖 UR Robot Controller - Synchronous Pose + Gripper Mode")
    print("=" * 55)
    print(f"📁 Command file: {args.json_source}")
    print(f"⏱️  Responsiveness: {args.responsiveness}s")
    print(f"🏃 Speed: {args.speed} m/s")
    print(f"⚡ Acceleration: {args.acceleration} m/s²")
    if not args.no_gripper:
        print(f"🤏 Gripper pin: Digital Output {args.gripper_pin}")
    else:
        print("🤏 Gripper control: DISABLED (pose-only mode)")
    
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
    
    # Initialize gripper to open state (optional - continue if fails)
    gripper_available = False
    if not args.no_gripper:
        print("🤏 Initializing gripper to open state...")
        try:
            if controller.set_gripper(0, args.gripper_pin):
                print("✅ Gripper initialized (open)")
                gripper_available = True
            else:
                print("⚠️  Gripper initialization failed - continuing without gripper control")
                gripper_available = False
        except Exception as e:
            print(f"⚠️  Gripper not available ({e}) - continuing with pose-only control")
            gripper_available = False
        
        # Get initial gripper state if feedback is available
        if gripper_available:
            try:
                initial_gripper_state = controller.get_gripper_state(args.gripper_pin)
                if initial_gripper_state is not None:
                    print(f"🤏 Initial gripper state: {'Closed' if initial_gripper_state else 'Open'}")
                else:
                    print("🤏 Gripper feedback not available")
            except Exception as e:
                print(f"🤏 Gripper feedback error: {e}")
    else:
        print("🤏 Gripper control disabled by user (--no-gripper)")
    
    print(f"\n🎯 Starting pose + gripper sequence from '{args.json_source}'...")
    if gripper_available:
        print("💡 Commands include both pose and gripper control (0=open, 1=closed)")
    else:
        print("💡 Gripper control disabled - executing pose commands only")
    print("Press Ctrl+C to stop")
    print("-" * 55)
    
    try:
        # Initialize command processor
        processor = URCommandProcessor(controller)
        
        # Process pose and gripper commands
        processor.process_synchronous_poses_with_gripper(
            json_file=args.json_source,
            log_file=args.json_log,
            responsiveness=args.responsiveness
        )
        
    except KeyboardInterrupt:
        print("\n⏹️  Stopping robot...")
        controller.emergency_stop()
        # Open gripper on emergency stop if available
        if gripper_available:
            controller.set_gripper(0, args.gripper_pin)
    except Exception as e:
        print(f"\n❌ Error during operation: {e}")
        controller.emergency_stop()
        # Open gripper on error if available
        if gripper_available:
            controller.set_gripper(0, args.gripper_pin)
    finally:
        # Get final pose and gripper state
        final_pose = controller.get_tcp_pose()
        if final_pose:
            print(f"📍 Final TCP pose: [{final_pose[0]:.3f}, {final_pose[1]:.3f}, "
                  f"{final_pose[2]:.3f}, {final_pose[3]:.3f}, {final_pose[4]:.3f}, {final_pose[5]:.3f}]")
        
        if gripper_available:
            final_gripper_state = controller.get_gripper_state(args.gripper_pin)
            if final_gripper_state is not None:
                print(f"🤏 Final gripper state: {'Closed' if final_gripper_state else 'Open'}")
            
            # Ensure gripper is open before disconnecting
            print("🤏 Ensuring gripper is open before disconnecting...")
            controller.set_gripper(0, args.gripper_pin)
        
        print("🔌 Disconnecting...")
        controller.disconnect()
        print("✅ Operation completed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
