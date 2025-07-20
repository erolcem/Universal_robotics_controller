#!/usr/bin/env python3
"""
UR Robot Controller Library

A Python library for controlling Universal Robots (UR) arms through RTDE.
Supports both simulation (URSim) and physical robots.

Author: Your Name
License: MIT
"""

import json
import time
import sys
import logging
from typing import List, Dict, Optional, Tuple, Any, TextIO
from pathlib import Path

try:
    import rtde_control
    import rtde_receive
except ImportError:
    print("ERROR: ur_rtde library not found. Please install with: pip install ur-rtde")
    sys.exit(1)

try:
    import yaml
except ImportError:
    print("WARNING: PyYAML not found. Configuration file support disabled.")
    yaml = None


class URRobotController:
    """Universal Robot controller supporting both simulation and physical robots."""
    
    def __init__(self, config_path: Optional[str] = None, robot_ip: str = "127.0.0.1", 
                 robot_type: str = "simulation", frequency: float = 500.0):
        """
        Initialize the UR Robot Controller.
        
        Args:
            config_path: Path to YAML configuration file
            robot_ip: IP address of the robot or simulator
            robot_type: "simulation" or "physical"
            frequency: RTDE communication frequency in Hz
        """
        self.config = {}
        self.robot_ip = robot_ip
        self.robot_type = robot_type
        self.frequency = frequency
        
        # Setup logging first
        self.setup_logging()
        
        # Load configuration if provided
        if config_path and yaml:
            self.load_config(config_path)
            self.robot_ip = self.config.get('robot', {}).get('ip', robot_ip)
            self.robot_type = self.config.get('robot', {}).get('type', robot_type)
            self.frequency = self.config.get('robot', {}).get('frequency', frequency)
        
        # RTDE interfaces
        self.rtde_c: Optional[rtde_control.RTDEControlInterface] = None
        self.rtde_r: Optional[rtde_receive.RTDEReceiveInterface] = None
        
        # Safety and movement settings
        self.max_velocity = self.config.get('physical', {}).get('safety', {}).get('max_velocity', 0.5)
        self.max_acceleration = self.config.get('physical', {}).get('safety', {}).get('max_acceleration', 1.0)
        self.default_speed = self.config.get('movement', {}).get('default_speed', 0.2)
        self.default_acceleration = self.config.get('movement', {}).get('default_acceleration', 0.5)
        
        self.logger.info(f"Initialized UR Controller for {robot_type} robot at {robot_ip}")
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            self.logger.info(f"Loaded configuration from {config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load config file {config_path}: {e}")
    
    def setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('URController')
    
    def connect(self) -> bool:
        """
        Connect to the robot via RTDE.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.logger.info(f"Connecting to robot at {self.robot_ip}...")
            
            # Initialize RTDE interfaces
            if self.robot_type == "physical":
                # For physical robots, use additional safety checks
                flags = rtde_control.RTDEControlInterface.FLAG_VERBOSE
            else:
                flags = 0
                
            self.rtde_c = rtde_control.RTDEControlInterface(self.robot_ip, self.frequency, flags)
            self.rtde_r = rtde_receive.RTDEReceiveInterface(self.robot_ip, self.frequency)
            
            # Check connections
            if not (self.rtde_c.isConnected() and self.rtde_r.isConnected()):
                self.logger.error("Failed to establish RTDE connections")
                return False
            
            self.logger.info("Successfully connected to robot")
            
            # Additional checks for physical robots
            if self.robot_type == "physical":
                return self._verify_physical_robot_safety()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def _verify_physical_robot_safety(self) -> bool:
        """Verify safety conditions for physical robot."""
        try:
            # Check robot mode
            robot_mode = self.rtde_r.getRobotMode()
            self.logger.info(f"Robot mode: {robot_mode}")
            
            # Check safety status
            safety_status = self.rtde_r.getSafetyMode()
            self.logger.info(f"Safety status: {safety_status}")
            
            # Additional safety checks can be added here
            # For example, checking joint limits, workspace limits, etc.
            
            return True
            
        except Exception as e:
            self.logger.error(f"Safety verification failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the robot."""
        if self.rtde_c:
            self.rtde_c.disconnect()
        if self.rtde_r:
            self.rtde_r.disconnect()
        self.logger.info("Disconnected from robot")
    
    def get_tcp_pose(self) -> Optional[List[float]]:
        """
        Get current TCP (Tool Center Point) pose.
        
        Returns:
            [x, y, z, rx, ry, rz] or None if failed
        """
        if not self.rtde_r:
            self.logger.error("Not connected to robot")
            return None
        
        try:
            return self.rtde_r.getActualTCPPose()
        except Exception as e:
            self.logger.error(f"Failed to get TCP pose: {e}")
            return None
    
    def move_linear(self, target_pose: List[float], speed: Optional[float] = None, 
                   acceleration: Optional[float] = None) -> bool:
        """
        Move robot linearly to target pose.
        
        Args:
            target_pose: [x, y, z, rx, ry, rz] in meters and radians
            speed: Linear speed in m/s
            acceleration: Linear acceleration in m/s²
            
        Returns:
            True if move command sent successfully
        """
        if not self.rtde_c:
            self.logger.error("Not connected to robot")
            return False
        
        speed = speed or self.default_speed
        acceleration = acceleration or self.default_acceleration
        
        # Safety checks for physical robots
        if self.robot_type == "physical":
            if not self._check_safety_limits(target_pose, speed, acceleration):
                return False
        
        try:
            self.logger.info(f"Moving to pose: {target_pose} at speed {speed}")
            self.rtde_c.moveL(target_pose, speed, acceleration)
            return True
        except Exception as e:
            self.logger.error(f"Move failed: {e}")
            return False
    
    def move_velocity(self, velocity: List[float], acceleration: Optional[float] = None, 
                     duration: float = 1.0) -> bool:
        """
        Apply velocity command to robot.
        
        Args:
            velocity: [vx, vy, vz, vrx, vry, vrz] in m/s and rad/s
            acceleration: Acceleration in m/s²
            duration: Duration to apply velocity in seconds
            
        Returns:
            True if velocity command sent successfully
        """
        if not self.rtde_c:
            self.logger.error("Not connected to robot")
            return False
        
        acceleration = acceleration or self.default_acceleration
        
        # Safety checks for physical robots
        if self.robot_type == "physical":
            if not self._check_velocity_limits(velocity, acceleration):
                return False
        
        try:
            self.rtde_c.speedL(velocity, acceleration, duration)
            return True
        except Exception as e:
            self.logger.error(f"Velocity move failed: {e}")
            return False
    
    def _check_safety_limits(self, target_pose: List[float], speed: float, 
                           acceleration: float) -> bool:
        """Check safety limits for physical robot movements."""
        # Check speed and acceleration limits
        if speed > self.max_velocity:
            self.logger.error(f"Speed {speed} exceeds maximum {self.max_velocity}")
            return False
        
        if acceleration > self.max_acceleration:
            self.logger.error(f"Acceleration {acceleration} exceeds maximum {self.max_acceleration}")
            return False
        
        # Check workspace limits if configured
        workspace = self.config.get('physical', {}).get('safety', {}).get('workspace_limits', {})
        if workspace:
            x, y, z = target_pose[:3]
            
            if 'x' in workspace and not (workspace['x'][0] <= x <= workspace['x'][1]):
                self.logger.error(f"X position {x} outside workspace limits {workspace['x']}")
                return False
            
            if 'y' in workspace and not (workspace['y'][0] <= y <= workspace['y'][1]):
                self.logger.error(f"Y position {y} outside workspace limits {workspace['y']}")
                return False
            
            if 'z' in workspace and not (workspace['z'][0] <= z <= workspace['z'][1]):
                self.logger.error(f"Z position {z} outside workspace limits {workspace['z']}")
                return False
        
        return True
    
    def _check_velocity_limits(self, velocity: List[float], acceleration: float) -> bool:
        """Check velocity limits for physical robot."""
        # Check if any velocity component exceeds limits
        linear_velocity = (velocity[0]**2 + velocity[1]**2 + velocity[2]**2)**0.5
        
        if linear_velocity > self.max_velocity:
            self.logger.error(f"Linear velocity {linear_velocity} exceeds maximum {self.max_velocity}")
            return False
        
        if acceleration > self.max_acceleration:
            self.logger.error(f"Acceleration {acceleration} exceeds maximum {self.max_acceleration}")
            return False
        
        return True
    
    def is_connected(self) -> bool:
        """Check if robot is connected."""
        return (self.rtde_c is not None and self.rtde_c.isConnected() and 
                self.rtde_r is not None and self.rtde_r.isConnected())
    
    def emergency_stop(self) -> bool:
        """Emergency stop the robot."""
        if not self.rtde_c:
            return False
        
        try:
            self.rtde_c.stopL(2.0)  # Stop with 2 m/s² deceleration
            self.logger.warning("Emergency stop activated")
            return True
        except Exception as e:
            self.logger.error(f"Emergency stop failed: {e}")
            return False


