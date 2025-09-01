#!/usr/bin/env python3
"""
External Robot Control Example
Demonstrates how to control the robot from a separate program
"""

import time
import json
from pathlib import Path

class ExternalRobotController:
    """External interface to control the robot system"""
    
    def __init__(self, control_dir: str = "control"):
        self.control_dir = Path(control_dir)
        self.command_file = self.control_dir / "robot_commands.txt"
        self.status_file = self.control_dir / "robot_status.json"
        self.response_file = self.control_dir / "robot_response.txt"
        
    def send_command(self, command: str):
        """Send command to robot controller"""
        with open(self.command_file, 'a') as f:
            f.write(f"{command}\n")
        print(f"📤 Sent command: {command}")
        
    def get_status(self) -> dict:
        """Get current robot status"""
        try:
            with open(self.status_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def get_latest_response(self) -> str:
        """Get latest response from robot"""
        try:
            with open(self.response_file, 'r') as f:
                lines = f.readlines()
                return lines[-1].strip() if lines else ""
        except Exception:
            return ""
    
    def wait_for_robot_ready(self, timeout: int = 10) -> bool:
        """Wait for robot to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_status()
            if status.get('running', False):
                return True
            time.sleep(0.5)
        return False
    
    def pause_robot(self):
        """Pause robot execution"""
        self.send_command("pause")
    
    def resume_robot(self):
        """Resume robot execution"""
        self.send_command("resume")
    
    def stop_robot(self):
        """Stop robot execution"""
        self.send_command("stop")
    
    def slow_down(self):
        """Slow down robot"""
        self.send_command("slow")
    
    def speed_up(self):
        """Speed up robot"""
        self.send_command("fast")
    
    def set_speed(self, speed: float):
        """Set robot speed"""
        self.send_command(f"speed {speed}")
    
    def set_speed_multiplier(self, multiplier: float):
        """Set speed multiplier"""
        self.send_command(f"multiplier {multiplier}")
    
    def add_function(self, function_name: str, speed: float = None):
        """Add function to robot queue"""
        if speed:
            self.send_command(f"add {function_name} {speed}")
        else:
            self.send_command(f"add {function_name}")
    
    def monitor_status(self, duration: int = 30):
        """Monitor robot status for specified duration"""
        print(f"🔍 Monitoring robot for {duration} seconds...")
        start_time = time.time()
        
        while time.time() - start_time < duration:
            status = self.get_status()
            if status:
                running = "✅" if status.get('running', False) else "❌"
                paused = "⏸️" if status.get('paused', False) else "▶️"
                speed = status.get('effective_speed', 0)
                executed = status.get('functions_executed', 0)
                queue_size = status.get('queue_size', 0)
                
                print(f"Status: {running} {paused} | Speed: {speed:.3f} m/s | Functions: {executed} | Queue: {queue_size}")
            
            time.sleep(2)

def main():
    """Example usage of external robot control"""
    controller = ExternalRobotController()
    
    print("🤖 External Robot Control Example")
    print("💡 Make sure the main robot controller is running first!")
    
    # Wait for robot to be ready
    print("⏳ Waiting for robot to be ready...")
    if not controller.wait_for_robot_ready():
        print("❌ Robot not ready. Make sure interactive_robot_control.py is running.")
        return
    
    print("✅ Robot is ready!")
    
    try:
        # Example control sequence
        print("\n🎯 Starting example control sequence...")
        
        # Add some functions
        controller.add_function("home")
        time.sleep(2)
        
        controller.add_function("pickup", 0.05)  # Slow pickup
        time.sleep(1)
        
        # Speed up for travel
        print("🚀 Speeding up...")
        controller.speed_up()
        time.sleep(1)
        
        controller.add_function("square")
        time.sleep(5)
        
        # Pause execution
        print("⏸️ Pausing execution...")
        controller.pause_robot()
        time.sleep(3)
        
        # Resume
        print("▶️ Resuming execution...")
        controller.resume_robot()
        time.sleep(2)
        
        # Slow down
        print("🐌 Slowing down...")
        controller.slow_down()
        controller.slow_down()  # Make it really slow
        time.sleep(1)
        
        controller.add_function("dropoff")
        
        # Monitor for a while
        controller.monitor_status(15)
        
        print("✅ Example completed!")
        
    except KeyboardInterrupt:
        print("\n🛑 External control interrupted")
        controller.stop_robot()

if __name__ == "__main__":
    main()
