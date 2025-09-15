#!/usr/bin/env python3
"""
MIR Target Detection System
Monitors MIR position and detects when it reaches target locations
Integrates with existing UR robot control system

Usage:
1. Set goals via MIR website as usual
2. Run this script to monitor when MIR reaches targets
3. Automatically triggers UR operations when targets are reached
"""

import json
import time
import threading
import requests
from pathlib import Path
import sys

class MIRTargetDetector:
    """Detects when MIR reaches target positions and triggers UR operations"""
    
    def __init__(self, mir_ip="118.138.107.60", ur_control_dir="control"):
        self.mir_ip = mir_ip
        self.mir_base_url = f"http://{mir_ip}/api/v2.0.0"
        self.ur_control_dir = Path(ur_control_dir)
        
        # Ensure control directory exists
        self.ur_control_dir.mkdir(exist_ok=True)
        
        # State tracking
        self.monitoring = False
        self.last_position = None
        self.last_mission_text = ""
        self.last_state_text = ""
        self.position_stable_count = 0
        self.position_threshold = 0.1  # Position change threshold in meters
        self.stable_required = 5       # Number of stable readings required
        
        # Target detection settings
        self.target_mappings = {
            # You can customize these based on your actual mission names or positions
            "pickup": "pickup",
            "dropoff": "dropoff1",  # Default dropoff
            "left": "dropoff3_safe",
            "right": "dropoff1", 
            "home": "home"
        }
        
    def get_mir_status(self):
        """Get comprehensive MIR status"""
        try:
            response = requests.get(f"{self.mir_base_url}/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                return {
                    "position": {
                        "x": status.get("position", {}).get("x", 0),
                        "y": status.get("position", {}).get("y", 0),
                        "orientation": status.get("position", {}).get("orientation", 0)
                    },
                    "state_text": status.get("state_text", ""),
                    "mission_text": status.get("mission_text", ""),
                    "distance_to_next_target": status.get("distance_to_next_target", 0),
                    "battery_percentage": status.get("battery_percentage", 0),
                    "velocity": {
                        "linear": status.get("velocity", {}).get("linear", 0),
                        "angular": status.get("velocity", {}).get("angular", 0)
                    }
                }
        except Exception as e:
            print(f"❌ Error getting MIR status: {e}")
        return None
    
    def position_distance(self, pos1, pos2):
        """Calculate distance between two positions"""
        if not pos1 or not pos2:
            return float('inf')
        return ((pos1["x"] - pos2["x"])**2 + (pos1["y"] - pos2["y"])**2)**0.5
    
    def is_position_stable(self, current_pos):
        """Check if MIR position is stable (not moving)"""
        if not self.last_position:
            self.last_position = current_pos
            return False
            
        distance = self.position_distance(current_pos, self.last_position)
        
        if distance < self.position_threshold:
            self.position_stable_count += 1
        else:
            self.position_stable_count = 0
            
        self.last_position = current_pos
        return self.position_stable_count >= self.stable_required
    
    def detect_target_reached(self, status):
        """Detect if MIR has reached a target based on various indicators"""
        triggers = []
        
        # Method 1: Check if position is stable and mission text indicates arrival
        if self.is_position_stable(status["position"]):
            mission_text = status["mission_text"].lower()
            state_text = status["state_text"].lower()
            
            # Common MIR mission completion indicators
            completion_indicators = [
                "completed", "reached", "arrived", "finished", 
                "done", "success", "target", "goal"
            ]
            
            for indicator in completion_indicators:
                if indicator in mission_text or indicator in state_text:
                    triggers.append(f"Mission indicator: {indicator}")
                    break
        
        # Method 2: Check if distance to next target is very small (< 0.1m)
        if status["distance_to_next_target"] < 0.1:
            triggers.append("Close to target (< 0.1m)")
        
        # Method 3: Check if MIR velocity is near zero (stopped)
        linear_vel = status["velocity"]["linear"]
        angular_vel = status["velocity"]["angular"]
        if abs(linear_vel) < 0.05 and abs(angular_vel) < 0.05:
            if self.position_stable_count >= self.stable_required:
                triggers.append("Stopped and stable")
        
        # Method 4: State text analysis
        state_text = status["state_text"].lower()
        if "ready" in state_text or "idle" in state_text or "paused" in state_text:
            if self.position_stable_count >= self.stable_required:
                triggers.append("Ready/Idle state")
        
        return triggers
    
    def determine_ur_function(self, status):
        """Determine which UR function to execute based on MIR status"""
        mission_text = status["mission_text"].lower()
        position = status["position"]
        
        # Try to match mission text to functions
        for keyword, ur_function in self.target_mappings.items():
            if keyword in mission_text:
                return ur_function
        
        # Fallback: Use position-based logic (you can customize coordinates)
        x, y = position["x"], position["y"]
        
        if abs(x) < 1.0 and abs(y) < 1.0:  # Near origin
            return "home"
        elif x < 3.0:  # Left side of workspace
            return "pickup"
        elif x > 6.0:  # Right side
            return "dropoff1"
        else:  # Middle area
            return "dropoff3_safe"
    
    def send_ur_command(self, ur_function):
        """Send command to UR robot control system"""
        try:
            # Write to the UR control file
            command_file = self.ur_control_dir / "robot_commands.txt"
            
            # Add the function with MIR pause
            command = f"add {ur_function} 0.1 true\n"
            
            with open(command_file, "a") as f:
                f.write(command)
            
            print(f"✅ Sent UR command: {command.strip()}")
            
            # Also log the operation
            log_file = self.ur_control_dir / "coordination_log.txt"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, "a") as f:
                f.write(f"{timestamp}: MIR target reached → UR function '{ur_function}'\n")
                
        except Exception as e:
            print(f"❌ Error sending UR command: {e}")
    
    def monitor_loop(self):
        """Main monitoring loop"""
        print("🔍 Starting MIR target detection...")
        print(f"📡 Monitoring MIR at: {self.mir_ip}")
        print("🎯 Will trigger UR operations when targets are reached")
        
        while self.monitoring:
            try:
                status = self.get_mir_status()
                if not status:
                    time.sleep(1)
                    continue
                
                # Check for target arrival
                triggers = self.detect_target_reached(status)
                
                if triggers:
                    # Determine appropriate UR function
                    ur_function = self.determine_ur_function(status)
                    
                    print(f"\n🎯 TARGET DETECTED!")
                    print(f"   Position: ({status['position']['x']:.2f}, {status['position']['y']:.2f})")
                    print(f"   Mission: {status['mission_text']}")
                    print(f"   State: {status['state_text']}")
                    print(f"   Triggers: {', '.join(triggers)}")
                    print(f"   UR Function: {ur_function}")
                    
                    # Send UR command
                    self.send_ur_command(ur_function)
                    
                    # Wait a bit to avoid repeated triggers
                    time.sleep(5)
                    self.position_stable_count = 0
                
                # Show periodic status
                if hasattr(self, '_last_status_time'):
                    if time.time() - self._last_status_time > 10:  # Every 10 seconds
                        self._show_periodic_status(status)
                else:
                    self._last_status_time = time.time()
                
                time.sleep(0.5)  # Check every 500ms
                
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                time.sleep(2)
    
    def _show_periodic_status(self, status):
        """Show periodic status updates"""
        pos = status["position"]
        print(f"📍 MIR: ({pos['x']:.2f}, {pos['y']:.2f}) | "
              f"State: {status['state_text'][:20]} | "
              f"Mission: {status['mission_text'][:30]} | "
              f"Dist: {status['distance_to_next_target']:.2f}m")
        self._last_status_time = time.time()
    
    def start_monitoring(self):
        """Start monitoring MIR position"""
        if self.monitoring:
            print("⚠️  Already monitoring")
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("✅ MIR target detection started")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        print("🛑 MIR target detection stopped")
    
    def test_connection(self):
        """Test connection to MIR"""
        print(f"🧪 Testing connection to MIR at {self.mir_ip}...")
        status = self.get_mir_status()
        if status:
            print("✅ Connection successful!")
            print(f"   Position: ({status['position']['x']:.2f}, {status['position']['y']:.2f})")
            print(f"   State: {status['state_text']}")
            print(f"   Mission: {status['mission_text']}")
            print(f"   Battery: {status['battery_percentage']:.1f}%")
            return True
        else:
            print("❌ Connection failed!")
            return False
    
    def configure_target_mapping(self, keyword, ur_function):
        """Configure keyword to UR function mapping"""
        self.target_mappings[keyword.lower()] = ur_function
        print(f"✅ Mapped '{keyword}' → '{ur_function}'")
    
    def show_current_config(self):
        """Show current configuration"""
        print("📋 CURRENT CONFIGURATION:")
        print(f"   MIR IP: {self.mir_ip}")
        print(f"   UR Control Dir: {self.ur_control_dir}")
        print(f"   Position Threshold: {self.position_threshold}m")
        print(f"   Stability Required: {self.stable_required} readings")
        print("   Target Mappings:")
        for keyword, ur_func in self.target_mappings.items():
            print(f"     '{keyword}' → '{ur_func}'")


