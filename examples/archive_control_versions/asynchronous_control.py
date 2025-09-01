#!/usr/bin/env python3
"""
Asynchronous Robot Control with Gripper
Continuous streaming of commands with real-time control
"""

import json
import time
import socket
import argparse
import threading
import queue
from pathlib import Path

class AsyncRobotController:
    """Asynchronous robot controller using socket communication"""
    
    def __init__(self, robot_ip: str = "192.168.1.6"):
        self.robot_ip = robot_ip
        self.port = 30002
        self.command_queue = queue.Queue()
        self.running = False
        self.worker_thread = None
        
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
    
    def worker(self):
        """Worker thread that processes commands asynchronously"""
        print("🔄 Async worker started")
        
        while self.running:
            try:
                # Get command with timeout
                cmd_type, data = self.command_queue.get(timeout=1.0)
                
                if cmd_type == "pose":
                    x, y, z, rx, ry, rz, speed = data
                    script = f"movel(p[{x}, {y}, {z}, {rx}, {ry}, {rz}], {speed}, 0.5)"
                    if self.send_urscript(script):
                        print(f"🎯 Pose → [{x:6.3f}, {y:6.3f}, {z:6.3f}]")
                    
                elif cmd_type == "gripper":
                    state = data
                    script = f"set_tool_digital_out(0, {bool(state)})"
                    if self.send_urscript(script):
                        action = "closed" if state else "opened"
                        print(f"🤏 Gripper {action}")
                
                elif cmd_type == "wait":
                    duration = data
                    print(f"⏱️  Wait {duration}s")
                    time.sleep(duration)
                
                elif cmd_type == "stop":
                    print("⏹️  Stop command received")
                    break
                
                self.command_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Worker error: {e}")
        
        print("🔄 Async worker stopped")
    
    def start(self):
        """Start the async controller"""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self.worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        
        print("✅ Async controller started")
    
    def stop(self):
        """Stop the async controller"""
        if not self.running:
            return
        
        self.command_queue.put(("stop", None))
        self.running = False
        
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
        
        print("✅ Async controller stopped")
    
    def move_to_pose(self, pose: list, speed: float = 0.2):
        """Queue a pose movement command"""
        x, y, z, rx, ry, rz = pose
        self.command_queue.put(("pose", (x, y, z, rx, ry, rz, speed)))
    
    def set_gripper(self, state: int):
        """Queue a gripper command"""
        self.command_queue.put(("gripper", state))
    
    def wait(self, duration: float):
        """Queue a wait command"""
        self.command_queue.put(("wait", duration))
    
    def queue_size(self):
        """Get current queue size"""
        return self.command_queue.qsize()

def run_asynchronous_control(commands_file: str, robot_ip: str = "192.168.1.6", 
                           speed: float = 0.2, no_gripper: bool = False):
    """Run asynchronous pose control with optional gripper"""
    
    print("🤖 Asynchronous Robot Control")
    print("=" * 45)
    print(f"📁 Commands: {commands_file}")
    print(f"🏃 Speed: {speed} m/s")
    print(f"🤏 Gripper: {'Disabled' if no_gripper else 'Enabled'}")
    print(f"⚡ Mode: Continuous streaming")
    print("=" * 45)
    
    # Load commands
    commands = []
    try:
        with open(commands_file, 'r') as f:
            for line in f:
                if line.strip():
                    commands.append(json.loads(line))
        print(f"📋 Loaded {len(commands)} commands")
    except Exception as e:
        print(f"❌ Could not load commands: {e}")
        return False
    
    # Initialize async controller
    controller = AsyncRobotController(robot_ip)
    controller.start()
    
    try:
        # Initialize gripper
        if not no_gripper:
            print("🤏 Initializing gripper...")
            controller.set_gripper(0)  # Open
            controller.wait(1.0)
        
        print(f"\n🎯 Streaming {len(commands)} commands...")
        print("Commands are queued and executed asynchronously")
        print("Press Ctrl+C to stop")
        print("-" * 45)
        
        # Queue all commands
        for i, cmd in enumerate(commands):
            # Extract pose
            pose = [cmd['x'], cmd['y'], cmd['z'], cmd['rx'], cmd['ry'], cmd['rz']]
            
            # Queue pose movement
            controller.move_to_pose(pose, speed)
            
            # Queue gripper command if enabled
            if not no_gripper and 'gripper' in cmd:
                controller.set_gripper(cmd['gripper'])
            
            # Add timing between commands
            controller.wait(1.5)
            
            print(f"📤 Queued command {i+1}/{len(commands)} | Queue size: {controller.queue_size()}")
            
            # Small delay to prevent overwhelming
            time.sleep(0.1)
        
        # Wait for queue to be processed
        print(f"\n⏳ Processing {controller.queue_size()} queued commands...")
        
        while controller.queue_size() > 0:
            print(f"⏳ Queue: {controller.queue_size()} remaining", end='\r')
            time.sleep(1)
        
        # Final cleanup
        if not no_gripper:
            print("\n🤏 Final gripper open...")
            controller.set_gripper(0)
            controller.wait(1.0)
        
        print("\n✅ All commands processed!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Interrupted by user")
    
    finally:
        controller.stop()
        time.sleep(1)
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Asynchronous Robot Control')
    parser.add_argument('commands', nargs='?', 
                       default='synchronous_poses_with_gripper.jsonl',
                       help='Commands file (default: synchronous_poses_with_gripper.jsonl)')
    parser.add_argument('--ip', default='192.168.1.6', 
                       help='Robot IP address')
    parser.add_argument('--speed', type=float, default=0.2, 
                       help='Movement speed (m/s)')
    parser.add_argument('--no-gripper', action='store_true',
                       help='Disable gripper control')
    
    args = parser.parse_args()
    
    success = run_asynchronous_control(
        commands_file=args.commands,
        robot_ip=args.ip,
        speed=args.speed,
        no_gripper=args.no_gripper
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
