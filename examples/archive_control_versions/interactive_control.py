#!/usr/bin/env python3
"""
Interactive Function-Based Robot Control
Real-time function queuing and execution system
"""

import json
import time
import socket
import threading
import queue
import argparse
import signal
import sys
from pathlib import Path

class InteractiveRobotController:
    """Interactive robot controller with real-time function queuing"""
    
    def __init__(self, robot_ip: str = "192.168.1.6", functions_dir: str = "functions"):
        self.robot_ip = robot_ip
        self.port = 30002
        self.functions_dir = Path(functions_dir)
        
        # Queues and state
        self.function_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.paused = False
        self.running = False
        
        # Threads
        self.worker_thread = None
        self.input_thread = None
        
        # Statistics
        self.functions_executed = 0
        self.commands_executed = 0
        
        # Ensure functions directory exists
        self.functions_dir.mkdir(exist_ok=True)
        
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
            print(f"❌ Command failed: {e}")
            return False
    
    def load_function(self, function_name: str) -> list:
        """Load a function (JSONL file) and return commands"""
        function_file = self.functions_dir / f"{function_name}.jsonl"
        
        if not function_file.exists():
            print(f"❌ Function '{function_name}' not found in {self.functions_dir}")
            return []
        
        commands = []
        try:
            with open(function_file, 'r') as f:
                for line in f:
                    if line.strip():
                        commands.append(json.loads(line))
            
            print(f"📁 Loaded function '{function_name}' with {len(commands)} commands")
            return commands
            
        except Exception as e:
            print(f"❌ Error loading function '{function_name}': {e}")
            return []
    
    def queue_function(self, function_name: str, speed: float = 0.2):
        """Queue a function for execution"""
        commands = self.load_function(function_name)
        if commands:
            self.function_queue.put((function_name, commands, speed))
            print(f"📥 Queued function '{function_name}' | Queue size: {self.function_queue.qsize()}")
            return True
        return False
    
    def worker(self):
        """Main worker thread that processes functions and commands"""
        print("🔄 Interactive robot worker started")
        
        while self.running:
            try:
                # Check if paused
                while self.paused and self.running:
                    print("⏸️  Worker paused", end='\r')
                    time.sleep(0.5)
                
                if not self.running:
                    break
                
                # Process function queue first
                try:
                    function_name, commands, speed = self.function_queue.get(timeout=1.0)
                    
                    print(f"\n🎯 Executing function '{function_name}' ({len(commands)} commands)")
                    print(f"⚡ Speed: {speed} m/s")
                    
                    # Convert function commands to robot commands
                    for i, cmd in enumerate(commands):
                        if not self.running:
                            break
                        
                        # Wait if paused
                        while self.paused and self.running:
                            time.sleep(0.1)
                        
                        # Add pose command
                        pose = [cmd['x'], cmd['y'], cmd['z'], cmd['rx'], cmd['ry'], cmd['rz']]
                        self.command_queue.put(("pose", (pose, speed)))
                        
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
                        script = f"movel(p[{x}, {y}, {z}, {rx}, {ry}, {rz}], {speed}, 0.5)"
                        if self.send_urscript(script):
                            print(f"🎯 → [{x:6.3f}, {y:6.3f}, {z:6.3f}]")
                            self.commands_executed += 1
                    
                    elif cmd_type == "gripper":
                        state = data
                        script = f"set_tool_digital_out(0, {bool(state)})"
                        if self.send_urscript(script):
                            action = "closed" if state else "opened"
                            print(f"🤏 Gripper {action}")
                            self.commands_executed += 1
                    
                    elif cmd_type == "wait":
                        duration = data
                        time.sleep(duration)
                    
                    self.command_queue.task_done()
                    
                except queue.Empty:
                    # Show waiting status when no commands
                    if self.function_queue.empty() and self.command_queue.empty():
                        print("⏳ Waiting for functions...", end='\r')
                        time.sleep(1)
                
            except Exception as e:
                print(f"❌ Worker error: {e}")
                time.sleep(1)
        
        print("\n🔄 Interactive robot worker stopped")
    
    def input_handler(self):
        """Handle interactive input commands"""
        print("\n" + "="*50)
        print("🎮 INTERACTIVE ROBOT CONTROL")
        print("="*50)
        print("Commands:")
        print("  add <function_name> [speed]  - Queue a function")
        print("  pause                        - Pause execution")
        print("  resume                       - Resume execution") 
        print("  status                       - Show status")
        print("  list                         - List available functions")
        print("  clear                        - Clear function queue")
        print("  quit                         - Stop and exit")
        print("="*50)
        
        while self.running:
            try:
                command = input("\n🤖 > ").strip().lower()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0]
                
                if cmd == "add" and len(parts) >= 2:
                    function_name = parts[1]
                    speed = float(parts[2]) if len(parts) > 2 else 0.2
                    self.queue_function(function_name, speed)
                
                elif cmd == "pause":
                    self.paused = True
                    print("⏸️  Execution paused")
                
                elif cmd == "resume":
                    self.paused = False
                    print("▶️  Execution resumed")
                
                elif cmd == "status":
                    print(f"\n📊 Status:")
                    print(f"   Functions in queue: {self.function_queue.qsize()}")
                    print(f"   Commands in queue: {self.command_queue.qsize()}")
                    print(f"   Execution state: {'Paused' if self.paused else 'Running'}")
                    print(f"   Functions executed: {self.functions_executed}")
                    print(f"   Commands executed: {self.commands_executed}")
                
                elif cmd == "list":
                    functions = list(self.functions_dir.glob("*.jsonl"))
                    if functions:
                        print(f"\n📁 Available functions in {self.functions_dir}:")
                        for f in functions:
                            print(f"   {f.stem}")
                    else:
                        print(f"📁 No functions found in {self.functions_dir}")
                
                elif cmd == "clear":
                    # Clear function queue
                    while not self.function_queue.empty():
                        try:
                            self.function_queue.get_nowait()
                        except queue.Empty:
                            break
                    print("🗑️  Function queue cleared")
                
                elif cmd in ["quit", "exit", "q"]:
                    print("👋 Stopping...")
                    self.stop()
                    break
                
                else:
                    print("❌ Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                print("\n👋 Stopping...")
                self.stop()
                break
            except Exception as e:
                print(f"❌ Input error: {e}")
    
    def start(self):
        """Start the interactive controller"""
        if self.running:
            return
        
        self.running = True
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self.worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        
        # Start input handler thread
        self.input_thread = threading.Thread(target=self.input_handler)
        self.input_thread.daemon = True
        self.input_thread.start()
        
        print("✅ Interactive robot controller started")
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the interactive controller"""
        if not self.running:
            return
        
        self.running = False
        
        # Join threads
        if self.worker_thread:
            self.worker_thread.join(timeout=2.0)
        
        print("✅ Interactive robot controller stopped")

def main():
    parser = argparse.ArgumentParser(description='Interactive Function-Based Robot Control')
    parser.add_argument('--ip', default='192.168.1.6', help='Robot IP address')
    parser.add_argument('--functions-dir', default='functions', help='Functions directory')
    
    args = parser.parse_args()
    
    controller = InteractiveRobotController(args.ip, args.functions_dir)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n🛑 Received interrupt signal")
        controller.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    controller.start()

if __name__ == "__main__":
    main()
