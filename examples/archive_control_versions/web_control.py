#!/usr/bin/env python3
"""
Web-Based Interactive Robot Control
Clean separation of control interface and robot output
"""

import json
import time
import socket
import threading
import queue
import argparse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class RobotController:
    """Robot controller backend"""
    
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
        self.last_messages = []
        
        # Worker thread
        self.worker_thread = None
        
        # Ensure functions directory exists
        self.functions_dir.mkdir(exist_ok=True)
    
    def log_message(self, message: str):
        """Add message to log"""
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        self.last_messages.append(full_message)
        
        # Keep only last 20 messages
        if len(self.last_messages) > 20:
            self.last_messages.pop(0)
        
        print(full_message)
    
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
            self.log_message(f"❌ Command failed: {e}")
            return False
    
    def load_function(self, function_name: str) -> list:
        """Load function from JSONL file"""
        function_file = self.functions_dir / f"{function_name}.jsonl"
        
        if not function_file.exists():
            self.log_message(f"❌ Function '{function_name}' not found")
            return []
        
        commands = []
        try:
            with open(function_file, 'r') as f:
                for line in f:
                    if line.strip():
                        commands.append(json.loads(line))
            
            self.log_message(f"📁 Loaded function '{function_name}' ({len(commands)} commands)")
            return commands
            
        except Exception as e:
            self.log_message(f"❌ Error loading function '{function_name}': {e}")
            return []
    
    def queue_function(self, function_name: str, speed: float = 0.2):
        """Queue a function for execution"""
        commands = self.load_function(function_name)
        if commands:
            self.function_queue.put((function_name, commands, speed))
            self.log_message(f"📥 Queued function '{function_name}' | Queue: {self.function_queue.qsize()}")
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
            "available_functions": self.get_available_functions(),
            "recent_messages": self.last_messages[-10:]  # Last 10 messages
        }
    
    def worker(self):
        """Worker thread"""
        self.log_message("🔄 Robot worker started")
        
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
                    self.log_message(f"🎯 Executing '{function_name}' ({len(commands)} commands)")
                    
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
                    self.log_message(f"✅ Function '{function_name}' completed")
                    
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
                            self.log_message(f"🎯 → [{x:6.3f}, {y:6.3f}, {z:6.3f}]")
                            self.commands_executed += 1
                    
                    elif cmd_type == "gripper":
                        state = data
                        script = f"set_tool_digital_out(0, {bool(state)})"
                        if self.send_urscript(script):
                            action = "closed" if state else "opened"
                            self.log_message(f"🤏 Gripper {action}")
                            self.commands_executed += 1
                    
                    elif cmd_type == "wait":
                        time.sleep(data)
                    
                    self.command_queue.task_done()
                    
                except queue.Empty:
                    pass
                
            except Exception as e:
                self.log_message(f"❌ Worker error: {e}")
                time.sleep(1)
        
        self.log_message("🔄 Robot worker stopped")
    
    def start(self):
        """Start the controller"""
        if self.running:
            return
        
        self.running = True
        self.worker_thread = threading.Thread(target=self.worker, daemon=True)
        self.worker_thread.start()
        self.log_message("✅ Robot controller started")
    
    def stop(self):
        """Stop the controller"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=2)
        self.log_message("✅ Robot controller stopped")

class WebHandler(BaseHTTPRequestHandler):
    """Web interface handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>Robot Control Interface</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f0f0f0; }
        .container { max-width: 1200px; margin: 0 auto; }
        .panel { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .controls { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .status { background: #e8f5e8; }
        .messages { background: #f8f8f8; height: 300px; overflow-y: auto; padding: 10px; border: 1px solid #ddd; }
        button { padding: 10px 20px; margin: 5px; border: none; border-radius: 4px; cursor: pointer; }
        .primary { background: #007bff; color: white; }
        .success { background: #28a745; color: white; }
        .warning { background: #ffc107; color: black; }
        .danger { background: #dc3545; color: white; }
        input, select { padding: 8px; margin: 5px; border: 1px solid #ddd; border-radius: 4px; }
        .function-list { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Interactive Robot Control</h1>
        
        <div class="controls">
            <div class="panel">
                <h3>📋 Status</h3>
                <div id="status" class="status">Loading...</div>
                
                <h3>🎮 Controls</h3>
                <button class="success" onclick="pauseResume()">⏸️ Pause/Resume</button>
                <button class="warning" onclick="clearQueue()">🗑️ Clear Queue</button>
                <button class="danger" onclick="emergencyStop()">🛑 Emergency Stop</button>
                
                <h3>📁 Add Function</h3>
                <select id="functionSelect">
                    <option value="">Select function...</option>
                </select>
                <input type="number" id="speedInput" placeholder="Speed (0.2)" step="0.1" min="0.1" max="2.0" value="0.2">
                <button class="primary" onclick="addFunction()">➕ Add to Queue</button>
            </div>
            
            <div class="panel">
                <h3>📊 Quick Functions</h3>
                <div class="function-list" id="quickFunctions">
                    <!-- Functions will be loaded here -->
                </div>
                
                <h3>📝 Messages</h3>
                <div id="messages" class="messages">
                    <!-- Messages will appear here -->
                </div>
            </div>
        </div>
    </div>

    <script>
        let isPaused = false;
        
        function updateStatus() {
            fetch('/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('status').innerHTML = `
                        <strong>Running:</strong> ${data.running ? '✅' : '❌'}<br>
                        <strong>Paused:</strong> ${data.paused ? '⏸️' : '▶️'}<br>
                        <strong>Current Function:</strong> ${data.current_function || 'None'}<br>
                        <strong>Function Queue:</strong> ${data.function_queue_size}<br>
                        <strong>Command Queue:</strong> ${data.command_queue_size}<br>
                        <strong>Functions Executed:</strong> ${data.functions_executed}<br>
                        <strong>Commands Executed:</strong> ${data.commands_executed}
                    `;
                    
                    // Update function dropdown
                    const select = document.getElementById('functionSelect');
                    select.innerHTML = '<option value="">Select function...</option>';
                    data.available_functions.forEach(f => {
                        select.innerHTML += `<option value="${f}">${f}</option>`;
                    });
                    
                    // Update quick functions
                    const quickDiv = document.getElementById('quickFunctions');
                    quickDiv.innerHTML = '';
                    data.available_functions.forEach(f => {
                        quickDiv.innerHTML += `<button class="primary" onclick="quickAdd('${f}')">${f}</button>`;
                    });
                    
                    // Update messages
                    const messagesDiv = document.getElementById('messages');
                    messagesDiv.innerHTML = data.recent_messages.join('<br>');
                    messagesDiv.scrollTop = messagesDiv.scrollHeight;
                    
                    isPaused = data.paused;
                });
        }
        
        function addFunction() {
            const func = document.getElementById('functionSelect').value;
            const speed = document.getElementById('speedInput').value || 0.2;
            
            if (!func) {
                alert('Please select a function');
                return;
            }
            
            fetch('/add_function', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({function: func, speed: parseFloat(speed)})
            });
        }
        
        function quickAdd(functionName) {
            fetch('/add_function', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({function: functionName, speed: 0.2})
            });
        }
        
        function pauseResume() {
            fetch('/pause_resume', {method: 'POST'});
        }
        
        function clearQueue() {
            if (confirm('Clear all queued functions?')) {
                fetch('/clear_queue', {method: 'POST'});
            }
        }
        
        function emergencyStop() {
            if (confirm('Emergency stop robot?')) {
                fetch('/emergency_stop', {method: 'POST'});
            }
        }
        
        // Update every second
        setInterval(updateStatus, 1000);
        updateStatus();
    </script>
</body>
</html>
            """
            
            self.wfile.write(html.encode())
        
        elif self.path == "/status":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            status = self.server.robot_controller.get_status()
            self.wfile.write(json.dumps(status).encode())
        
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        if self.path == "/add_function":
            data = json.loads(post_data.decode())
            function_name = data.get('function')
            speed = data.get('speed', 0.2)
            
            success = self.server.robot_controller.queue_function(function_name, speed)
            
            self.send_response(200 if success else 400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"success": success}).encode())
        
        elif self.path == "/pause_resume":
            controller = self.server.robot_controller
            controller.paused = not controller.paused
            action = "paused" if controller.paused else "resumed"
            controller.log_message(f"⏸️ Execution {action}")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"paused": controller.paused}).encode())
        
        elif self.path == "/clear_queue":
            controller = self.server.robot_controller
            while not controller.function_queue.empty():
                try:
                    controller.function_queue.get_nowait()
                except:
                    break
            controller.log_message("🗑️ Function queue cleared")
            
            self.send_response(200)
            self.end_headers()
        
        elif self.path == "/emergency_stop":
            controller = self.server.robot_controller
            controller.stop()
            controller.log_message("🛑 Emergency stop activated")
            
            self.send_response(200)
            self.end_headers()

def main():
    parser = argparse.ArgumentParser(description='Web-Based Robot Control')
    parser.add_argument('--ip', default='192.168.1.6', help='Robot IP')
    parser.add_argument('--port', type=int, default=8080, help='Web server port')
    parser.add_argument('--functions-dir', default='functions', help='Functions directory')
    
    args = parser.parse_args()
    
    # Create robot controller
    controller = RobotController(args.ip, args.functions_dir)
    controller.start()
    
    # Create web server
    server = HTTPServer(('localhost', args.port), WebHandler)
    server.robot_controller = controller
    
    print(f"🌐 Web interface: http://localhost:{args.port}")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
        controller.stop()
        server.shutdown()

if __name__ == "__main__":
    main()
