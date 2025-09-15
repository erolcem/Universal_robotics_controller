#!/usr/bin/env python3
"""
MIR Mission-Based UR Controller
Automatically executes UR functions based on MIR mission progress

Mission Flow: "FYP moving test"
1. P_start → pickup + compact
2. PL1 → home + dropoff1 + home + compact  
3. P_start → pickup + compact
4. PL2 → home + dropoff2 + home + compact
5. P_start → pickup + compact
6. PR1 → home + dropoff3_safe + home + compact
7. P_start → pickup + compact  
8. PR2 → home + dropoff4_safe + home + compact
9. Repeat cycle...
"""

import json
import time
import threading
import requests
from pathlib import Path
import re

class MIRMissionController:
    """Controls UR operations based on MIR mission status"""
    
    def __init__(self, mir_ip="118.138.107.60", ur_control_dir="control"):
        self.mir_ip = mir_ip
        self.mir_base_url = f"http://{mir_ip}/api/v2.0.0"
        self.ur_control_dir = Path(ur_control_dir)
        
        # Mission tracking
        self.monitoring = False
        self.current_mission = None
        self.last_position_name = ""
        self.mission_cycle_count = 0
        
        # Mission sequence definition
        self.mission_sequence = {
            "P_start": {
                "functions": ["pickup", "compact"],
                "description": "Pickup station - collect and compact"
            },
            "PL1": {
                "functions": ["home", "dropoff1", "home", "compact"],
                "description": "Left position 1 - dropoff and return"
            },
            "PL2": {
                "functions": ["home", "dropoff2", "home", "compact"], 
                "description": "Left position 2 - dropoff and return"
            },
            "PR1": {
                "functions": ["home", "dropoff3_safe", "home", "compact"],
                "description": "Right position 1 - safe dropoff and return"
            },
            "PR2": {
                "functions": ["home", "dropoff4_safe", "home", "compact"],
                "description": "Right position 2 - safe dropoff and return"
            }
        }
        
        # Expected mission cycle order
        self.cycle_order = [
            ("P_start", "pickup_1"),
            ("PL1", "dropoff_1"), 
            ("P_start", "pickup_2"),
            ("PL2", "dropoff_2"),
            ("P_start", "pickup_3"), 
            ("PR1", "dropoff_3"),
            ("P_start", "pickup_4"),
            ("PR2", "dropoff_4")
        ]
        self.cycle_position = 0
        
        # State tracking
        self.last_mission_text = ""
        self.position_triggers = set()
        self.operation_in_progress = False
        
    def get_mir_mission_status(self):
        """Get detailed MIR mission status"""
        try:
            # Get mission status
            response = requests.get(f"{self.mir_base_url}/mission_queue", timeout=5)
            missions = response.json() if response.status_code == 200 else []
            
            # Get current status
            status_response = requests.get(f"{self.mir_base_url}/status", timeout=5)
            status = status_response.json() if status_response.status_code == 200 else {}
            
            return {
                "missions": missions,
                "current_position": status.get("position", {}),
                "state_text": status.get("state_text", ""),
                "mission_text": status.get("mission_text", ""),
                "distance_to_next_target": status.get("distance_to_next_target", 0),
                "velocity": status.get("velocity", {}),
                "mission_queue_id": status.get("mission_queue_id", 0)
            }
        except Exception as e:
            print(f"❌ Error getting MIR status: {e}")
            return None
    
    def detect_position_arrival(self, mission_status):
        """Detect when MIR arrives at a specific position"""
        mission_text = mission_status.get("mission_text", "").lower()
        state_text = mission_status.get("state_text", "").lower()
        distance = mission_status.get("distance_to_next_target", float('inf'))
        
        # Look for position indicators in mission text
        position_patterns = {
            "p_start": ["p_start", "start", "pickup"],
            "pl1": ["pl1", "left_1", "left1"],
            "pl2": ["pl2", "left_2", "left2"], 
            "pr1": ["pr1", "right_1", "right1"],
            "pr2": ["pr2", "right_2", "right2"]
        }
        
        detected_position = None
        for position, patterns in position_patterns.items():
            for pattern in patterns:
                if pattern in mission_text or pattern in state_text:
                    detected_position = position.upper()
                    break
            if detected_position:
                break
        
        # Additional checks for arrival
        arrival_indicators = [
            distance < 0.2,  # Very close to target
            "reached" in state_text,
            "arrived" in state_text,
            "completed" in mission_text,
            "executing" in state_text and distance < 0.5
        ]
        
        if detected_position and any(arrival_indicators):
            return detected_position
        
        return None
    
    def execute_ur_sequence(self, position, sequence_functions):
        """Execute a sequence of UR functions for a position"""
        if self.operation_in_progress:
            print(f"⚠️  Operation already in progress, skipping {position}")
            return
            
        self.operation_in_progress = True
        
        try:
            print(f"\n🎯 EXECUTING SEQUENCE FOR {position}")
            print(f"📍 Location: {self.mission_sequence[position]['description']}")
            print(f"🤖 Functions: {' → '.join(sequence_functions)}")
            
            for i, ur_function in enumerate(sequence_functions, 1):
                print(f"\n{i}/{len(sequence_functions)} Executing: {ur_function}")
                
                # Send UR command with MIR pause
                self.send_ur_command(ur_function, pause_mir=True)
                
                # Wait for UR operation to complete
                self.wait_for_ur_completion()
                
                # Small delay between operations
                time.sleep(1)
            
            print(f"✅ Sequence complete for {position}")
            
            # Update cycle tracking
            self.advance_cycle_position(position)
            
        except Exception as e:
            print(f"❌ Error executing sequence for {position}: {e}")
        finally:
            self.operation_in_progress = False
    
    def send_ur_command(self, ur_function, speed=0.1, pause_mir=True):
        """Send command to UR system"""
        try:
            command_file = self.ur_control_dir / "robot_commands.txt"
            
            if pause_mir:
                command = f"add {ur_function} {speed} true\n"
            else:
                command = f"add {ur_function} {speed}\n"
            
            with open(command_file, "a") as f:
                f.write(command)
            
            print(f"✅ Sent: {command.strip()}")
            
            # Log operation
            log_file = self.ur_control_dir / "mission_log.txt"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, "a") as f:
                f.write(f"{timestamp}: {ur_function} triggered by MIR mission\n")
                
        except Exception as e:
            print(f"❌ Error sending UR command: {e}")
    
    def wait_for_ur_completion(self):
        """Wait for UR operation to complete by monitoring response file"""
        timeout = 60  # 60 second timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response_file = self.ur_control_dir / "robot_response.txt"
                if response_file.exists():
                    with open(response_file, "r") as f:
                        recent_lines = f.readlines()[-5:]  # Check last 5 lines
                    
                    # Look for completion indicators
                    for line in recent_lines:
                        if "completed" in line.lower() or "✅" in line:
                            return True
                
                time.sleep(0.5)
            except Exception:
                time.sleep(0.5)
        
        print("⚠️  Timeout waiting for UR completion")
        return False
    
    def advance_cycle_position(self, position):
        """Advance the cycle position tracker"""
        expected_position, operation_type = self.cycle_order[self.cycle_position]
        
        if position == expected_position:
            self.cycle_position = (self.cycle_position + 1) % len(self.cycle_order)
            print(f"📈 Cycle progress: {self.cycle_position}/{len(self.cycle_order)}")
            
            if self.cycle_position == 0:
                self.mission_cycle_count += 1
                print(f"🔄 Completed mission cycle #{self.mission_cycle_count}")
    
    def monitor_mission_loop(self):
        """Main monitoring loop for MIR missions"""
        print("🔍 Starting MIR mission monitoring...")
        print("🎯 Watching for 'FYP moving test' mission progress")
        print("📋 Mission sequence:")
        for pos, info in self.mission_sequence.items():
            print(f"   {pos}: {' → '.join(info['functions'])}")
        
        while self.monitoring:
            try:
                mission_status = self.get_mir_mission_status()
                if not mission_status:
                    time.sleep(2)
                    continue
                
                # Check if FYP moving test mission is active
                mission_text = mission_status.get("mission_text", "")
                if "fyp" not in mission_text.lower() and "moving" not in mission_text.lower():
                    time.sleep(1)
                    continue
                
                # Detect position arrival
                arrived_position = self.detect_position_arrival(mission_status)
                
                if arrived_position and arrived_position != self.last_position_name:
                    if arrived_position in self.mission_sequence:
                        self.last_position_name = arrived_position
                        
                        # Execute UR sequence for this position
                        sequence = self.mission_sequence[arrived_position]["functions"]
                        
                        # Execute in separate thread to avoid blocking
                        operation_thread = threading.Thread(
                            target=self.execute_ur_sequence,
                            args=(arrived_position, sequence)
                        )
                        operation_thread.start()
                
                # Show periodic status
                if hasattr(self, '_last_status_time'):
                    if time.time() - self._last_status_time > 15:
                        self._show_status(mission_status)
                else:
                    self._last_status_time = time.time()
                
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(3)
    
    def _show_status(self, mission_status):
        """Show periodic status updates"""
        mission_text = mission_status.get("mission_text", "")[:50]
        state_text = mission_status.get("state_text", "")[:30]
        distance = mission_status.get("distance_to_next_target", 0)
        
        print(f"📊 Status: {state_text} | Mission: {mission_text} | Dist: {distance:.2f}m | Cycle: {self.mission_cycle_count}")
        self._last_status_time = time.time()
    
    def start_monitoring(self):
        """Start mission monitoring"""
        if self.monitoring:
            print("⚠️  Already monitoring")
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_mission_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("✅ MIR mission monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        print("🛑 MIR mission monitoring stopped")
    
    def show_mission_status(self):
        """Show current mission status"""
        mission_status = self.get_mir_mission_status()
        if mission_status:
            print("📊 CURRENT MISSION STATUS:")
            print(f"   Mission: {mission_status.get('mission_text', 'None')}")
            print(f"   State: {mission_status.get('state_text', 'Unknown')}")
            print(f"   Distance to target: {mission_status.get('distance_to_next_target', 0):.2f}m")
            print(f"   Current cycle: {self.mission_cycle_count}")
            print(f"   Cycle position: {self.cycle_position}/{len(self.cycle_order)}")
            print(f"   Last position: {self.last_position_name}")


def main():
    """Interactive MIR mission controller"""
    print("🚀 MIR Mission-Based UR Controller")
    print("=" * 45)
    print("🎯 Designed for 'FYP moving test' mission")
    
    controller = MIRMissionController()
    
    print("\n📋 AVAILABLE COMMANDS:")
    print("   start    - Start mission monitoring")
    print("   stop     - Stop monitoring") 
    print("   status   - Show current mission status")
    print("   cycle    - Show cycle progress")
    print("   test     - Test UR command sending")
    print("   quit     - Exit")
    
    try:
        while True:
            cmd = input("\n🎯 Command: ").strip().lower()
            
            if cmd == "start":
                controller.start_monitoring()
            elif cmd == "stop":
                controller.stop_monitoring()
            elif cmd == "status":
                controller.show_mission_status()
            elif cmd == "cycle":
                print(f"📈 Mission cycles completed: {controller.mission_cycle_count}")
                print(f"📍 Current cycle position: {controller.cycle_position}/{len(controller.cycle_order)}")
                if controller.cycle_position < len(controller.cycle_order):
                    next_pos, next_op = controller.cycle_order[controller.cycle_position]
                    print(f"🎯 Next expected: {next_pos} ({next_op})")
            elif cmd == "test":
                controller.send_ur_command("home", pause_mir=False)
            elif cmd == "quit":
                break
            else:
                print("❌ Unknown command")
    
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop_monitoring()
        print("\n✅ MIR mission controller shut down")


if __name__ == "__main__":
    main()