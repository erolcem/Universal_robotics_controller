#!/usr/bin/env python3
"""
Unified Robot Control System
Integrates UR robot arm control with MIR base control for collaborative robotics

Features:
- UR robot function queuing and execution
- MIR base pause/resume coordination
- Synchronized multi-robot operations
- Real-time interactive control
- External program interface
- Collaborative workflow management
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
import requests

# Import MIR control from YW_MiR directory
sys.path.append(str(Path(__file__).parent / "YW_MiR"))
from simple_mir_control import SimpleMiRControl


class UnifiedRobotController:
    """Unified controller for UR robot arm and MIR base"""
    
    def __init__(self, 
                 ur_ip: str = "192.168.1.6", 
                 mir_ip: str = "mir.com",
                 functions_dir: str = "functions", 
                 control_dir: str = "control"):
        
        # UR Robot configuration
        self.ur_ip = ur_ip
        self.ur_port = 30002
        
        # MIR Base configuration  
        self.mir_ip = mir_ip
        
        # Directory setup
        self.functions_dir = Path(functions_dir)
        self.control_dir = Path(control_dir)
        
        # Queues and state
        self.function_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.paused = False
        self.running = False
        
        # UR Speed control
        self.current_speed = 0.1  # m/s
        self.speed_multiplier = 1.0
        
        # MIR control
        self.mir_control = None
        self.mir_enabled = False
        self.mir_auto_pause = True  # Automatically pause MIR during UR operations
        
        # Threads
        self.worker_thread = None
        self.input_thread = None
        self.external_monitor_thread = None
        
        # Statistics
        self.ur_functions_executed = 0
        self.ur_commands_executed = 0
        self.mir_operations = 0
        self.start_time = None
        
        # Control files for external interface
        self.command_file = self.control_dir / "robot_commands.txt"
        self.status_file = self.control_dir / "robot_status.json"
        self.response_file = self.control_dir / "robot_response.txt"
        
        # Ensure directories exist
        self.functions_dir.mkdir(exist_ok=True)
        self.control_dir.mkdir(exist_ok=True)
        
        # Initialize systems
        self._init_control_files()
        self._init_mir_control()
    
    def _init_control_files(self):
        """Initialize external control interface files"""
        self.command_file.write_text("")
        self.response_file.write_text("")
        self._update_status_file()
    
    def _init_mir_control(self):
        """Initialize MIR control system"""
        try:
            print(f"🔗 Connecting to MIR base at {self.mir_ip}...")
            self.mir_control = SimpleMiRControl(self.mir_ip)
            
            # Test connection
            if self.mir_control._get_status():
                self.mir_enabled = True
                print("✅ MIR base connected successfully")
                self._write_response("MIR base connected")
            else:
                print("⚠️  MIR base connection failed - continuing without MIR")
                self.mir_enabled = False
                
        except Exception as e:
            print(f"⚠️  MIR initialization error: {e}")
            print("   Continuing without MIR base control")
            self.mir_enabled = False
    
    def _update_status_file(self):
        """Update status file for external monitoring"""
        status = {
            "systems": {
                "ur_robot": {
                    "ip": self.ur_ip,
                    "running": self.running,
                    "paused": self.paused,
                    "current_speed": self.current_speed,
                    "speed_multiplier": self.speed_multiplier,
                    "effective_speed": self.current_speed * self.speed_multiplier,
                    "functions_executed": self.ur_functions_executed,
                    "commands_executed": self.ur_commands_executed,
                    "queue_size": self.function_queue.qsize()
                },
                "mir_base": {
                    "ip": self.mir_ip,
                    "enabled": self.mir_enabled,
                    "auto_pause": self.mir_auto_pause,
                    "operations": self.mir_operations,
                    "connected": self.mir_control is not None
                }
            },
            "timestamp": time.time()
        }
        
        if self.start_time:
            status["uptime"] = time.time() - self.start_time
        
        # Add MIR status if available
        if self.mir_enabled and self.mir_control:
            try:
                mir_pos = self.mir_control.get_position()
                mir_battery = self.mir_control.get_battery()
                mir_ready = self.mir_control.is_ready()
                mir_paused = self.mir_control.is_paused()
                
                status["systems"]["mir_base"].update({
                    "position": mir_pos,
                    "battery": mir_battery,
                    "ready": mir_ready,
                    "paused": mir_paused
                })
            except Exception as e:
                status["systems"]["mir_base"]["status_error"] = str(e)
            
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    # UR Robot Control Methods
    def send_urscript(self, script: str) -> bool:
        """Send URScript command via socket"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3.0)
            sock.connect((self.ur_ip, self.ur_port))
            sock.send((script + "\n").encode('utf-8'))
            sock.close()
            return True
        except Exception as e:
            print(f"❌ UR Socket error: {e}")
            return False
    
    def load_ur_function(self, function_name: str) -> Optional[List[Dict[str, Any]]]:
        """Load UR function from JSONL file"""
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
            print(f"❌ Error loading UR function '{function_name}': {e}")
            return None
    
    def list_ur_functions(self) -> List[str]:
        """List all available UR functions"""
        return [f.stem for f in self.functions_dir.glob("*.jsonl")]
    
    def add_ur_function(self, function_name: str, speed: Optional[float] = None, pause_mir: bool = None):
        """Add UR function to execution queue with optional MIR coordination"""
        commands = self.load_ur_function(function_name)
        if commands is None:
            print(f"❌ UR Function '{function_name}' not found")
            return False
            
        use_speed = speed if speed is not None else self.current_speed
        
        # Determine if MIR should be paused
        mir_pause = pause_mir if pause_mir is not None else self.mir_auto_pause
        
        self.function_queue.put((function_name, commands, use_speed, mir_pause))
        print(f"✅ Added UR function '{function_name}' to queue (speed: {use_speed} m/s, MIR pause: {mir_pause})")
        return True
    
    # MIR Base Control Methods
    def mir_pause(self) -> bool:
        """Pause MIR base"""
        if not self.mir_enabled:
            print("⚠️  MIR not enabled")
            return False
            
        try:
            success = self.mir_control.pause()
            if success:
                self.mir_operations += 1
                print("⏸️  MIR base paused")
                self._write_response("MIR paused")
            return success
        except Exception as e:
            print(f"❌ MIR pause error: {e}")
            return False
    
    def mir_resume(self) -> bool:
        """Resume MIR base"""
        if not self.mir_enabled:
            print("⚠️  MIR not enabled")
            return False
            
        try:
            success = self.mir_control.resume()
            if success:
                self.mir_operations += 1
                print("▶️  MIR base resumed")
                self._write_response("MIR resumed")
            return success
        except Exception as e:
            print(f"❌ MIR resume error: {e}")
            return False
    
    def mir_status(self):
        """Display MIR status"""
        if not self.mir_enabled:
            print("❌ MIR not enabled")
            return
            
        try:
            self.mir_control.status_summary()
        except Exception as e:
            print(f"❌ MIR status error: {e}")
    
    def set_mir_auto_pause(self, enabled: bool):
        """Enable/disable automatic MIR pausing during UR operations"""
        self.mir_auto_pause = enabled
        status = "enabled" if enabled else "disabled"
        print(f"🤖 MIR auto-pause {status}")
        self._write_response(f"MIR auto-pause {status}")
    
    # Unified Control Methods
    def pause(self):
        """Pause entire system"""
        self.paused = True
        print("⏸️  Unified system paused")
        
        # Also pause MIR if enabled
        if self.mir_enabled:
            self.mir_pause()
            
        self._write_response("Unified system paused")
    
    def resume(self):
        """Resume entire system"""
        self.paused = False
        print("▶️  Unified system resumed")
        
        # Also resume MIR if enabled
        if self.mir_enabled:
            self.mir_resume()
            
        self._write_response("Unified system resumed")
    
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
        
        print("🛑 Unified system stopped and queues cleared")
        self._write_response("Unified system stopped")
    
    def set_speed(self, speed: float):
        """Set base UR movement speed"""
        if 0.01 <= speed <= 1.0:
            self.current_speed = speed
            print(f"🚀 UR speed set to {speed} m/s")
            self._write_response(f"UR speed set to {speed} m/s")
        else:
            print("❌ UR speed must be between 0.01 and 1.0 m/s")
            self._write_response("Invalid UR speed range")
    
    def set_speed_multiplier(self, multiplier: float):
        """Set UR speed multiplier"""
        if 0.1 <= multiplier <= 5.0:
            self.speed_multiplier = multiplier
            effective = self.current_speed * multiplier
            print(f"⚡ UR speed multiplier set to {multiplier}x (effective: {effective:.3f} m/s)")
            self._write_response(f"UR speed multiplier set to {multiplier}x")
        else:
            print("❌ UR speed multiplier must be between 0.1 and 5.0")
            self._write_response("Invalid UR speed multiplier range")
    
    def get_status(self):
        """Display unified system status"""
        effective_speed = self.current_speed * self.speed_multiplier
        uptime = time.time() - self.start_time if self.start_time else 0
        
        print(f"\\n📊 Unified Robot System Status:")
        print(f"   System Running: {'✅' if self.running else '❌'}")
        print(f"   System Paused: {'⏸️' if self.paused else '▶️'}")
        print(f"   Uptime: {uptime:.1f}s")
        
        print(f"\\n🤖 UR Robot Arm:")
        print(f"   IP: {self.ur_ip}")
        print(f"   Base Speed: {self.current_speed} m/s")
        print(f"   Speed Multiplier: {self.speed_multiplier}x")
        print(f"   Effective Speed: {effective_speed:.3f} m/s")
        print(f"   Functions Executed: {self.ur_functions_executed}")
        print(f"   Commands Executed: {self.ur_commands_executed}")
        print(f"   Queue Size: {self.function_queue.qsize()}")
        
        print(f"\\n🚁 MIR Base:")
        print(f"   IP: {self.mir_ip}")
        print(f"   Enabled: {'✅' if self.mir_enabled else '❌'}")
        print(f"   Auto-pause: {'✅' if self.mir_auto_pause else '❌'}")
        print(f"   Operations: {self.mir_operations}")
        
        if self.mir_enabled:
            try:
                pos = self.mir_control.get_position()
                battery = self.mir_control.get_battery()
                ready = self.mir_control.is_ready()
                mir_paused = self.mir_control.is_paused()
                
                print(f"   Position: x={pos['x']:.2f}, y={pos['y']:.2f}, θ={pos['orientation']:.1f}°")
                print(f"   Battery: {battery:.1f}%")
                print(f"   Ready: {'✅' if ready else '❌'}")
                print(f"   Paused: {'⏸️' if mir_paused else '▶️'}")
            except Exception as e:
                print(f"   Status Error: {e}")
    
    def _write_response(self, message: str):
        """Write response for external programs"""
        timestamp = time.strftime("%H:%M:%S")
        response = f"[{timestamp}] {message}\\n"
        with open(self.response_file, 'a') as f:
            f.write(response)
    
    def _monitor_external_commands(self):
        """Monitor external command file"""
        last_modified = 0
        
        while self.running:
            try:
                if self.command_file.exists():
                    current_modified = self.command_file.stat().st_mtime
                    
                    if current_modified > last_modified:
                        last_modified = current_modified
                        
                        commands = self.command_file.read_text().strip()
                        if commands:
                            self.command_file.write_text("")
                            
                            for command in commands.split('\\n'):
                                command = command.strip()
                                if command:
                                    self._process_external_command(command)
                
                time.sleep(0.1)
                
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
            # System control
            if cmd == "pause":
                self.pause()
            elif cmd == "resume":
                self.resume()
            elif cmd == "stop":
                self.stop()
            elif cmd == "status":
                self.get_status()
                
            # UR control
            elif cmd == "speed" and len(parts) > 1:
                speed = float(parts[1])
                self.set_speed(speed)
            elif cmd == "multiplier" and len(parts) > 1:
                multiplier = float(parts[1])
                self.set_speed_multiplier(multiplier)
            elif cmd == "ur_add" and len(parts) > 1:
                function_name = parts[1]
                speed = float(parts[2]) if len(parts) > 2 else None
                pause_mir = parts[3].lower() == "true" if len(parts) > 3 else None
                self.add_ur_function(function_name, speed, pause_mir)
                
            # MIR control
            elif cmd == "mir_pause":
                self.mir_pause()
            elif cmd == "mir_resume":
                self.mir_resume()
            elif cmd == "mir_status":
                self.mir_status()
            elif cmd == "mir_auto" and len(parts) > 1:
                enabled = parts[1].lower() == "true"
                self.set_mir_auto_pause(enabled)
                
            # Collaborative operations
            elif cmd == "collab_add" and len(parts) > 1:
                # Add UR function with MIR coordination
                function_name = parts[1]
                speed = float(parts[2]) if len(parts) > 2 else None
                self.add_ur_function(function_name, speed, pause_mir=True)
                
            else:
                print(f"⚠️  Unknown external command: {command}")
                self._write_response(f"Unknown command: {command}")
                
        except Exception as e:
            print(f"❌ External command error: {e}")
            self._write_response(f"Command error: {e}")
    
    def worker_function(self):
        """Main worker thread function"""
        print("🤖 Unified robot worker started")
        
        while self.running:
            self._update_status_file()
            
            try:
                # Check for new functions to execute
                function_name, commands, speed, pause_mir = self.function_queue.get(timeout=0.1)
                
                if not self.running:
                    break
                
                print(f"\\n🔧 Executing UR function: {function_name}")
                
                # Pause MIR if requested
                mir_was_paused = False
                if pause_mir and self.mir_enabled:
                    mir_was_paused = True
                    self.mir_pause()
                    time.sleep(0.5)  # Brief pause to ensure MIR stops
                
                # Execute UR function
                try:
                    for i, command in enumerate(commands):
                        # Check if paused
                        while self.paused and self.running:
                            time.sleep(0.1)
                            self._update_status_file()
                        
                        if not self.running:
                            break
                        
                        # Apply speed for movement commands
                        if "type" in command and command["type"] in ["movej", "movel"]:
                            command["speed"] = speed * self.speed_multiplier
                        elif "x" in command:  # Old format - apply speed directly
                            command["speed"] = speed * self.speed_multiplier
                        
                        # Send command
                        script = self._build_urscript(command)
                        if script:
                            success = self.send_urscript(script)
                            if success:
                                self.ur_commands_executed += 1
                                # Display command type - improved detection
                                if "type" in command:
                                    cmd_display = command["type"]
                                elif "x" in command:
                                    cmd_display = "movel"
                                else:
                                    cmd_display = "unknown"
                                print(f"   ✅ Command {i+1}/{len(commands)}: {cmd_display}")
                            else:
                                # Display command type - improved detection
                                if "type" in command:
                                    cmd_display = command["type"]
                                elif "x" in command:
                                    cmd_display = "movel"
                                else:
                                    cmd_display = "unknown"
                                print(f"   ❌ Command {i+1}/{len(commands)} failed: {cmd_display}")
                            
                            # Wait between commands
                            time.sleep(0.1)
                    
                    self.ur_functions_executed += 1
                    print(f"✅ UR function '{function_name}' completed")
                    
                except Exception as e:
                    print(f"❌ Error executing UR function '{function_name}': {e}")
                
                finally:
                    # Resume MIR if it was paused for this operation
                    if mir_was_paused and self.mir_enabled:
                        time.sleep(0.5)  # Brief pause before resuming
                        self.mir_resume()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"❌ Worker error: {e}")
                time.sleep(1.0)
    
    def _build_urscript(self, command: Dict[str, Any]) -> Optional[str]:
        """Build URScript from command dictionary"""
        try:
            # Handle new format with explicit type
            if "type" in command:
                cmd_type = command["type"]
                
                if cmd_type == "movej":
                    joints = command["joints"]
                    speed = command.get("speed", 0.1)
                    accel = command.get("accel", 0.3)
                    return f"movej({joints}, a={accel}, v={speed})"
                    
                elif cmd_type == "movel":
                    pose = command["pose"]
                    speed = command.get("speed", 0.1)
                    accel = command.get("accel", 0.3)
                    return f"movel(p{pose}, a={accel}, v={speed})"
                    
                elif cmd_type == "sleep":
                    duration = command["duration"]
                    return f"sleep({duration})"
                    
                elif cmd_type == "gripper":
                    action = command["action"]
                    if action == "open":
                        def _build_urscript(self, command: Dict[str, Any]) -> Optional[str]:
        """Build URScript from command dictionary"""
        try:
            # Handle new format with "type" field
            if "type" in command:
                cmd_type = command["type"]
                
                if cmd_type == "movej":
                    joints = command["joints"]
                    speed = command.get("speed", 0.1)
                    accel = command.get("accel", 0.3)
                    return f"movej({joints}, a={accel}, v={speed})"
                    
                elif cmd_type == "movel":
                    pose = command["pose"]
                    speed = command.get("speed", 0.1)
                    accel = command.get("accel", 0.3)
                    return f"movel(p{pose}, a={accel}, v={speed})"
                    
                elif cmd_type == "sleep":
                    duration = command["duration"]
                    return f"sleep({duration})"
                    
                elif cmd_type == "gripper":
                    action = command["action"]
                    if action == "open":
                        return "set_tool_digital_out(0, False)
