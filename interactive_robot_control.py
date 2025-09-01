#!/usr/bin/env python3
"""
Enhanced Interactive Robot Control System
- Real-time function queuing and execution
- Terminal-based control commands
- External program control via command files
- Speed control and pause/resume functionality
"""

import json
import time
import socket
import threading
import queue
import argparse
import signal
import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

class EnhancedRobotController:
    """Enhanced robot controller with multi-interface control"""
    
    def __init__(self, robot_ip: str = "192.168.1.6", functions_dir: str = "functions", control_dir: str = "control"):
        self.robot_ip = robot_ip
        self.port = 30002
        self.functions_dir = Path(functions_dir)
        self.control_dir = Path(control_dir)
        
        # Queues and state
        self.function_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.paused = False
        self.running = False
        
        # Speed control
        self.current_speed = 0.1  # m/s
        self.speed_multiplier = 1.0  # For slow-down/speed-up
        
        # Threads
        self.worker_thread = None
        self.input_thread = None
        self.external_monitor_thread = None
        
        # Statistics
        self.functions_executed = 0
        self.commands_executed = 0
        self.start_time = None
        
        # Control files for external interface
        self.command_file = self.control_dir / "robot_commands.txt"
        self.status_file = self.control_dir / "robot_status.json"
        self.response_file = self.control_dir / "robot_response.txt"
        
        # Ensure directories exist
        self.functions_dir.mkdir(exist_ok=True)
        self.control_dir.mkdir(exist_ok=True)
        
        # Initialize control files
        self._init_control_files()
        
    def _init_control_files(self):
        """Initialize external control interface files"""
        self.command_file.write_text("")
        self.response_file.write_text("")
        self._update_status_file()
        
    def _update_status_file(self):
        """Update status file for external monitoring"""
        status = {
            "running": self.running,
            "paused": self.paused,
            "current_speed": self.current_speed,
            "speed_multiplier": self.speed_multiplier,
            "effective_speed": self.current_speed * self.speed_multiplier,
            "functions_executed": self.functions_executed,
            "commands_executed": self.commands_executed,
            "queue_size": self.function_queue.qsize(),
            "timestamp": time.time()
        }
        
        if self.start_time:
            status["uptime"] = time.time() - self.start_time
            
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    def send_urscript(self, script: str) -> bool:
        """Send URScript command via socket"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3.0)
            sock.connect((self.robot_ip, self.port))
            sock.send((script + "\n").encode('utf-8'))
            sock.close()
            return True
        except Exception as e:
            print(f"❌ Socket error: {e}")
            return False
    
    def load_function(self, function_name: str) -> Optional[List[Dict[str, Any]]]:
        """Load function from JSONL file"""
        function_file = self.functions_dir / f"{function_name}.jsonl"
        
        if not function_file.exists():
            return None
            
        commands = []
        try:
            with open(function_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        commands.append(json.loads(line))
            return commands
        except Exception as e:
            print(f"❌ Error loading function '{function_name}': {e}")
            return None
    
    def list_functions(self) -> List[str]:
        """List all available functions"""
        return [f.stem for f in self.functions_dir.glob("*.jsonl")]
    
    def add_function(self, function_name: str, speed: Optional[float] = None):
        """Add function to execution queue"""
        commands = self.load_function(function_name)
        if commands is None:
            print(f"❌ Function '{function_name}' not found")
            return False
            
        use_speed = speed if speed is not None else self.current_speed
        self.function_queue.put((function_name, commands, use_speed))
        print(f"✅ Added function '{function_name}' to queue (speed: {use_speed} m/s)")
        return True
    
    def pause(self):
        """Pause execution"""
        self.paused = True
        print("⏸️  Execution paused")
        self._write_response("Execution paused")
    
    def resume(self):
        """Resume execution"""
        self.paused = False
        print("▶️  Execution resumed")
        self._write_response("Execution resumed")
    
    def set_speed(self, speed: float):
        """Set base movement speed"""
        if 0.01 <= speed <= 1.0:
            self.current_speed = speed
            print(f"🚀 Speed set to {speed} m/s")
            self._write_response(f"Speed set to {speed} m/s")
        else:
            print("❌ Speed must be between 0.01 and 1.0 m/s")
            self._write_response("Invalid speed range")
    
    def set_speed_multiplier(self, multiplier: float):
        """Set speed multiplier for slow-down/speed-up"""
        if 0.1 <= multiplier <= 5.0:
            self.speed_multiplier = multiplier
            effective = self.current_speed * multiplier
            print(f"⚡ Speed multiplier set to {multiplier}x (effective: {effective:.3f} m/s)")
            self._write_response(f"Speed multiplier set to {multiplier}x")
        else:
            print("❌ Speed multiplier must be between 0.1 and 5.0")
            self._write_response("Invalid speed multiplier range")
    
    def slow_down(self):
        """Reduce speed by half"""
        new_multiplier = max(0.1, self.speed_multiplier * 0.5)
        self.set_speed_multiplier(new_multiplier)
    
    def speed_up(self):
        """Double the speed"""
        new_multiplier = min(5.0, self.speed_multiplier * 2.0)
        self.set_speed_multiplier(new_multiplier)
    
    def stop(self):
        """Stop execution and clear queues"""
        self.paused = False
        self.running = False
        
        # Clear queues
        while not self.function_queue.empty():
            try:
                self.function_queue.get_nowait()
            except queue.Empty:
                break
                
        while not self.command_queue.empty():
            try:
                self.command_queue.get_nowait()
            except queue.Empty:
                break
                
        print("🛑 Execution stopped and queues cleared")
        self._write_response("Execution stopped")
    
    def get_status(self):
        """Display current status"""
        effective_speed = self.current_speed * self.speed_multiplier
        uptime = time.time() - self.start_time if self.start_time else 0
        
        print(f"\n📊 Robot Controller Status:")
        print(f"   Running: {'✅' if self.running else '❌'}")
        print(f"   Paused: {'⏸️' if self.paused else '▶️'}")
        print(f"   Base Speed: {self.current_speed} m/s")
        print(f"   Speed Multiplier: {self.speed_multiplier}x")
        print(f"   Effective Speed: {effective_speed:.3f} m/s")
        print(f"   Functions Executed: {self.functions_executed}")
        print(f"   Commands Executed: {self.commands_executed}")
        print(f"   Queue Size: {self.function_queue.qsize()}")
        print(f"   Uptime: {uptime:.1f}s")
        print(f"   Robot IP: {self.robot_ip}")
    
    def _write_response(self, message: str):
        """Write response for external programs"""
        timestamp = time.strftime("%H:%M:%S")
        response = f"[{timestamp}] {message}\n"
        with open(self.response_file, 'a') as f:
            f.write(response)
    
    def _monitor_external_commands(self):
        """Monitor external command file for commands from other programs"""
        last_modified = 0
        
        while self.running:
            try:
                if self.command_file.exists():
                    current_modified = self.command_file.stat().st_mtime
                    
                    if current_modified > last_modified:
                        last_modified = current_modified
                        
                        # Read and process commands
                        commands = self.command_file.read_text().strip()
                        if commands:
                            # Clear the file
                            self.command_file.write_text("")
                            
                            # Process each command
                            for command in commands.split('\n'):
                                command = command.strip()
                                if command:
                                    self._process_external_command(command)
                
                time.sleep(0.1)  # Check every 100ms
                
            except Exception as e:
                print(f"⚠️  External command monitor error: {e}")
                time.sleep(1.0)
    
    def _process_external_command(self, command: str):
        """Process command from external program"""
        parts = command.split()
        if not parts:
            return
            
        cmd = parts[0].lower()
        
        try:
            if cmd == "pause":
                self.pause()
            elif cmd == "resume":
                self.resume()
            elif cmd == "stop":
                self.stop()
            elif cmd == "slow":
                self.slow_down()
            elif cmd == "fast":
                self.speed_up()
            elif cmd == "speed" and len(parts) > 1:
                speed = float(parts[1])
                self.set_speed(speed)
            elif cmd == "multiplier" and len(parts) > 1:
                multiplier = float(parts[1])
                self.set_speed_multiplier(multiplier)
            elif cmd == "add" and len(parts) > 1:
                function_name = parts[1]
                speed = float(parts[2]) if len(parts) > 2 else None
                self.add_function(function_name, speed)
            elif cmd == "status":
                self.get_status()
            else:
                print(f"⚠️  Unknown external command: {command}")
                self._write_response(f"Unknown command: {command}")
                
        except Exception as e:
            print(f"❌ External command error: {e}")
            self._write_response(f"Command error: {e}")
    
    def worker_function(self):
        """Main worker thread function"""
        print("🤖 Robot worker started")
        
        while self.running:
            # Update status file
            self._update_status_file()
            
            # Check for pause
            while self.paused and self.running:
                time.sleep(0.1)
                self._update_status_file()
            
            if not self.running:
                break
                
            # Process function queue first
            try:
                function_name, commands, base_speed = self.function_queue.get(timeout=1.0)
                
                print(f"\n🎯 Executing function '{function_name}' ({len(commands)} commands)")
                effective_speed = base_speed * self.speed_multiplier
                print(f"⚡ Effective speed: {effective_speed:.3f} m/s (base: {base_speed}, multiplier: {self.speed_multiplier}x)")
                
                # Convert function commands to robot commands
                for i, cmd in enumerate(commands):
                    if not self.running:
                        break
                    
                    # Wait if paused
                    while self.paused and self.running:
                        time.sleep(0.1)
                    
                    # Add pose command with current effective speed
                    pose = [cmd['x'], cmd['y'], cmd['z'], cmd['rx'], cmd['ry'], cmd['rz']]
                    current_effective = base_speed * self.speed_multiplier
                    self.command_queue.put(("pose", (pose, current_effective)))
                    
                    # Add gripper command if present
                    if 'gripper' in cmd:
                        self.command_queue.put(("gripper", cmd['gripper']))
                    
                    # Add wait between commands
                    self.command_queue.put(("wait", 1.5))
                
                self.functions_executed += 1
                self.function_queue.task_done()
                
                print(f"✅ Function '{function_name}' completed")
                
            except queue.Empty:
                # No functions to process, wait for commands or new functions
                pass
            
            # Process command queue
            try:
                cmd_type, data = self.command_queue.get(timeout=0.1)
                
                if cmd_type == "pose":
                    pose, speed = data
                    x, y, z, rx, ry, rz = pose
                    script = f"movel(p[{x}, {y}, {z}, {rx}, {ry}, {rz}], {speed:.3f}, 0.5)"
                    if self.send_urscript(script):
                        print(f"🎯 → [{x:6.3f}, {y:6.3f}, {z:6.3f}] @ {speed:.3f} m/s")
                        self.commands_executed += 1
                
                elif cmd_type == "gripper":
                    state = data
                    script = f"set_tool_digital_out(0, {bool(state)})"
                    if self.send_urscript(script):
                        status = "OPEN" if state else "CLOSE"
                        print(f"🦾 Gripper → {status}")
                        self.commands_executed += 1
                
                elif cmd_type == "wait":
                    duration = data
                    time.sleep(duration)
                
                self.command_queue.task_done()
                
            except queue.Empty:
                pass
    
    def input_handler(self):
        """Handle terminal input commands"""
        while self.running:
            try:
                user_input = input().strip().lower()
                
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0]
                
                if command in ['quit', 'exit', 'q']:
                    self.stop()
                    break
                elif command == 'help' or command == 'h':
                    self.show_help()
                elif command == 'list' or command == 'l':
                    functions = self.list_functions()
                    print(f"📋 Available functions: {', '.join(functions) if functions else 'None'}")
                elif command == 'add' or command == 'a':
                    if len(parts) > 1:
                        function_name = parts[1]
                        speed = float(parts[2]) if len(parts) > 2 else None
                        self.add_function(function_name, speed)
                    else:
                        print("❌ Usage: add <function_name> [speed]")
                elif command == 'pause' or command == 'p':
                    self.pause()
                elif command == 'resume' or command == 'r':
                    self.resume()
                elif command == 'stop' or command == 's':
                    self.stop()
                elif command == 'status':
                    self.get_status()
                elif command == 'speed':
                    if len(parts) > 1:
                        try:
                            speed = float(parts[1])
                            self.set_speed(speed)
                        except ValueError:
                            print("❌ Invalid speed value")
                    else:
                        print(f"Current speed: {self.current_speed} m/s")
                elif command == 'slow':
                    self.slow_down()
                elif command == 'fast':
                    self.speed_up()
                elif command == 'multiplier':
                    if len(parts) > 1:
                        try:
                            multiplier = float(parts[1])
                            self.set_speed_multiplier(multiplier)
                        except ValueError:
                            print("❌ Invalid multiplier value")
                    else:
                        print(f"Current multiplier: {self.speed_multiplier}x")
                else:
                    print(f"❌ Unknown command: {command}. Type 'help' for available commands.")
                    
            except EOFError:
                break
            except Exception as e:
                print(f"❌ Input error: {e}")
    
    def show_help(self):
        """Show available commands"""
        print("""
