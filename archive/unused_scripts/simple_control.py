#!/usr/bin/env python3
"""
Simple Command Line Robot Control
No mixed output - clean command-response interface
"""

import json
import time
import socket
import threading
import queue
import argparse
import sys
from pathlib import Path

class SimpleRobotController:
    """Simple robot controller with clean CLI"""
    
    def __init__(self, robot_ip: str = "192.168.1.6", functions_dir: str = "functions"):
        self.robot_ip = robot_ip
        self.functions_dir = Path(functions_dir)
        
        # Queues and state
        self.function_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.paused = False
        self.running = False
        
        # Status
        self.current_function = ""
        self.functions_executed = 0
        self.commands_executed = 0
        self.last_result = ""
        
        # Worker thread
        self.worker_thread = None
        
        # Ensure functions directory exists
        self.functions_dir.mkdir(exist_ok=True)
    
    def send_urscript(self, script: str) -> bool:
        """Send URScript command via socket"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3.0)
            sock.connect((self.robot_ip, 30002))
            sock.send((script + "\n").encode('utf-8'))
            sock.close()
            return True
        except Exception as e:
            self.last_result = f"Command failed: {e}"
            return False
    
    def load_function(self, function_name: str) -> list:
        """Load function from JSONL file"""
        function_file = self.functions_dir / f"{function_name}.jsonl"
        
        if not function_file.exists():
            self.last_result = f"Function '{function_name}' not found"
            return []
        
        commands = []
        try:
            with open(function_file, 'r') as f:
                for line in f:
                    if line.strip():
                        commands.append(json.loads(line))
            
            self.last_result = f"Loaded function '{function_name}' ({len(commands)} commands)"
            return commands
            
        except Exception as e:
            self.last_result = f"Error loading function '{function_name}': {e}"
            return []
    
    def queue_function(self, function_name: str, speed: float = 0.2) -> str:
        """Queue a function for execution"""
        commands = self.load_function(function_name)
        if commands:
            self.function_queue.put((function_name, commands, speed))
            return f"✅ Queued '{function_name}' | Queue size: {self.function_queue.qsize()}"
        return f"❌ Failed to queue '{function_name}'"
    
    def get_available_functions(self) -> list:
        """Get list of available functions"""
        return [f.stem for f in self.functions_dir.glob("*.jsonl")]
    
    def get_status(self) -> str:
        """Get current status as formatted string"""
        status_lines = [
            f"Running: {'✅' if self.running else '❌'}",
            f"Paused: {'⏸️' if self.paused else '▶️'}",
            f"Current Function: {self.current_function or 'None'}",
            f"Function Queue: {self.function_queue.qsize()}",
            f"Command Queue: {self.command_queue.qsize()}",
            f"Functions Executed: {self.functions_executed}",
            f"Commands Executed: {self.commands_executed}",
        ]
        return "\n".join(status_lines)
    
    def worker(self):
        """Worker thread (silent execution)"""
        while self.running:
            try:
                # Handle pause
                while self.paused and self.running:
                    time.sleep(0.5)
                
                if not self.running:
                    break
                
                # Process functions
                try:
                    function_name, commands, speed = self.function_queue.get(timeout=1.0)
                    
                    self.current_function = function_name
                    
                    # Convert to robot commands
                    for cmd in commands:
                        if not self.running:
                            break
                        
                        while self.paused and self.running:
                            time.sleep(0.1)
                        
                        # Pose command
                        pose = [cmd['x'], cmd['y'], cmd['z'], cmd['rx'], cmd['ry'], cmd['rz']]
                        self.command_queue.put(("pose", (pose, speed)))
                        
                        # Gripper command
                        if 'gripper' in cmd:
                            self.command_queue.put(("gripper", cmd['gripper']))
                        
                        self.command_queue.put(("wait", 1.5))
                    
                    self.functions_executed += 1
                    self.current_function = ""
                    self.function_queue.task_done()
                    
                except queue.Empty:
                    pass
                
                # Process commands
                try:
                    cmd_type, data = self.command_queue.get(timeout=0.1)
                    
                    if cmd_type == "pose":
                        pose, speed = data
                        x, y, z, rx, ry, rz = pose
                        script = f"movel(p[{x}, {y}, {z}, {rx}, {ry}, {rz}], {speed}, 0.5)"
                        if self.send_urscript(script):
                            self.commands_executed += 1
                    
                    elif cmd_type == "gripper":
                        state = data
                        script = f"set_tool_digital_out(0, {bool(state)})"
                        if self.send_urscript(script):
                            self.commands_executed += 1
                    
                    elif cmd_type == "wait":
                        time.sleep(data)
                    
                    self.command_queue.task_done()
                    
                except queue.Empty:
                    pass
                
            except Exception as e:
                self.last_result = f"Worker error: {e}"
                time.sleep(1)
    
    def start(self):
        """Start the controller"""
        if self.running:
            return "Already running"
        
        self.running = True
        self.worker_thread = threading.Thread(target=self.worker, daemon=True)
        self.worker_thread.start()
        return "✅ Robot controller started"
    
    def stop(self):
        """Stop the controller"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2)
        return "✅ Robot controller stopped"
    
    def pause_resume(self):
        """Toggle pause state"""
        self.paused = not self.paused
        action = "paused" if self.paused else "resumed"
        return f"⏸️ Execution {action}"
    
    def clear_queue(self):
        """Clear function queue"""
        count = 0
        while not self.function_queue.empty():
            try:
                self.function_queue.get_nowait()
                count += 1
            except:
                break
        return f"🗑️ Cleared {count} functions from queue"