class URCommandProcessor:
    """Process JSON command files for robot control."""
    
    def __init__(self, controller: URRobotController):
        """Initialize with a robot controller."""
        self.controller = controller
        self.logger = logging.getLogger('URCommandProcessor')
    
    def process_synchronous_commands(self, json_file: str, log_file: Optional[str] = None,
                                   responsiveness: float = 1.0) -> None:
        """
        Process commands from JSON file synchronously.
        
        Args:
            json_file: Path to JSONL file with delta commands
            log_file: Optional log file path
            responsiveness: Time between commands in seconds
        """
        if not self.controller.is_connected():
            self.logger.error("Robot not connected")
            return
        
        log_f = None
        if log_file:
            log_f = open(log_file, 'a')
        
        try:
            with open(json_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    
                    try:
                        cmd = json.loads(line)
                        if self._execute_delta_command(cmd, log_f):
                            time.sleep(responsiveness)
                        else:
                            self.logger.error(f"Failed to execute command on line {line_num}")
                            break
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON on line {line_num}: {e}")
                        continue
                        
        except FileNotFoundError:
            self.logger.error(f"Command file not found: {json_file}")
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        finally:
            if log_f:
                log_f.close()
    
    def process_asynchronous_commands(self, json_file: str, responsiveness: float = 1.0) -> None:
        """
        Process commands from JSON file asynchronously (streaming).
        
        Args:
            json_file: Path to JSONL file
            responsiveness: Time between checks in seconds
        """
        if not self.controller.is_connected():
            self.logger.error("Robot not connected")
            return
        
        try:
            # Open file and seek to end
            with open(json_file, 'r') as f:
                f.seek(0, 2)  # Seek to end
                
                current_velocity = [0.0] * 6
                
                while True:
                    # Read new lines
                    lines = f.readlines()
                    if lines:
                        try:
                            # Use the last command
                            cmd = json.loads(lines[-1])
                            current_velocity = [
                                float(cmd.get('dx', 0.0)),
                                float(cmd.get('dy', 0.0)),
                                float(cmd.get('dz', 0.0)),
                                float(cmd.get('drx', 0.0)),
                                float(cmd.get('dry', 0.0)),
                                float(cmd.get('drz', 0.0))
                            ]
                        except (json.JSONDecodeError, ValueError) as e:
                            self.logger.error(f"Invalid command: {e}")
                    
                    # Apply current velocity
                    self.logger.debug(f"Applying velocity: {current_velocity}")
                    self.controller.move_velocity(current_velocity, duration=responsiveness)
                    time.sleep(responsiveness)
                    
        except FileNotFoundError:
            self.logger.error(f"Command file not found: {json_file}")
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
    
    def _execute_delta_command(self, cmd: Dict, log_f: Optional[TextIO] = None) -> bool:
        """Execute a delta movement command."""
        try:
            # Extract delta values
            dx = float(cmd.get('dx', 0.0))
            dy = float(cmd.get('dy', 0.0))
            dz = float(cmd.get('dz', 0.0))
            drx = float(cmd.get('drx', 0.0))
            dry = float(cmd.get('dry', 0.0))
            drz = float(cmd.get('drz', 0.0))
            
            # Get current pose
            current_pose = self.controller.get_tcp_pose()
            if current_pose is None:
                return False
            
            # Calculate target pose
            target_pose = [
                current_pose[0] + dx,
                current_pose[1] + dy,
                current_pose[2] + dz,
                current_pose[3] + drx,
                current_pose[4] + dry,
                current_pose[5] + drz
            ]
            
            # Log command
            if log_f:
                log_entry = {
                    'timestamp': time.time(),
                    'target_pose': target_pose,
                    'delta': [dx, dy, dz, drx, dry, drz]
                }
                log_f.write(json.dumps(log_entry) + '\n')
                log_f.flush()
            
            # Execute movement
            velocity = [dx, dy, dz, drx, dry, drz]
            return self.controller.move_velocity(velocity)
            
        except (ValueError, KeyError) as e:
            self.logger.error(f"Invalid command format: {e}")
            return False


def create_default_config(config_path: str) -> None:
    """Create a default configuration file."""
    config_template_path = Path(__file__).parent.parent / "config" / "robot_config_template.yaml"
    
    if config_template_path.exists():
        import shutil
        shutil.copy(config_template_path, config_path)
        print(f"Created default configuration at {config_path}")
    else:
        print(f"Template configuration not found at {config_template_path}")


if __name__ == "__main__":
    # Basic test of the library
    controller = URRobotController()
    
    if controller.connect():
        print("Connection successful!")
        pose = controller.get_tcp_pose()
        print(f"Current TCP pose: {pose}")
        controller.disconnect()
    else:
        print("Connection failed!")