🤖 Enhanced Robot Control Commands:
Terminal Commands:
  help, h           - Show this help
  list, l           - List available functions
  add <func> [speed] - Add function to queue (optional speed)
  pause, p          - Pause execution
  resume, r         - Resume execution
  stop, s           - Stop and clear queues
  status            - Show current status
  speed <value>     - Set base speed (0.01-1.0 m/s)
  multiplier <val>  - Set speed multiplier (0.1-5.0x)
  slow              - Halve current speed multiplier
  fast              - Double current speed multiplier
  quit, exit, q     - Exit program

External Control:
  Write commands to: control/robot_commands.txt
  Read status from:  control/robot_status.json
  Read responses:    control/robot_response.txt
  
External Commands: pause, resume, stop, slow, fast, speed <val>, 
                  multiplier <val>, add <func> [speed], status
        """)
    
    def start(self):
        """Start the interactive robot controller"""
        self.running = True
        self.start_time = time.time()
        
        print("🚀 Enhanced Robot Control System Starting...")
        print(f"🔗 Connecting to robot at {self.robot_ip}:{self.port}")
        
        # Start threads
        self.worker_thread = threading.Thread(target=self.worker_function, daemon=True)
        self.input_thread = threading.Thread(target=self.input_handler, daemon=True)
        self.external_monitor_thread = threading.Thread(target=self._monitor_external_commands, daemon=True)
        
        self.worker_thread.start()
        self.input_thread.start()
        self.external_monitor_thread.start()
        
        print("✅ System ready!")
        print("📋 Type 'help' for commands")
        print("🎯 Waiting for functions...")
        print(f"📁 External control via: {self.control_dir}/")
        
        try:
            # Keep main thread alive
            while self.running:
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
            
        finally:
            self.running = False
            print("🔄 Shutting down...")
            
            # Wait for threads to finish
            if self.worker_thread and self.worker_thread.is_alive():
                self.worker_thread.join(timeout=2)
            if self.input_thread and self.input_thread.is_alive():
                self.input_thread.join(timeout=1)
            if self.external_monitor_thread and self.external_monitor_thread.is_alive():
                self.external_monitor_thread.join(timeout=1)
                
            print("✅ Shutdown complete")

def main():
    parser = argparse.ArgumentParser(description="Enhanced Interactive Robot Control System")
    parser.add_argument("--robot-ip", default="192.168.1.6", help="Robot IP address")
    parser.add_argument("--functions-dir", default="functions", help="Functions directory")
    parser.add_argument("--control-dir", default="control", help="External control directory")
    args = parser.parse_args()
    
    # Handle Ctrl+C gracefully
    controller = EnhancedRobotController(
        robot_ip=args.robot_ip,
        functions_dir=args.functions_dir,
        control_dir=args.control_dir
    )
    
    def signal_handler(signum, frame):
        print("\n🛑 Signal received, shutting down...")
        controller.running = False
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    controller.start()

if __name__ == "__main__":
    main()