set_tool_digital_out(1, True)"
                    elif action == "close":
                        return "set_tool_digital_out(0, True)
set_tool_digital_out(1, False)"
            
            # Handle old format (x, y, z, rx, ry, rz) - same as original system
            elif all(key in command for key in ['x', 'y', 'z', 'rx', 'ry', 'rz']):
                x, y, z, rx, ry, rz = command['x'], command['y'], command['z'], command['rx'], command['ry'], command['rz']
                speed = command.get('speed', 0.1)
                
                # Use the exact same format as the original working system
                script = f"movel(p[{x}, {y}, {z}, {rx}, {ry}, {rz}], {speed:.3f}, 0.5)"
                
                # Handle gripper if present
                if 'gripper' in command:
                    gripper_state = command['gripper']
                    if gripper_state == 1:  # Close
                        script += "
set_tool_digital_out(0, True)
set_tool_digital_out(1, False)"
                    else:  # Open
                        script += "
set_tool_digital_out(0, False)
set_tool_digital_out(1, True)"
                
                return script
                    
            return None
        except Exception as e:
            print(f"❌ Error building URScript: {e}")
            return None
                    elif action == "close":
                        return "set_tool_digital_out(0, True)\nset_tool_digital_out(1, False)"
            
            # Handle old format with direct coordinates (backward compatibility)
            elif "x" in command and "y" in command and "z" in command:
                x = command["x"]
                y = command["y"] 
                z = command["z"]
                rx = command.get("rx", 0)
                ry = command.get("ry", 0)
                rz = command.get("rz", 0)
                speed = command.get("speed", 0.1)
                
                pose_script = f"movel(p[{x}, {y}, {z}, {rx}, {ry}, {rz}], v={speed}, a=0.3)"
                
                # Handle gripper if present
                if "gripper" in command:
                    gripper_value = command["gripper"]
                    if gripper_value == 1:  # Close gripper
                        gripper_script = "set_tool_digital_out(0, True)\nset_tool_digital_out(1, False)"
                    else:  # Open gripper
                        gripper_script = "set_tool_digital_out(0, False)\nset_tool_digital_out(1, True)"
                    return f"{pose_script}\nsleep(0.5)\n{gripper_script}"
                
                return pose_script
                    
            return None
        except Exception as e:
            print(f"❌ Error building URScript: {e}")
            return None
    
    def start_interactive_mode(self):
        """Start interactive terminal control"""
        self.running = True
        self.start_time = time.time()
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self.worker_function, daemon=True)
        self.worker_thread.start()
        
        # Start external monitor thread
        self.external_monitor_thread = threading.Thread(target=self._monitor_external_commands, daemon=True)
        self.external_monitor_thread.start()
        
        print("\\n🚀 Unified Robot Control System Started")
        print("=" * 60)
        print("UR ROBOT COMMANDS:")
        print("  add <function> [speed] [pause_mir] - Add UR function to queue")
        print("  list                              - List available UR functions")
        print("  speed <value>                     - Set UR base speed (0.01-1.0)")
        print("  multiplier <value>                - Set UR speed multiplier (0.1-5.0)")
        print("  slow / fast                       - Halve/double current speed")
        print()
        print("MIR BASE COMMANDS:")
        print("  mir pause / mir resume            - Control MIR base")
        print("  mir status                        - Show MIR status")
        print("  mir auto <true/false>             - Enable/disable auto-pause")
        print()
        print("SYSTEM COMMANDS:")
        print("  pause / resume                    - Control entire system")
        print("  status                            - Show system status")
        print("  stop                              - Stop system and clear queues")
        print("  collab <function> [speed]         - Add UR function with MIR pause")
        print("  quit                              - Exit program")
        print("=" * 60)
        
        try:
            while self.running:
                try:
                    user_input = input("\\n🤖 unified> ").strip()
                    if not user_input:
                        continue
                        
                    parts = user_input.split()
                    command = parts[0].lower()
                    
                    if command == "quit":
                        break
                    elif command == "add" and len(parts) > 1:
                        function_name = parts[1]
                        speed = float(parts[2]) if len(parts) > 2 else None
                        pause_mir = parts[3].lower() == "true" if len(parts) > 3 else None
                        self.add_ur_function(function_name, speed, pause_mir)
                    elif command == "collab" and len(parts) > 1:
                        function_name = parts[1]
                        speed = float(parts[2]) if len(parts) > 2 else None
                        self.add_ur_function(function_name, speed, pause_mir=True)
                    elif command == "list":
                        functions = self.list_ur_functions()
                        print(f"\\n📁 Available UR functions ({len(functions)}):")
                        for func in sorted(functions):
                            print(f"   • {func}")
                    elif command == "pause":
                        self.pause()
                    elif command == "resume":
                        self.resume()
                    elif command == "stop":
                        self.stop()
                    elif command == "status":
                        self.get_status()
                    elif command == "speed" and len(parts) > 1:
                        speed = float(parts[1])
                        self.set_speed(speed)
                    elif command == "multiplier" and len(parts) > 1:
                        multiplier = float(parts[1])
                        self.set_speed_multiplier(multiplier)
                    elif command == "slow":
                        new_multiplier = max(0.1, self.speed_multiplier * 0.5)
                        self.set_speed_multiplier(new_multiplier)
                    elif command == "fast":
                        new_multiplier = min(5.0, self.speed_multiplier * 2.0)
                        self.set_speed_multiplier(new_multiplier)
                    elif command == "mir":
                        if len(parts) > 1:
                            mir_cmd = parts[1].lower()
                            if mir_cmd == "pause":
                                self.mir_pause()
                            elif mir_cmd == "resume":
                                self.mir_resume()
                            elif mir_cmd == "status":
                                self.mir_status()
                            elif mir_cmd == "auto" and len(parts) > 2:
                                enabled = parts[2].lower() == "true"
                                self.set_mir_auto_pause(enabled)
                            else:
                                print("❌ Unknown MIR command. Use: pause, resume, status, auto <true/false>")
                        else:
                            print("❌ MIR command required. Use: pause, resume, status, auto <true/false>")
                    else:
                        print(f"❌ Unknown command: {command}")
                        print("   Use 'status' to see system info or 'quit' to exit")
                        
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"❌ Command error: {e}")
                    
        except KeyboardInterrupt:
            pass
        
        print("\\n🛑 Shutting down unified robot control system...")
        self.stop()


