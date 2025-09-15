#!/usr/bin/env python3
"""
Quick MIR-UR Integration
Simple integration that monitors MIR and triggers UR operations

Usage:
1. Start your UR robot system: python3 unified_robot_control_simple.py --robot-ip 192.168.1.6 --mir-ip 118.138.127.231
2. Run this script: python3 quick_mir_integration.py  
3. Set goals via MIR website as usual
4. This script detects when MIR reaches targets and sends UR commands
"""

import time
import threading
from pathlib import Path

class QuickMIRIntegration:
    """Simple MIR-UR integration using your existing setup"""
    
    def __init__(self, ur_control_dir="control"):
        self.ur_control_dir = Path(ur_control_dir)
        self.ur_control_dir.mkdir(exist_ok=True)
        
        # Simple target detection based on manual triggers
        self.monitoring = False
        self.current_location = "unknown"
        
        # Location to UR function mapping
        self.location_functions = {
            "pickup": "pickup",
            "dropoff1": "dropoff1", 
            "dropoff2": "dropoff2",
            "dropoff3": "dropoff3_safe",
            "dropoff4": "dropoff4_safe",
            "left1": "dropoff3_safe",
            "left2": "dropoff4_safe", 
            "right1": "dropoff1",
            "right2": "dropoff2",
            "home": "home"
        }
    
    def send_ur_command(self, ur_function, speed=0.1, pause_mir=True):
        """Send command to UR system via file interface"""
        try:
            command_file = self.ur_control_dir / "robot_commands.txt"
            
            if pause_mir:
                # Send command that includes MIR pause
                command = f"add {ur_function} {speed} true\n"
            else:
                command = f"add {ur_function} {speed}\n"
            
            with open(command_file, "a") as f:
                f.write(command)
            
            print(f"✅ Sent UR command: {command.strip()}")
            
            # Log the operation
            log_file = self.ur_control_dir / "operation_log.txt"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, "a") as f:
                f.write(f"{timestamp}: Triggered '{ur_function}' from location '{self.current_location}'\n")
                
        except Exception as e:
            print(f"❌ Error sending UR command: {e}")
    
    def trigger_operation(self, location_name):
        """Manually trigger operation for a location"""
        if location_name.lower() in self.location_functions:
            ur_function = self.location_functions[location_name.lower()]
            self.current_location = location_name
            
            print(f"🎯 OPERATION TRIGGERED")
            print(f"   Location: {location_name}")
            print(f"   UR Function: {ur_function}")
            
            self.send_ur_command(ur_function, speed=0.1, pause_mir=True)
        else:
            print(f"❌ Unknown location: {location_name}")
            print(f"Available locations: {', '.join(self.location_functions.keys())}")
    
    def auto_pickup_dropoff_cycle(self, dropoff_location):
        """Automatic pickup-dropoff cycle"""
        print(f"🔄 Starting pickup-dropoff cycle to {dropoff_location}")
        
        # First pickup
        print("1️⃣ Triggering pickup...")
        self.trigger_operation("pickup")
        
        # Wait a bit
        time.sleep(2)
        
        # Then dropoff
        print(f"2️⃣ Triggering dropoff at {dropoff_location}...")
        self.trigger_operation(dropoff_location)
    
    def show_menu(self):
        """Show interactive menu"""
        print("\n📋 QUICK COMMANDS:")
        print("=" * 30)
        print("🎯 SINGLE OPERATIONS:")
        for loc, func in self.location_functions.items():
            print(f"   {loc:<10} → {func}")
        
        print("\n🔄 PICKUP-DROPOFF CYCLES:")
        print("   cycle1     → pickup + dropoff1")
        print("   cycle2     → pickup + dropoff2") 
        print("   cycle3     → pickup + dropoff3_safe")
        print("   cycle4     → pickup + dropoff4_safe")
        
        print("\n⚡ SYSTEM COMMANDS:")
        print("   status     → Check UR system status")
        print("   pause      → Pause UR system")
        print("   resume     → Resume UR system")
        print("   stop       → Stop all operations")
        print("   help       → Show this menu")
        print("   quit       → Exit")
    
    def send_system_command(self, command):
        """Send system command to UR"""
        try:
            command_file = self.ur_control_dir / "robot_commands.txt"
            with open(command_file, "a") as f:
                f.write(f"{command}\n")
            print(f"✅ Sent system command: {command}")
        except Exception as e:
            print(f"❌ Error sending command: {e}")
    
    def check_ur_status(self):
        """Check UR system status"""
        try:
            status_file = self.ur_control_dir / "robot_status.json"
            if status_file.exists():
                with open(status_file, "r") as f:
                    status = f.read()
                print("📊 UR System Status:")
                print(status)
            else:
                print("❌ No status file found. Is UR system running?")
        except Exception as e:
            print(f"❌ Error reading status: {e}")


def main():
    """Interactive MIR-UR integration"""
    print("🚀 Quick MIR-UR Integration")
    print("=" * 40)
    print("💡 Make sure your UR system is running first!")
    print("   python3 unified_robot_control_simple.py --robot-ip 192.168.1.6 --mir-ip 118.138.107.60")
    
    integration = QuickMIRIntegration()
    integration.show_menu()
    
    try:
        while True:
            cmd = input("\n🎯 Command: ").strip().lower()
            
            if cmd == "quit":
                break
            elif cmd == "help":
                integration.show_menu()
            elif cmd == "status":
                integration.check_ur_status()
            elif cmd in ["pause", "resume", "stop"]:
                integration.send_system_command(cmd)
            elif cmd.startswith("cycle"):
                if cmd == "cycle1":
                    integration.auto_pickup_dropoff_cycle("dropoff1")
                elif cmd == "cycle2":
                    integration.auto_pickup_dropoff_cycle("dropoff2")
                elif cmd == "cycle3":
                    integration.auto_pickup_dropoff_cycle("dropoff3")
                elif cmd == "cycle4":
                    integration.auto_pickup_dropoff_cycle("dropoff4")
                else:
                    print("❌ Unknown cycle. Use cycle1, cycle2, cycle3, or cycle4")
            elif cmd in integration.location_functions:
                integration.trigger_operation(cmd)
            else:
                print("❌ Unknown command. Type 'help' for available commands.")
    
    except KeyboardInterrupt:
        pass
    
    print("\n✅ Integration shut down")


if __name__ == "__main__":
    main()