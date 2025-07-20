#!/usr/bin/env python3
"""
UR Robot Example Script

Demonstrates basic connection and movement capabilities.
Works with both simulation and physical robots.

Usage:
    python examples/basic_example.py [--config config.yaml] [--robot-ip IP] [--robot-type TYPE]
"""

import sys
import argparse
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from ur_controller import URRobotController


def test_basic_connection(controller: URRobotController) -> bool:
    """Test basic connection to robot."""
    print("Testing basic connection...")
    
    if not controller.connect():
        print("❌ Connection failed!")
        return False
    
    print("✅ Connection successful!")
    
    # Get current pose
    pose = controller.get_tcp_pose()
    if pose:
        print(f"📍 Current TCP pose: {[round(p, 3) for p in pose]}")
    else:
        print("❌ Failed to get TCP pose")
        return False
    
    return True


def test_basic_movements(controller: URRobotController) -> bool:
    """Test basic robot movements."""
    print("\nTesting basic movements...")
    
    # Get initial pose
    initial_pose = controller.get_tcp_pose()
    if not initial_pose:
        print("❌ Failed to get initial pose")
        return False
    
    print(f"📍 Initial pose: {[round(p, 3) for p in initial_pose]}")
    
    # Test small movements
    movements = [
        ("Moving +10cm in X", [0.1, 0.0, 0.0, 0.0, 0.0, 0.0]),
        ("Moving back to start", [-0.1, 0.0, 0.0, 0.0, 0.0, 0.0]),
        ("Moving +5cm in Y", [0.0, 0.05, 0.0, 0.0, 0.0, 0.0]),
        ("Moving back to start", [0.0, -0.05, 0.0, 0.0, 0.0, 0.0]),
    ]
    
    for description, delta in movements:
        print(f"🔄 {description}...")
        
        # Calculate target pose
        target_pose = [initial_pose[i] + delta[i] for i in range(6)]
        
        # Execute movement
        if controller.move_linear(target_pose, speed=0.1):
            time.sleep(2)  # Wait for movement to complete
            print("✅ Movement completed")
        else:
            print("❌ Movement failed")
            return False
    
    print("✅ All movements completed successfully!")
    return True


def test_velocity_control(controller: URRobotController) -> bool:
    """Test velocity control."""
    print("\nTesting velocity control...")
    
    # Test different velocities
    velocities = [
        ("Moving left at 5cm/s", [-0.05, 0.0, 0.0, 0.0, 0.0, 0.0]),
        ("Moving right at 5cm/s", [0.05, 0.0, 0.0, 0.0, 0.0, 0.0]),
        ("Stopping", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    ]
    
    for description, velocity in velocities:
        print(f"🔄 {description}...")
        
        if controller.move_velocity(velocity, duration=2.0):
            time.sleep(2.5)  # Wait for movement
            print("✅ Velocity command completed")
        else:
            print("❌ Velocity command failed")
            return False
    
    print("✅ Velocity control test completed!")
    return True


def main():
    """Main example function."""
    parser = argparse.ArgumentParser(description="UR Robot Basic Example")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--robot-ip", default="127.0.0.1", help="Robot IP address")
    parser.add_argument("--robot-type", choices=["simulation", "physical"], 
                       default="simulation", help="Robot type")
    parser.add_argument("--skip-movements", action="store_true", 
                       help="Skip movement tests (connection only)")
    
    args = parser.parse_args()
    
    print("🤖 UR Robot Controller - Basic Example")
    print("=" * 40)
    
    # Initialize controller
    if args.config:
        controller = URRobotController(config_path=args.config)
    else:
        controller = URRobotController(
            robot_ip=args.robot_ip, 
            robot_type=args.robot_type
        )
    
    try:
        # Test connection
        if not test_basic_connection(controller):
            return 1
        
        if not args.skip_movements:
            # Test movements
            if not test_basic_movements(controller):
                return 1
            
            # Test velocity control
            if not test_velocity_control(controller):
                return 1
        
        print("\n🎉 All tests completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    finally:
        controller.disconnect()
        print("👋 Disconnected from robot")


if __name__ == "__main__":
    sys.exit(main())
