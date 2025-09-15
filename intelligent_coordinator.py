#!/usr/bin/env python3
"""
Intelligent MIR-UR Coordination System
Monitors MIR position and automatically triggers UR functions when MIR reaches targets

Features:
- Monitor MIR position in real-time
- Detect when MIR reaches predefined target locations
- Automatically pause MIR and execute appropriate UR function
- Resume MIR after UR operation completes
- Smart location-to-function mapping
"""

import json
import time
import threading
import requests
from pathlib import Path
import sys

# Import our unified control system
sys.path.append(str(Path(__file__).parent))
from unified_robot_control_simple import EnhancedRobotController

class IntelligentCoordinator:
    """Intelligent coordinator that manages MIR-UR workflows"""
    
    def __init__(self, robot_controller, mir_ip="118.138.127.231"):
        self.robot = robot_controller
        self.mir_ip = mir_ip
        self.mir_base_url = f"http://{mir_ip}/api/v2.0.0"
        
        # Target locations and their associated UR functions
        self.target_locations = {
            "pickup_station": {
                "position": {"x": 1.0, "y": 2.0},  # Adjust to your actual coordinates
                "tolerance": 0.3,  # Distance tolerance in meters
                "ur_function": "pickup",
                "description": "Pickup station - collect pipes"
            },
            "dropoff_left_1": {
                "position": {"x": 5.0, "y": 1.0},  # Adjust coordinates
                "tolerance": 0.3,
                "ur_function": "dropoff3_safe", 
                "description": "Left scaffold position 1"
            },
            "dropoff_left_2": {
                "position": {"x": 5.0, "y": 3.0},  # Adjust coordinates
                "tolerance": 0.3,
                "ur_function": "dropoff4_safe",
                "description": "Left scaffold position 2"
            },
            "dropoff_right_1": {
                "position": {"x": 7.0, "y": 1.0},  # Adjust coordinates
                "tolerance": 0.3,
                "ur_function": "dropoff1",
                "description": "Right scaffold position 1"
            },
            "dropoff_right_2": {
                "position": {"x": 7.0, "y": 3.0},  # Adjust coordinates
                "tolerance": 0.3,
                "ur_function": "dropoff2",
                "description": "Right scaffold position 2"
            }
        }
        
        # State tracking
        self.monitoring = False
        self.last_position = None
        self.current_target = None
        self.operation_in_progress = False
        
        # Monitoring thread
        self.monitor_thread = None
        
    def get_mir_position(self):
        """Get current MIR position"""
        try:
            response = requests.get(f"{self.mir_base_url}/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                return {
                    "x": status.get("position", {}).get("x", 0),
                    "y": status.get("position", {}).get("y", 0),
                    "orientation": status.get("position", {}).get("orientation", 0)
                }
        except Exception as e:
            print(f"❌ Error getting MIR position: {e}")
        return None
    
    def get_mir_mission_status(self):
        """Get MIR mission status to detect when it reaches targets"""
        try:
            response = requests.get(f"{self.mir_base_url}/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                return {
                    "state_text": status.get("state_text", ""),
                    "mission_text": status.get("mission_text", ""),
                    "distance_to_next_target": status.get("distance_to_next_target", float('inf'))
                }
        except Exception as e:
            print(f"❌ Error getting MIR mission status: {e}")
        return None
    
    def distance_to_target(self, pos1, pos2):
        """Calculate distance between two positions"""
        if not pos1 or not pos2:
            return float('inf')
        return ((pos1["x"] - pos2["x"])**2 + (pos1["y"] - pos2["y"])**2)**0.5
    
    def find_nearby_target(self, current_pos):
        """Find if MIR is near any target location"""
        if not current_pos:
            return None
            
        for target_name, target_info in self.target_locations.items():
            distance = self.distance_to_target(current_pos, target_info["position"])
            if distance <= target_info["tolerance"]:
                return target_name, target_info
        return None
    
    def execute_coordinated_operation(self, target_name, target_info):
        """Execute coordinated MIR pause + UR function + MIR resume"""
        if self.operation_in_progress:
            return
            
        self.operation_in_progress = True
        print(f"🎯 TARGET REACHED: {target_name}")
        print(f"📍 Location: {target_info['description']}")
        
        try:
            # Step 1: Pause MIR
            print("🚁 Pausing MIR...")
            if self.robot.mir_enabled:
                self.robot.mir_control.pause()
            time.sleep(1)  # Let MIR settle
            
            # Step 2: Execute UR function
            print(f"🤖 Executing UR function: {target_info['ur_function']}")
            self.robot._add_function_to_queue(
                target_info['ur_function'], 
                speed=0.1, 
                pause_mir=False  # MIR already paused
            )
            
            # Step 3: Wait for UR to complete
            print("⏳ Waiting for UR operation to complete...")
            while not self.robot.ur_queue.empty() or self.robot.ur_executing:
                time.sleep(0.5)
            
            # Step 4: Resume MIR
            print("🚁 Resuming MIR...")
            if self.robot.mir_enabled:
                self.robot.mir_control.resume()
            
            print(f"✅ Coordinated operation complete at {target_name}")
            
        except Exception as e:
            print(f"❌ Error in coordinated operation: {e}")
            # Try to resume MIR in case of error
            if self.robot.mir_enabled:
                try:
                    self.robot.mir_control.resume()
                except:
                    pass
        finally:
            self.operation_in_progress = False
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print("🔍 Starting intelligent MIR-UR coordination...")
        print("📍 Monitoring target locations:")
        for name, info in self.target_locations.items():
            print(f"   • {name}: {info['description']} → {info['ur_function']}")
        
        while self.monitoring:
            try:
                # Get current MIR position
                current_pos = self.get_mir_position()
                if not current_pos:
                    time.sleep(1)
                    continue
                
                # Check if near any target
                target_result = self.find_nearby_target(current_pos)
                if target_result:
                    target_name, target_info = target_result
                    
                    # Only trigger if this is a new target (avoid repeated triggers)
                    if self.current_target != target_name:
                        self.current_target = target_name
                        # Execute coordinated operation in separate thread
                        operation_thread = threading.Thread(
                            target=self.execute_coordinated_operation,
                            args=(target_name, target_info)
                        )
                        operation_thread.start()
                else:
                    # Not near any target
                    self.current_target = None
                
                self.last_position = current_pos
                time.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(2)
    
    def start_monitoring(self):
        """Start the intelligent monitoring system"""
        if self.monitoring:
            print("⚠️  Monitoring already running")
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("✅ Intelligent coordination started")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("🛑 Intelligent coordination stopped")
    
    def update_target_location(self, target_name, x, y, tolerance=0.3):
        """Update a target location's coordinates"""
        if target_name in self.target_locations:
            self.target_locations[target_name]["position"] = {"x": x, "y": y}
            self.target_locations[target_name]["tolerance"] = tolerance
            print(f"✅ Updated {target_name} location to ({x}, {y}) ±{tolerance}m")
        else:
            print(f"❌ Target '{target_name}' not found")
    
    def add_target_location(self, target_name, x, y, ur_function, description, tolerance=0.3):
        """Add a new target location"""
        self.target_locations[target_name] = {
            "position": {"x": x, "y": y},
            "tolerance": tolerance,
            "ur_function": ur_function,
            "description": description
        }
        print(f"✅ Added target '{target_name}' at ({x}, {y}) → {ur_function}")
    
    def show_status(self):
        """Show current coordination status"""
        print("📊 INTELLIGENT COORDINATION STATUS:")
        print(f"   Monitoring: {'🟢 Active' if self.monitoring else '🔴 Stopped'}")
        print(f"   Current Target: {self.current_target or 'None'}")
        print(f"   Operation in Progress: {'🟢 Yes' if self.operation_in_progress else '🔴 No'}")
        
        if self.last_position:
            print(f"   MIR Position: ({self.last_position['x']:.2f}, {self.last_position['y']:.2f})")
        
        print(f"   Configured Targets: {len(self.target_locations)}")