def signal_handler(signum, frame):
    """Handle shutdown signal"""
    print("\\n🛑 Signal received, shutting down...")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="Unified Robot Control System")
    parser.add_argument("--ur-ip", default="192.168.1.6", help="UR robot IP address")
    parser.add_argument("--mir-ip", default="mir.com", help="MIR base IP address")
    parser.add_argument("--functions-dir", default="functions", help="Directory containing UR function files")
    parser.add_argument("--control-dir", default="control", help="Directory for external control interface")
    parser.add_argument("--cli", action="store_true", help="Start in CLI mode for external control")
    
    args = parser.parse_args()
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create controller
    controller = UnifiedRobotController(
        ur_ip=args.ur_ip,
        mir_ip=args.mir_ip,
        functions_dir=args.functions_dir,
        control_dir=args.control_dir
    )
    
    if args.cli:
        # CLI mode for external control
        print("🤖 Unified Robot CLI Mode")
        print("Commands: status, ur_add <function>, mir_pause, mir_resume, pause, resume, stop")
        
        try:
            controller.running = True
            controller.start_time = time.time()
            
            controller.worker_thread = threading.Thread(target=controller.worker_function, daemon=True)
            controller.worker_thread.start()
            
            while True:
                command = input("cli> ").strip()
                if command == "quit":
                    break
                controller._process_external_command(command)
                
        except KeyboardInterrupt:
            pass
        finally:
            controller.stop()
    else:
        # Interactive mode
        controller.start_interactive_mode()


if __name__ == "__main__":
    main()