def main():
    parser = argparse.ArgumentParser(description='Simple Command Line Robot Control')
    parser.add_argument('--ip', default='192.168.1.6', help='Robot IP')
    parser.add_argument('--functions-dir', default='functions', help='Functions directory')
    
    args = parser.parse_args()
    
    # Create robot controller
    controller = SimpleRobotController(args.ip, args.functions_dir)
    
    print("🤖 Simple Robot Control")
    print("=" * 40)
    print("Type 'help' for commands, 'quit' to exit")
    print("=" * 40)
    
    # Start robot
    print(controller.start())
    
    try:
        while True:
            try:
                cmd = input("\nrobot> ").strip()
                
                if not cmd:
                    continue
                
                if cmd in ['quit', 'exit', 'q']:
                    break
                
                elif cmd == 'help':
                    print("""
Available commands:
  help              - Show this help
  start             - Start robot controller
  stop              - Stop robot controller
  status            - Show current status
  list              - List available functions
  add <function>    - Add function to queue
  pause             - Pause/resume execution
  clear             - Clear function queue
  quit              - Exit program
                    """)
                
                elif cmd == 'start':
                    print(controller.start())
                
                elif cmd == 'stop':
                    print(controller.stop())
                
                elif cmd == 'status':
                    print(controller.get_status())
                
                elif cmd == 'list':
                    functions = controller.get_available_functions()
                    if functions:
                        print(f"📁 Available functions ({len(functions)}):")
                        for func in functions:
                            print(f"  • {func}")
                    else:
                        print("No functions found")
                
                elif cmd.startswith('add '):
                    function_name = cmd[4:].strip()
                    if function_name:
                        print(controller.queue_function(function_name))
                    else:
                        print("❌ Please specify a function name")
                
                elif cmd == 'pause':
                    print(controller.pause_resume())
                
                elif cmd == 'clear':
                    print(controller.clear_queue())
                
                else:
                    print(f"❌ Unknown command: {cmd}")
                    print("Type 'help' for available commands")
                
            except KeyboardInterrupt:
                break
            except EOFError:
                break
    
    finally:
        print(f"\n{controller.stop()}")
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
