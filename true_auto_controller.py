#!/usr/bin/env python3
"""
TRUE AUTOMATION: MIR Mission Auto-Detection
Automatically detects MIR mission progress and triggers UR operations

This monitors your MIR's API to detect:
- When missions start/stop
- Current mission name  
- Position names in missions
- When MIR reaches specific positions
"""

import time
import threading
import json
from pathlib import Path
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  requests not available. Install with: pip install requests")

class TrueAutoController:
    """Fully automatic MIR mission monitoring and UR control"""
    
    def __init__(self, mir_ip="118.138.107.60", ur_control_dir="control"):
        self.mir_ip = mir_ip
        self.mir_base_url = f"http://{mir_ip}/api/v2.0.0"
        self.ur_control_dir = Path(ur_control_dir)
        
        # Auto-detection settings
        self.monitoring = False
        self.check_interval = 1.0  # Check every 1 second
        
        # Mission tracking
        self.current_mission = None
        self.last_mission_text = ""
        self.last_position = None
        self.position_history = []
        
        # Position detection patterns
        self.position_triggers = {
            "P_start": {
                "patterns": ["p_start", "start", "pickup", "p start"],
                "ur_sequence": ["pickup", "compact"],
                "description": "Pickup station"
            },
            "PL1": {
                "patterns": ["pl1", "pl 1", "left 1", "left1"],
                "ur_sequence": ["home", "dropoff1", "home", "compact"],
                "description": "Left position 1"
            },
            "PL2": {
                "patterns": ["pl2", "pl 2", "left 2", "left2"],
                "ur_sequence": ["home", "dropoff2", "home", "compact"],
                "description": "Left position 2"
            },
            "PR1": {
                "patterns": ["pr1", "pr 1", "right 1", "right1"],
                "ur_sequence": ["home", "dropoff3_safe", "home", "compact"],
                "description": "Right position 1"
            },
            "PR2": {
                "patterns": ["pr2", "pr 2", "right 2", "right2"],
                "ur_sequence": ["home", "dropoff4_safe", "home", "compact"],
                "description": "Right position 2"
            }
        }
        
        # State tracking
        self.operation_in_progress = False
        self.triggered_positions = set()
        
    def get_mir_status(self):
        """Get MIR status via API"""
        if not REQUESTS_AVAILABLE:
            return None
            
        try:
            # Get main status
            response = requests.get(f"{self.mir_base_url}/status", timeout=3)
            if response.status_code != 200:
                return None
                
            status = response.json()
            
            # Get mission queue
            mission_response = requests.get(f"{self.mir_base_url}/mission_queue", timeout=3)
            missions = mission_response.json() if mission_response.status_code == 200 else []
            
            # Get mission details if available
            current_mission = None
            if missions:
                current_mission = missions[0] if len(missions) > 0 else None
            
            return {
                "position": status.get("position", {}),
                "state_text": status.get("state_text", ""),
                "mission_text": status.get("mission_text", ""),
                "distance_to_next_target": status.get("distance_to_next_target", 999),
                "velocity": status.get("velocity", {}),
                "battery": status.get("battery_percentage", 0),
                "current_mission": current_mission,
                "mission_queue": missions
            }
        except Exception as e:
            print(f"❌ Error getting MIR status: {e}")
            return None
    
    def detect_position_arrival(self, mir_status):
        """Detect which position MIR has reached"""
        if not mir_status:
            return None
            
        mission_text = mir_status.get("mission_text", "").lower()
        state_text = mir_status.get("state_text", "").lower()
        distance = mir_status.get("distance_to_next_target", 999)
        
        # Check if MIR is stopped/arrived (multiple indicators)
        is_arrived = any([
            distance < 0.3,  # Very close to target
            "reached" in state_text,
            "arrived" in state_text,
            "executing" in state_text and distance < 1.0,
            "ready" in state_text,
            mir_status.get("velocity", {}).get("linear", 1) < 0.1  # Not moving
        ])
        
        if not is_arrived:
            return None
        
        # Check mission text for position patterns
        for position_name, position_info in self.position_triggers.items():
            for pattern in position_info["patterns"]:
                if pattern in mission_text or pattern in state_text:
                    return position_name
        
        return None
    
    def execute_ur_sequence(self, position_name, ur_sequence):
        """Execute UR sequence for detected position"""
        if self.operation_in_progress:
            print(f"⚠️  Already executing, skipping {position_name}")
            return
            
        # Avoid duplicate triggers
        position_key = f"{position_name}_{int(time.time())}"
        if position_name in self.triggered_positions:
            if time.time() - getattr(self, f"last_{position_name}_time", 0) < 30:
                return  # Too soon since last trigger
        
        self.operation_in_progress = True
        setattr(self, f"last_{position_name}_time", time.time())
        
        try:
            info = self.position_triggers[position_name]
            print(f"\n🎯 AUTO TRIGGER: {position_name}")
            print(f"📍 {info['description']}")
            print(f"🤖 Sequence: {' → '.join(ur_sequence)}")
            
            for i, ur_function in enumerate(ur_sequence, 1):
                print(f"  {i}/{len(ur_sequence)} Executing: {ur_function}")
                
                # Send UR command
                pause_mir = ur_function != "compact"  # Don't pause for compact
                self.send_ur_command(ur_function, pause_mir=pause_mir)
                
                # Wait between commands
                if i < len(ur_sequence):
                    time.sleep(2)
            
            print(f"✅ {position_name} sequence complete")
            self.triggered_positions.add(position_name)
            
        except Exception as e:
            print(f"❌ Error executing {position_name}: {e}")
        finally:
            self.operation_in_progress = False
    
    def send_ur_command(self, ur_function, pause_mir=True, speed=0.1):
        """Send command to UR system"""
        try:
            command_file = self.ur_control_dir / "robot_commands.txt"
            
            if pause_mir:
                command = f"add {ur_function} {speed} true\n"
            else:
                command = f"add {ur_function} {speed}\n"
            
            with open(command_file, "a") as f:
                f.write(command)
            
            print(f"    📤 {command.strip()}")
            
            # Log
            log_file = self.ur_control_dir / "auto_mission_log.txt"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, "a") as f:
                f.write(f"{timestamp}: AUTO {ur_function} (pause_mir: {pause_mir})\n")
                
        except Exception as e:
            print(f"❌ Error sending command: {e}")
    
    def monitor_loop(self):
        """Main automatic monitoring loop"""
        print("🤖 STARTING TRUE AUTOMATION")
        print("=" * 40)
        print(f"🔍 Monitoring MIR at: {self.mir_ip}")
        print("🎯 Will auto-trigger UR operations when positions detected")
        print("📋 Monitoring for positions:")
        for pos, info in self.position_triggers.items():
            seq = " → ".join(info["ur_sequence"])
            print(f"   {pos}: {seq}")
        print()
        
        consecutive_errors = 0
        
        while self.monitoring:
            try:
                # Get MIR status
                mir_status = self.get_mir_status()
                if not mir_status:
                    consecutive_errors += 1
                    if consecutive_errors > 10:
                        print("❌ Too many connection errors. Check MIR IP and network.")
                        time.sleep(10)
                    else:
                        time.sleep(self.check_interval)
                    continue
                
                consecutive_errors = 0
                
                # Check if FYP mission is running
                mission_text = mir_status.get("mission_text", "")
                if "fyp" not in mission_text.lower():
                    time.sleep(self.check_interval)
                    continue
                
                # Detect position arrival
                detected_position = self.detect_position_arrival(mir_status)
                if detected_position:
                    ur_sequence = self.position_triggers[detected_position]["ur_sequence"]
                    
                    # Execute in thread to avoid blocking
                    thread = threading.Thread(
                        target=self.execute_ur_sequence,
                        args=(detected_position, ur_sequence)
                    )
                    thread.start()
                
                # Show periodic status
                if hasattr(self, "_last_status_show"):
                    if time.time() - self._last_status_show > 30:
                        self._show_status(mir_status)
                else:
                    self._last_status_show = time.time()
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Monitor error: {e}")
                time.sleep(5)
    
    def _show_status(self, mir_status):
        """Show periodic status"""
        mission = mir_status.get("mission_text", "")[:40]
        state = mir_status.get("state_text", "")[:20]
        distance = mir_status.get("distance_to_next_target", 0)
        battery = mir_status.get("battery", 0)
        
        print(f"📊 MIR: {state} | Mission: {mission} | Dist: {distance:.1f}m | Battery: {battery:.0f}%")
        self._last_status_show = time.time()
    
    def start_automation(self):
        """Start automatic monitoring"""
        if not REQUESTS_AVAILABLE:
            print("❌ Cannot start automation without requests library")
            print("   Install with: pip install requests")
            return False
            
        if self.monitoring:
            print("⚠️  Already monitoring")
            return False
        
        # Test connection first
        print("🧪 Testing MIR connection...")
        status = self.get_mir_status()
        if not status:
            print("❌ Cannot connect to MIR. Check IP address and network.")
            return False
        
        print(f"✅ Connected to MIR (Battery: {status.get('battery', 0):.0f}%)")
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print("🚀 TRUE AUTOMATION STARTED!")
        return True
    
    def stop_automation(self):
        """Stop automatic monitoring"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        print("🛑 Automation stopped")
    
    def test_connection(self):
        """Test MIR connection"""
        if not REQUESTS_AVAILABLE:
            print("❌ requests library required for MIR connection")
            return False
            
        print(f"🧪 Testing connection to {self.mir_ip}...")
        status = self.get_mir_status()
        if status:
            print("✅ MIR Connection successful!")
            print(f"   State: {status.get('state_text', 'Unknown')}")
            print(f"   Mission: {status.get('mission_text', 'None')}")
            print(f"   Battery: {status.get('battery', 0):.1f}%")
            return True
        else:
            print("❌ Connection failed!")
            print("   - Check IP address")
            print("   - Check network connection")
            print("   - Check MIR API is enabled")
            return False


def main():
    """True automation controller"""
    print("🤖 TRUE MIR AUTOMATION SYSTEM")
    print("=" * 35)
    
    controller = TrueAutoController()
    
    print("📋 COMMANDS:")
    print("   test     - Test MIR connection")
    print("   start    - Start automatic monitoring")
    print("   stop     - Stop monitoring")
    print("   status   - Show current status")
    print("   quit     - Exit")
    
    if not REQUESTS_AVAILABLE:
        print("\n⚠️  SETUP REQUIRED:")
        print("   pip install requests")
        print("   Then restart this program")
    
    try:
        while True:
            cmd = input("\n🤖 Command: ").strip().lower()
            
            if cmd == "quit":
                break
            elif cmd == "test":
                controller.test_connection()
            elif cmd == "start":
                controller.start_automation()
            elif cmd == "stop":
                controller.stop_automation()
            elif cmd == "status":
                status = controller.get_mir_status()
                if status:
                    print("📊 Current MIR Status:")
                    print(f"   Mission: {status.get('mission_text', 'None')}")
                    print(f"   State: {status.get('state_text', 'Unknown')}")
                    print(f"   Distance: {status.get('distance_to_next_target', 0):.2f}m")
                    print(f"   Battery: {status.get('battery', 0):.1f}%")
            else:
                print("❌ Unknown command")
    
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop_automation()
        print("\n✅ True automation shut down")


if __name__ == "__main__":
    main()