def main():
    """Test the intelligent coordination system"""
    print("🚀 Intelligent MIR-UR Coordination System")
    print("=" * 50)
    
    # Initialize robot controller
    robot = EnhancedRobotController(
        robot_ip="192.168.1.6",
        mir_ip="118.138.127.231"  # Your MIR IP
    )
    
    # Initialize intelligent coordinator
    coordinator = IntelligentCoordinator(robot, mir_ip="118.138.127.231")
    
    print("\n📋 AVAILABLE COMMANDS:")
    print("   start    - Start intelligent monitoring")
    print("   stop     - Stop monitoring")
    print("   status   - Show system status")
    print("   update <target> <x> <y> - Update target coordinates")
    print("   add <name> <x> <y> <function> <description> - Add new target")
    print("   targets  - Show all configured targets")
    print("   quit     - Exit")
    
    try:
        while True:
            cmd = input("\n🎯 Command: ").strip().lower()
            
            if cmd == "start":
                coordinator.start_monitoring()
            elif cmd == "stop":
                coordinator.stop_monitoring()
            elif cmd == "status":
                coordinator.show_status()
            elif cmd == "targets":
                print("📍 CONFIGURED TARGETS:")
                for name, info in coordinator.target_locations.items():
                    pos = info["position"]
                    print(f"   • {name}: ({pos['x']}, {pos['y']}) → {info['ur_function']}")
            elif cmd.startswith("update"):
                parts = cmd.split()
                if len(parts) >= 4:
                    coordinator.update_target_location(parts[1], float(parts[2]), float(parts[3]))
                else:
                    print("Usage: update <target> <x> <y>")
            elif cmd.startswith("add"):
                parts = cmd.split()
                if len(parts) >= 6:
                    coordinator.add_target_location(parts[1], float(parts[2]), float(parts[3]), 
                                                  parts[4], " ".join(parts[5:]))
                else:
                    print("Usage: add <name> <x> <y> <function> <description>")
            elif cmd == "quit":
                break
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
    
    except KeyboardInterrupt:
        pass
    finally:
        coordinator.stop_monitoring()
        print("\n✅ Intelligent coordination system shut down")


if __name__ == "__main__":
    main()