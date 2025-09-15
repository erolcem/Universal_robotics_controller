#!/usr/bin/env python3
"""
IMPROVED AUTOMATION: Better Position Detection
Works with paused MIR and position-based detection
"""

import time
import threading
import requests
from pathlib import Path
import json

class ImprovedAutoController:
    """Better automation that works with paused MIR"""
    
    def __init__(self, mir_ip="118.138.107.60"):
        self.mir_ip = mir_ip
        self.mir_base_url = f"http://{mir_ip}/api/v2.0.0"
        self.control_dir = Path("control")
        self.control_dir.mkdir(exist_ok=True)
        
        self.monitoring = False
        self.last_position = None
        self.positions_map = {}
        self.processed_positions = set()
        
        # Position workflows
        self.workflows = {
            "p_start": ["pickup", "compact"],
            "pl1": ["home", "dropoff1", "home", "compact"],
            "pl2": ["home", "dropoff2", "home", "compact"],
            "pr1": ["home", "dropoff3_safe", "home", "compact"],
            "pr2": ["home", "dropoff4_safe", "home", "compact"]
        }
    
    def load_positions(self):
        """Load position names from MIR"""
        try:
            # Get maps
            response = requests.get(f"{self.mir_base_url}/maps", timeout=5)
            if response.status_code != 200:
                return False
                
            maps = response.json()
            if not maps:
                return False
                
            map_id = maps[0].get('guid')
            
            # Get positions
            response = requests.get(f"{self.mir_base_url}/maps/{map_id}/positions", timeout=5)
            if response.status_code != 200:
                return False
                
            positions = response.json()
            
            print("📍 Available positions:")
            for pos in positions:
                name = pos.get('name', '').lower()
                pos_id = pos.get('guid')
                self.positions_map[pos_id] = name
                print(f"   - {name}")
                
                # Check if this matches our workflow positions
                for workflow_pos in self.workflows.keys():
                    if workflow_pos in name or any(part in name for part in workflow_pos.split('_')):
                        print(f"     ✅ Matches {workflow_pos}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading positions: {e}")
            return False
    
    def get_current_position(self):
        """Get current MIR position"""
        try:
            response = requests.get(f"{self.mir_base_url}/status", timeout=5)
            if response.status_code != 200:
                return None
                
            status = response.json()
            
            # Check if we're at a specific position
            mission_text = status.get('mission_text', '').lower()
            
            # Look for position patterns in mission text
            for workflow_pos in self.workflows.keys():
                patterns = [workflow_pos, workflow_pos.replace('_', ' '), workflow_pos.replace('_', '')]
                if any(pattern in mission_text for pattern in patterns):
                    return workflow_pos
            
            # Also check state for useful info
            state = status.get('state_text', '').lower()
            if 'ready' in state or 'executing' in state:
                # Try to determine position from coordinates or mission queue
                pass
                
            return None
            
        except Exception as e:
            print(f"❌ Error getting position: {e}")
            return None
    
    def monitor_positions(self):
        """Monitor for position changes"""
        print("🔍 Starting position monitoring...")
        
        while self.monitoring:
            try:
                # Get status
                response = requests.get(f"{self.mir_base_url}/status", timeout=5)
                if response.status_code == 200:
                    status = response.json()
                    state = status.get('state_text', '')
                    mission_text = status.get('mission_text', '')
                    battery = status.get('battery_percentage', 0)
                    
                    print(f"🔄 State: {state} | Mission: {mission_text} | Battery: {battery:.1f}%")
                    
                    # Check for position triggers
                    current_pos = self.get_current_position()
                    if current_pos and current_pos != self.last_position:
                        if current_pos not in self.processed_positions:
                            print(f"\n🎯 NEW POSITION DETECTED: {current_pos.upper()}")
                            self.execute_workflow(current_pos)
                            self.processed_positions.add(current_pos)
                        
                        self.last_position = current_pos
                
                time.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(5)
    
    def execute_workflow(self, position):
        """Execute UR workflow for position"""
        if position in self.workflows:
            sequence = self.workflows[position]
            print(f"🤖 Executing {position.upper()}: {' → '.join(sequence)}")
            
            for i, command in enumerate(sequence, 1):
                print(f"  {i}/{len(sequence)} {command}")
                
                # Send to UR
                pause_mir = command != "compact"
                self.send_ur_command(command, pause_mir=pause_mir)
                
                if i < len(sequence):
                    time.sleep(1)
            
            print(f"✅ {position.upper()} workflow complete")
    
    def send_ur_command(self, command, pause_mir=True, speed=0.1):
        """Send command to UR"""
        try:
            command_file = self.control_dir / "robot_commands.txt"
            
            if pause_mir:
                cmd_line = f"add {command} {speed} true\n"
            else:
                cmd_line = f"add {command} {speed}\n"
            
            with open(command_file, "a") as f:
                f.write(cmd_line)
            
            print(f"    📤 {cmd_line.strip()}")
            
        except Exception as e:
            print(f"❌ Error sending command: {e}")
    
    def start_monitoring(self):
        """Start monitoring"""
        if self.monitoring:
            print("⚠️ Already monitoring")
            return
        
        print("🚀 STARTING IMPROVED AUTOMATION")
        print("=" * 40)
        
        # Load positions
        if not self.load_positions():
            print("⚠️ Could not load positions, using text-based detection")
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_positions)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print("✅ Monitoring started!")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        print("🛑 Monitoring stopped")
    
    def manual_trigger(self, position):
        """Manual trigger for testing"""
        if position in self.workflows:
            print(f"🎯 Manual trigger: {position}")
            self.execute_workflow(position)
        else:
            print(f"❌ Unknown position: {position}")
            print(f"Available: {list(self.workflows.keys())}")

def main():
    controller = ImprovedAutoController()
    
    print("🔧 IMPROVED MIR AUTOMATION")
    print("=" * 30)
    print("📋 Commands:")
    print("   start    - Start monitoring")
    print("   stop     - Stop monitoring") 
    print("   trigger <pos> - Manual trigger")
    print("   status   - Check MIR status")
    print("   quit     - Exit")
    
    try:
        while True:
            cmd = input("\n🔧 Command: ").strip().lower()
            
            if cmd == "quit":
                break
            elif cmd == "start":
                controller.start_monitoring()
            elif cmd == "stop":
                controller.stop_monitoring()
            elif cmd == "status":
                # Quick status check
                try:
                    response = requests.get(f"{controller.mir_base_url}/status", timeout=5)
                    if response.status_code == 200:
                        status = response.json()
                        print(f"📊 State: {status.get('state_text')}")
                        print(f"📊 Mission: {status.get('mission_text')}")
                        print(f"📊 Battery: {status.get('battery_percentage', 0):.1f}%")
                except Exception as e:
                    print(f"❌ Error: {e}")
            elif cmd.startswith("trigger"):
                parts = cmd.split()
                if len(parts) > 1:
                    controller.manual_trigger(parts[1])
                else:
                    print("Usage: trigger <position>")
                    print(f"Available: {list(controller.workflows.keys())}")
            else:
                print("❌ Unknown command")
    
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop_monitoring()
        print("\n✅ Automation shut down")

if __name__ == "__main__":
    main()