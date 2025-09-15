#!/usr/bin/env python3
"""
FILE-BASED AUTOMATION: No External Dependencies
Uses file monitoring to detect when you manually signal position arrivals

How it works:
1. You watch your MIR via the website
2. When MIR reaches a position, you create a simple file
3. This system detects the file and triggers UR operations automatically
"""

import time
import threading
from pathlib import Path
import os

class FileBasedAutoController:
    """File-based automation - no external dependencies needed"""
    
    def __init__(self, ur_control_dir="control", trigger_dir="mir_triggers"):
        self.ur_control_dir = Path(ur_control_dir)
        self.trigger_dir = Path(trigger_dir)
        
        # Create directories
        self.ur_control_dir.mkdir(exist_ok=True)
        self.trigger_dir.mkdir(exist_ok=True)
        
        # Mission workflows
        self.position_workflows = {
            "p_start": ["pickup", "compact"],
            "pl1": ["home", "dropoff1", "home", "compact"],
            "pl2": ["home", "dropoff2", "home", "compact"],
            "pr1": ["home", "dropoff3_safe", "home", "compact"],
            "pr2": ["home", "dropoff4_safe", "home", "compact"]
        }
        
        # Monitoring state
        self.monitoring = False
        self.processed_files = set()
        
    def create_trigger_files(self):
        """Create example trigger files"""
        print("📁 Creating trigger file examples...")
        
        examples_dir = self.trigger_dir / "examples"
        examples_dir.mkdir(exist_ok=True)
        
        for position in self.position_workflows.keys():
            example_file = examples_dir / f"{position}.trigger"
            with open(example_file, "w") as f:
                f.write(f"# Touch this file when MIR reaches {position.upper()}\n")
                f.write(f"# Then move it to {self.trigger_dir}/\n")
                f.write(f"position: {position}\n")
                f.write(f"timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"✅ Example files created in: {examples_dir}")
        print("📋 To trigger operations:")
        print(f"   cp {examples_dir}/p_start.trigger {self.trigger_dir}/")
        print(f"   # Or simply: touch {self.trigger_dir}/p_start.trigger")
    
    def monitor_trigger_files(self):
        """Monitor for trigger files"""
        print("👀 MONITORING TRIGGER FILES")
        print(f"📁 Watching: {self.trigger_dir}")
        print("📋 Trigger files:")
        for pos in self.position_workflows.keys():
            print(f"   {pos}.trigger → {' → '.join(self.position_workflows[pos])}")
        print()
        
        while self.monitoring:
            try:
                # Check for trigger files
                trigger_files = list(self.trigger_dir.glob("*.trigger"))
                
                for trigger_file in trigger_files:
                    if str(trigger_file) in self.processed_files:
                        continue
                    
                    # Extract position from filename
                    position = trigger_file.stem.lower()
                    
                    if position in self.position_workflows:
                        print(f"\n🎯 TRIGGER DETECTED: {trigger_file.name}")
                        
                        # Execute UR sequence
                        self.execute_ur_sequence(position, self.position_workflows[position])
                        
                        # Mark as processed and remove file
                        self.processed_files.add(str(trigger_file))
                        trigger_file.unlink()  # Delete the trigger file
                        
                        print(f"✅ Processed and removed: {trigger_file.name}")
                    else:
                        print(f"❌ Unknown position in file: {trigger_file.name}")
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                print(f"❌ Error monitoring files: {e}")
                time.sleep(2)
    
    def execute_ur_sequence(self, position, ur_sequence):
        """Execute UR sequence"""
        try:
            print(f"🤖 Executing {position.upper()} sequence: {' → '.join(ur_sequence)}")
            
            for i, ur_function in enumerate(ur_sequence, 1):
                print(f"  {i}/{len(ur_sequence)} {ur_function}")
                
                # Send UR command
                pause_mir = ur_function != "compact"
                self.send_ur_command(ur_function, pause_mir=pause_mir)
                
                if i < len(ur_sequence):
                    time.sleep(2)  # Wait between commands
            
            print(f"✅ {position.upper()} sequence complete")
            
        except Exception as e:
            print(f"❌ Error executing {position}: {e}")
    
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
            
        except Exception as e:
            print(f"❌ Error sending command: {e}")
    
    def start_monitoring(self):
        """Start file monitoring"""
        if self.monitoring:
            print("⚠️  Already monitoring")
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_trigger_files)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print("🚀 FILE MONITORING STARTED!")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        print("🛑 File monitoring stopped")
    
    def manual_trigger(self, position):
        """Manually trigger a position"""
        if position in self.position_workflows:
            trigger_file = self.trigger_dir / f"{position}.trigger"
            with open(trigger_file, "w") as f:
                f.write(f"manual trigger at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            print(f"✅ Created trigger: {trigger_file}")
        else:
            print(f"❌ Unknown position: {position}")


def main():
    """File-based automation controller"""
    print("📁 FILE-BASED MIR AUTOMATION")
    print("=" * 35)
    print("🎯 No external dependencies required!")
    
    controller = FileBasedAutoController()
    
    print("\n📋 COMMANDS:")
    print("   setup    - Create trigger file examples")
    print("   start    - Start file monitoring")
    print("   stop     - Stop monitoring")
    print("   trigger <position> - Manual trigger")
    print("   positions - Show available positions")
    print("   quit     - Exit")
    
    print("\n💡 HOW TO USE:")
    print("1. Run 'setup' to create example files")
    print("2. Run 'start' to begin monitoring")
    print("3. When MIR reaches a position, copy the trigger file:")
    print("   cp mir_triggers/examples/p_start.trigger mir_triggers/")
    print("4. Or create trigger manually:")
    print("   touch mir_triggers/p_start.trigger")
    
    try:
        while True:
            cmd = input("\n📁 Command: ").strip().lower()
            
            if cmd == "quit":
                break
            elif cmd == "setup":
                controller.create_trigger_files()
            elif cmd == "start":
                controller.start_monitoring()
            elif cmd == "stop":
                controller.stop_monitoring()
            elif cmd == "positions":
                print("📍 Available positions:")
                for pos, seq in controller.position_workflows.items():
                    print(f"   {pos}: {' → '.join(seq)}")
            elif cmd.startswith("trigger"):
                parts = cmd.split()
                if len(parts) > 1:
                    controller.manual_trigger(parts[1])
                else:
                    print("Usage: trigger <position>")
            else:
                print("❌ Unknown command")
    
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop_monitoring()
        print("\n✅ File-based automation shut down")


if __name__ == "__main__":
    main()