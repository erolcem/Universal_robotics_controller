#!/usr/bin/env python3
"""
Split Terminal Robot Control
Separate control terminal from output terminal
"""

import json
import time
import socket
import threading
import queue
import argparse
import sys
from pathlib import Path

class RobotController:
    """Robot controller with clean separation"""
    
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
        
        # Worker thread
        self.worker_thread = None
        
        # Ensure functions directory exists
        self.functions_dir.mkdir(exist_ok=True)
    
    def log_message(self, message: str, msg_type: str = "info"):
        """Log message with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        prefix = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warn": "⚠️",
            "robot": "🤖"
        }.get(msg_type, "ℹ️")
        
        print(f"[{timestamp}] {prefix} {message}", file=sys.stdout, flush=True)
    
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
            self.log_message(f"Command failed: {e}", "error")
            return False
    
    def load_function(self, function_name: str) -> list:
        """Load function from JSONL file"""
        function_file = self.functions_dir / f"{function_name}.jsonl"
        
        if not function_file.exists():
            self.log_message(f"Function '{function_name}' not found", "error")
            return []
        
        commands = []
        try:
            with open(function_file, 'r') as f:
                for line in f:
                    if line.strip():
                        commands.append(json.loads(line))
            
            self.log_message(f"Loaded function '{function_name}' ({len(commands)} commands)")
            return commands
            
        except Exception as e:
            self.log_message(f"Error loading function '{function_name}': {e}", "error")
            return []
    
    def queue_function(self, function_name: str, speed: float = 0.2):
        """Queue a function for execution"""
        commands = self.load_function(function_name)
        if commands:
            self.function_queue.put((function_name, commands, speed))
            self.log_message(f"Queued function '{function_name}' | Queue size: {self.function_queue.qsize()}")
            return True
        return False
    
    def get_available_functions(self):
        """Get list of available functions"""
        return [f.stem for f in self.functions_dir.glob("*.jsonl")]
    
    def get_status(self):
        """Get current status"""
        return {
            "running": self.running,
            "paused": self.paused,
            "current_function": self.current_function,
            "function_queue_size": self.function_queue.qsize(),
            "command_queue_size": self.command_queue.qsize(),
            "functions_executed": self.functions_executed,
            "commands_executed": self.commands_executed,
            "available_functions": self.get_available_functions()
        }
    
    def worker(self):
        """Worker thread"""
        self.log_message("Robot worker started", "success")
        
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
                    self.log_message(f"Executing '{function_name}' ({len(commands)} commands)", "robot")
                    
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
                    self.log_message(f"Function '{function_name}' completed", "success")
                    
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
                            self.log_message(f"Pose → [{x:6.3f}, {y:6.3f}, {z:6.3f}]", "robot")
                            self.commands_executed += 1
                    
                    elif cmd_type == "gripper":
                        state = data
                        script = f"set_tool_digital_out(0, {bool(state)})"
                        if self.send_urscript(script):
                            action = "closed" if state else "opened"
                            self.log_message(f"Gripper {action}", "robot")
                            self.commands_executed += 1
                    
                    elif cmd_type == "wait":
                        time.sleep(data)
                    
                    self.command_queue.task_done()
                    
                except queue.Empty:
                    pass
                
            except Exception as e:
                self.log_message(f"Worker error: {e}", "error")
                time.sleep(1)
        
        self.log_message("Robot worker stopped", "warn")
    
    def start(self):
        """Start the controller"""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self.worker, daemon=True)
        self.worker_thread.start()
        self.log_message("Robot controller started", "success")
    
    def stop(self):
        """Stop the controller"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2)
        self.log_message("Robot controller stopped", "warn")

def control_interface(controller):
    """Control interface for second terminal"""
    print("🎮 Robot Control Interface")
    print("=" * 40)
    
    while controller.running:
        try:
            print("\nCommands:")
            print("  list          - Show available functions")
            print("  status        - Show current status")
            print("  add <func>    - Add function to queue")
            print("  pause         - Pause/resume execution")
            print("  clear         - Clear function queue")
            print("  stop          - Stop robot")
            print("  quit          - Exit")
            
            cmd = input("\n> ").strip().lower()
            
            if cmd == "quit" or cmd == "exit":
                break
            
            elif cmd == "list":
                functions = controller.get_available_functions()
                print(f"\n📁 Available functions ({len(functions)}):")
                for func in functions:
                    print(f"  • {func}")
            
            elif cmd == "status":
                status = controller.get_status()
                print(f"\n📊 Status:")
                print(f"  Running: {'✅' if status['running'] else '❌'}")
                print(f"  Paused: {'⏸️' if status['paused'] else '▶️'}")
                print(f"  Current Function: {status['current_function'] or 'None'}")
                print(f"  Function Queue: {status['function_queue_size']}")
                print(f"  Command Queue: {status['command_queue_size']}")
                print(f"  Functions Executed: {status['functions_executed']}")
                print(f"  Commands Executed: {status['commands_executed']}")
            
            elif cmd.startswith("add "):
                function_name = cmd[4:].strip()
                if controller.queue_function(function_name):
                    print(f"✅ Added '{function_name}' to queue")
                else:
                    print(f"❌ Failed to add '{function_name}'")
            
            elif cmd == "pause":
                controller.paused = not controller.paused
                action = "paused" if controller.paused else "resumed"
                print(f"⏸️ Execution {action}")
            
            elif cmd == "clear":
                while not controller.function_queue.empty():
                    try:
                        controller.function_queue.get_nowait()
                    except:
                        break
                print("🗑️ Function queue cleared")
            
            elif cmd == "stop":
                controller.stop()
                print("🛑 Robot stopped")
                break
            
            else:
                print("❌ Unknown command")
                
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    print("\n👋 Control interface closed")

def main():
    parser = argparse.ArgumentParser(description='Split Terminal Robot Control')
    parser.add_argument('--ip', default='192.168.1.6', help='Robot IP')
    parser.add_argument('--functions-dir', default='functions', help='Functions directory')
    parser.add_argument('--control-only', action='store_true', help='Control interface only')
    
    args = parser.parse_args()
    
    # Create robot controller
    controller = RobotController(args.ip, args.functions_dir)
    
    if args.control_only:
        # Just run control interface
        control_interface(controller)
    else:
        # Start robot and show instructions
        controller.start()
        
        print("🤖 Robot Controller Output Terminal")
        print("=" * 40)
        print("💡 Open another terminal and run:")
        print(f"   python {sys.argv[0]} --control-only")
        print("=" * 40)
        
        try:
            # Keep main thread alive
            while controller.running:
                time.sleep(1)
        except KeyboardInterrupt:
            controller.stop()

if __name__ == "__main__":
    main()
