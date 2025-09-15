#!/usr/bin/env python3
"""
Simple MIR Mission Workflow Controller
Manual trigger system for FYP moving test mission

Mission Flow:
P_start → pickup + compact
PL1 → home + dropoff1 + home + compact
P_start → pickup + compact  
PL2 → home + dropoff2 + home + compact
P_start → pickup + compact
PR1 → home + dropoff3_safe + home + compact
P_start → pickup + compact
PR2 → home + dropoff4_safe + home + compact
"""

import time
from pathlib import Path

class SimpleMissionController:
    """Simple controller for FYP moving test mission workflow"""
    
    def __init__(self, ur_control_dir="control"):
        self.ur_control_dir = Path(ur_control_dir)
        self.ur_control_dir.mkdir(exist_ok=True)
        
        # Mission workflow definition
        self.mission_workflows = {
            "p_start": {
                "name": "P_start (Pickup Station)",
                "sequence": ["pickup", "compact"],
                "description": "Pickup pipes and compact robot"
            },
            "pl1": {
                "name": "PL1 (Left Position 1)", 
                "sequence": ["home", "dropoff1", "home", "compact"],
                "description": "Go home, dropoff left 1, return home, compact"
            },
            "pl2": {
                "name": "PL2 (Left Position 2)",
                "sequence": ["home", "dropoff2", "home", "compact"], 
                "description": "Go home, dropoff left 2, return home, compact"
            },
            "pr1": {
                "name": "PR1 (Right Position 1)",
                "sequence": ["home", "dropoff3_safe", "home", "compact"],
                "description": "Go home, safe dropoff right 1, return home, compact"
            },
            "pr2": {
                "name": "PR2 (Right Position 2)",
                "sequence": ["home", "dropoff4_safe", "home", "compact"],
                "description": "Go home, safe dropoff right 2, return home, compact"
            }
        }
        
        # Full mission cycle
        self.full_cycle = [
            "p_start",  # Pickup 1
            "pl1",      # Dropoff left 1
            "p_start",  # Pickup 2
            "pl2",      # Dropoff left 2
            "p_start",  # Pickup 3
            "pr1",      # Dropoff right 1
            "p_start",  # Pickup 4
            "pr2"       # Dropoff right 2
        ]
        
        self.cycle_position = 0
        self.cycle_count = 0
    
    def execute_position_workflow(self, position_key):
        """Execute the complete workflow for a position"""
        if position_key not in self.mission_workflows:
            print(f"❌ Unknown position: {position_key}")
            return False
        
        workflow = self.mission_workflows[position_key]
        print(f"\n🎯 EXECUTING: {workflow['name']}")
        print(f"📝 {workflow['description']}")
        print(f"🤖 Sequence: {' → '.join(workflow['sequence'])}")
        
        try:
            for i, ur_function in enumerate(workflow['sequence'], 1):
                print(f"\n⚡ Step {i}/{len(workflow['sequence'])}: {ur_function}")
                
                # Send command with MIR pause (except for compact)
                pause_mir = ur_function != "compact"
                self.send_ur_command(ur_function, pause_mir=pause_mir)
                
                # Wait between operations  
                if i < len(workflow['sequence']):
                    print("⏳ Waiting 3 seconds before next operation...")
                    time.sleep(3)
            
            print(f"✅ {workflow['name']} workflow complete!")
            return True
            
        except Exception as e:
            print(f"❌ Error executing workflow: {e}")
            return False
    
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
            
            print(f"📤 Sent: {command.strip()}")
            
            # Log the operation
            log_file = self.ur_control_dir / "mission_workflow_log.txt"
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, "a") as f:
                f.write(f"{timestamp}: {ur_function} (MIR pause: {pause_mir})\n")
                
        except Exception as e:
            print(f"❌ Error sending command: {e}")
    
    def run_full_cycle(self):
        """Run the complete FYP moving test cycle"""
        print("🔄 STARTING FULL FYP MOVING TEST CYCLE")
        print("=" * 50)
        
        for i, position in enumerate(self.full_cycle, 1):
            workflow = self.mission_workflows[position]
            print(f"\n📍 STEP {i}/{len(self.full_cycle)}: {workflow['name']}")
            
            # Wait for user confirmation
            input("🎯 Press ENTER when MIR reaches this position...")
            
            # Execute workflow
            success = self.execute_position_workflow(position)
            if not success:
                print("❌ Workflow failed. Stopping cycle.")
                return False
            
            print(f"✅ Step {i} complete. Continuing to next position...")
        
        self.cycle_count += 1
        print(f"\n🎉 FULL CYCLE #{self.cycle_count} COMPLETE!")
        return True
    
    def run_auto_cycle(self, delay_between_steps=30):
        """Run cycle with automatic timing (for testing)"""
        print(f"🤖 RUNNING AUTO CYCLE (testing mode)")
        print(f"⏰ {delay_between_steps}s delay between steps")
        
        for i, position in enumerate(self.full_cycle, 1):
            workflow = self.mission_workflows[position]
            print(f"\n📍 AUTO STEP {i}/{len(self.full_cycle)}: {workflow['name']}")
            
            self.execute_position_workflow(position)
            
            if i < len(self.full_cycle):
                print(f"⏳ Waiting {delay_between_steps}s for next position...")
                time.sleep(delay_between_steps)
        
        self.cycle_count += 1
        print(f"\n🎉 AUTO CYCLE #{self.cycle_count} COMPLETE!")
    
    def show_mission_overview(self):
        """Show the complete mission overview"""
        print("📋 FYP MOVING TEST MISSION OVERVIEW")
        print("=" * 45)
        
        for i, position in enumerate(self.full_cycle, 1):
            workflow = self.mission_workflows[position]
            functions = " → ".join(workflow['sequence'])
            print(f"{i:2}. {workflow['name']:<25} | {functions}")
        
        print(f"\n📊 Total steps: {len(self.full_cycle)}")
        print(f"🔄 Cycles completed: {self.cycle_count}")
    
    def show_position_menu(self):
        """Show individual position commands"""
        print("\n🎯 INDIVIDUAL POSITION COMMANDS:")
        print("=" * 35)
        
        for key, workflow in self.mission_workflows.items():
            print(f"   {key:<8} → {workflow['name']}")
        
        print("\n🔄 FULL CYCLE COMMANDS:")
        print("   cycle    → Run complete cycle (manual)")
        print("   auto     → Run auto cycle (testing)")
        print("   overview → Show mission overview")
        print("   quit     → Exit")


def main():
    """Interactive mission controller"""
    print("🚀 FYP Moving Test Mission Controller")
    print("=" * 45)
    print("🎯 Controls UR operations for MIR mission workflow")
    
    controller = SimpleMissionController()
    controller.show_mission_overview()
    controller.show_position_menu()
    
    try:
        while True:
            cmd = input("\n🎯 Command: ").strip().lower()
            
            if cmd == "quit":
                break
            elif cmd == "overview":
                controller.show_mission_overview()
            elif cmd == "cycle":
                controller.run_full_cycle()
            elif cmd == "auto":
                delay = input("⏰ Delay between steps (default 30s): ").strip()
                delay = int(delay) if delay.isdigit() else 30
                controller.run_auto_cycle(delay)
            elif cmd == "help":
                controller.show_position_menu()
            elif cmd in controller.mission_workflows:
                controller.execute_position_workflow(cmd)
            else:
                print("❌ Unknown command. Available positions:")
                for key in controller.mission_workflows.keys():
                    print(f"   {key}")
                print("   Or use: cycle, auto, overview, help, quit")
    
    except KeyboardInterrupt:
        pass
    
    print("\n✅ Mission controller shut down")


if __name__ == "__main__":
    main()