def main():
    """Interactive MIR target detection"""
    print("🚀 MIR Target Detection System")
    print("=" * 40)
    
    # Initialize detector with your MIR IP
    detector = MIRTargetDetector(mir_ip="118.138.107.60")
    
    print("\n📋 AVAILABLE COMMANDS:")
    print("   test     - Test MIR connection")
    print("   start    - Start target detection")
    print("   stop     - Stop detection")
    print("   config   - Show current configuration")
    print("   map <keyword> <ur_function> - Configure target mapping")
    print("   status   - Show current MIR status")
    print("   quit     - Exit")
    
    try:
        while True:
            cmd = input("\n🎯 Command: ").strip().lower()
            
            if cmd == "test":
                detector.test_connection()
            elif cmd == "start":
                detector.start_monitoring()
            elif cmd == "stop":
                detector.stop_monitoring()
            elif cmd == "config":
                detector.show_current_config()
            elif cmd == "status":
                status = detector.get_mir_status()
                if status:
                    print(f"📍 Position: ({status['position']['x']:.2f}, {status['position']['y']:.2f})")
                    print(f"🎯 Mission: {status['mission_text']}")
                    print(f"🚁 State: {status['state_text']}")
                    print(f"📏 Distance to target: {status['distance_to_next_target']:.2f}m")
                    print(f"🔋 Battery: {status['battery_percentage']:.1f}%")
            elif cmd.startswith("map"):
                parts = cmd.split()
                if len(parts) >= 3:
                    detector.configure_target_mapping(parts[1], parts[2])
                else:
                    print("Usage: map <keyword> <ur_function>")
            elif cmd == "quit":
                break
            else:
                print("❌ Unknown command")
    
    except KeyboardInterrupt:
        pass
    finally:
        detector.stop_monitoring()
        print("\n✅ MIR target detection system shut down")


if __name__ == "__main__":
    main()