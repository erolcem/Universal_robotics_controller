# UR Robot Pipeline - Enhanced Interactive Control System

A comprehensive, multi-interface robot control system for Universal Robots (UR10e) with real-time function queuing, dynamic speed control, and external program integration.

## 🚀 Quick Start

1. **Activate the virtual environment:**
   ```bash
   source ur_venv/bin/activate
   ```

2. **Start the robot control system:**
   ```bash
   python interactive_robot_control.py
   ```

3. **Start controlling the robot:**
   ```
   list                    # See available functions
   add home               # Add home function to queue
   add pickup 0.05        # Add pickup with slow speed
   fast                   # Double the speed
   pause                  # Pause execution
   resume                 # Resume execution
   ```

## 📁 Project Structure

```
ursim_pipeline/
├── interactive_robot_control.py    # Main control system
├── robot_cli.py                    # External command-line interface
├── external_control_example.py     # Example external control program
├── functions/                      # Robot function definitions
│   ├── home.jsonl                 # Return to home position
│   ├── pickup.jsonl               # Pickup sequence with gripper
│   ├── dropoff.jsonl              # Dropoff sequence
│   ├── square.jsonl               # Square movement pattern
│   ├── rectangle.jsonl            # Rectangle movement
│   ├── circle.jsonl               # Circular movement (16 points)
│   ├── diamond.jsonl              # Diamond shape
│   ├── cube_outline.jsonl         # 3D cube outline
│   ├── pick_and_place.jsonl       # Complete pick and place
│   ├── diagonal_transfer.jsonl    # Diagonal movement with gripper
│   ├── vertical_line.jsonl        # Vertical line movement
│   └── z_oscillate.jsonl          # Z-axis oscillation
├── control/                       # External control interface
│   ├── robot_commands.txt         # Write commands here for external control
│   ├── robot_status.json          # Real-time robot status
│   └── robot_response.txt         # Responses to external commands
├── config/                        # Robot configuration files
├── scripts/                       # Utility scripts
├── examples/                      # Example files and archived versions
├── docs/                          # Documentation
└── archive/                       # Archived unused files
    ├── unused_jsonl/              # Old delta and pose files
    └── unused_scripts/            # Old control scripts
```

## 🎮 Control Interfaces

### 1. Terminal Interface (Interactive Mode)
Use these commands directly in the main terminal when `interactive_robot_control.py` is running:

| Command | Description | Example |
|---------|-------------|---------|
| `help`, `h` | Show available commands | `help` |
| `list`, `l` | List available functions | `list` |
| `add <func> [speed]` | Add function to queue | `add pickup 0.05` |
| `pause`, `p` | Pause execution | `pause` |
| `resume`, `r` | Resume execution | `resume` |
| `stop`, `s` | Stop and clear queues | `stop` |
| `status` | Show current status | `status` |
| `speed <value>` | Set base speed (0.01-1.0 m/s) | `speed 0.1` |
| `multiplier <val>` | Set speed multiplier (0.1-5.0x) | `multiplier 2.0` |
| `slow` | Halve current speed multiplier | `slow` |
| `fast` | Double current speed multiplier | `fast` |
| `quit`, `exit`, `q` | Exit program | `quit` |

### 2. External Command-Line Interface
Control the robot from separate terminal windows or scripts:

```bash
# Quick status check
python robot_cli.py status

# Control commands
python robot_cli.py pause
python robot_cli.py resume
python robot_cli.py add circle 0.08
python robot_cli.py fast
python robot_cli.py speed 0.15

# Get help
python robot_cli.py help
```

### 3. File-Based External Control
Write commands to `control/robot_commands.txt` for external program control:

```bash
# Single command
echo "pause" > control/robot_commands.txt

# Multiple commands
cat << EOF > control/robot_commands.txt
fast
add circle
slow
pause
EOF
```

### 4. External Program Integration
Use the provided example as a template for your own programs:

```bash
python external_control_example.py
```

## 🎯 Available Functions

The system includes comprehensive test functions in the `functions/` directory:

### Basic Functions
- **`home`**: Return to safe home position
- **`pickup`**: Pickup sequence with gripper control (5 commands)
- **`dropoff`**: Dropoff sequence with gripper control (5 commands)

### Geometric Patterns
- **`square`**: Square movement pattern (5 commands)
- **`rectangle`**: Rectangular movement (5 commands)
- **`circle`**: Smooth circular movement (17 points)
- **`diamond`**: Diamond shape pattern (5 commands)
- **`cube_outline`**: 3D cube outline (9 commands)

### Advanced Functions
- **`pick_and_place`**: Complete pick and place operation (6 commands)
- **`diagonal_transfer`**: Diagonal movement with gripper (8 commands)
- **`vertical_line`**: Vertical line movement (3 commands)
- **`z_oscillate`**: Z-axis oscillation pattern (13 commands)

## ⚡ Speed Control System

The system uses a two-level speed control mechanism:

### Base Speed
- Set with `speed <value>` command
- Range: 0.01 - 1.0 m/s
- Applied when functions are added to queue
- Each function can have its own base speed

### Speed Multiplier
- Set with `multiplier <value>` or `slow`/`fast` commands
- Range: 0.1 - 5.0x
- Applied dynamically during execution
- Affects all commands in real-time

### Effective Speed Formula
```
Effective Speed = Base Speed × Speed Multiplier
```

### Examples
```bash
# Set base speed to 0.1 m/s
speed 0.1

# Add function with custom speed
add pickup 0.05           # Pickup at 0.05 m/s base speed

# Double the speed multiplier (affects all current and future commands)
fast                      # Multiplier: 2.0x

# Effective speeds:
# - pickup function: 0.05 × 2.0 = 0.10 m/s
# - new functions: 0.1 × 2.0 = 0.20 m/s

# Slow down by half
slow                      # Multiplier: 1.0x (back to normal)
```

## 📊 Status Monitoring

### Terminal Status Display
```
📊 Robot Controller Status:
   Running: ✅
   Paused: ▶️
   Base Speed: 0.1 m/s
   Speed Multiplier: 2.0x
   Effective Speed: 0.200 m/s
   Functions Executed: 5
   Commands Executed: 25
   Queue Size: 2
   Uptime: 120.5s
   Robot IP: 192.168.1.6
```

### JSON Status File (`control/robot_status.json`)
```json
{
  "running": true,
  "paused": false,
  "current_speed": 0.1,
  "speed_multiplier": 2.0,
  "effective_speed": 0.2,
  "functions_executed": 5,
  "commands_executed": 25,
  "queue_size": 2,
  "uptime": 120.5,
  "timestamp": 1693564800.123
}
```

## 🔧 Creating Custom Functions

Functions are defined as JSONL (JSON Lines) files in the `functions/` directory. Each line represents a robot command.

### Basic Position Command
```json
{"x": 0.3, "y": -0.5, "z": 0.8, "rx": 3.14, "ry": 0, "rz": 0}
```

### Position with Gripper Control
```json
{"x": 0.3, "y": -0.5, "z": 0.7, "rx": 3.14, "ry": 0, "rz": 0, "gripper": 1}
```

### Complete Function Example (`functions/my_function.jsonl`)
```json
{"x": 0.0, "y": -0.6, "z": 0.9, "rx": 3.14, "ry": 0, "rz": 0}
{"x": 0.0, "y": -0.6, "z": 0.7, "rx": 3.14, "ry": 0, "rz": 0, "gripper": 1}
{"x": 0.2, "y": -0.4, "z": 0.7, "rx": 3.14, "ry": 0, "rz": 0}
{"x": 0.2, "y": -0.4, "z": 0.9, "rx": 3.14, "ry": 0, "rz": 0, "gripper": 0}
```

### Coordinate System
- **x**: Left/Right (positive = right)
- **y**: Forward/Backward (negative = toward robot base)
- **z**: Up/Down (positive = up)
- **rx, ry, rz**: Rotation around X, Y, Z axes (radians)
- **gripper**: 1 = close, 0 = open (optional)

## 🛡️ Safety Features

### Speed Limits
- Base speed: 0.01 - 1.0 m/s (enforced)
- Speed multiplier: 0.1 - 5.0x (enforced)
- Maximum effective speed: 5.0 m/s (theoretical)

### Emergency Controls
- **Pause**: Immediate pause without losing queue state
- **Stop**: Immediate stop with queue clearing
- **Graceful Shutdown**: Ctrl+C handling with proper cleanup

### Error Handling
- Network disconnection recovery
- Invalid command handling
- File operation error recovery
- Thread-safe queue operations

## 🔄 Workflow Examples

### Example 1: Basic Operation
```bash
# Start system
python interactive_robot_control.py

# Terminal commands:
list                    # See available functions
add home               # Go home first
add pickup 0.03        # Slow pickup
add square             # Move in square
add dropoff 0.03       # Slow dropoff
status                 # Check progress
```

### Example 2: Speed Control During Execution
```bash
# Start with functions
add circle
add rectangle

# While executing:
fast                   # Speed up current operations
add diamond           # Add more work
slow                  # Slow down
pause                 # Take a break
resume                # Continue
```

### Example 3: External Control
```bash
# Terminal 1: Start main system
python interactive_robot_control.py

# Terminal 2: External control
python robot_cli.py add home
python robot_cli.py fast
python robot_cli.py add circle 0.15
python robot_cli.py status
```

### Example 4: File-Based Control
```bash
# Create control script
cat << EOF > control/robot_commands.txt
add home
fast
add pickup
add square
slow
add dropoff
EOF

# Commands will be executed automatically
```

## 🔌 Robot Configuration

### Network Setup
- **Robot IP**: 192.168.1.6 (configurable)
- **Port**: 30002 (URScript socket)
- **Protocol**: TCP socket communication

### Hardware Requirements
- Universal Robots UR10e (or compatible)
- Tool Digital Output for gripper control
- Network connection to robot controller

### Software Dependencies
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Key packages:
# - ur_rtde (Real-Time Data Exchange)
# - threading, queue (built-in)
# - socket, json (built-in)
```

## 🐛 Troubleshooting

### Common Issues

#### Robot Not Responding
```bash
# Check connection
python scripts/quick_diagnostic.py

# Verify robot status
python robot_cli.py status
```

#### Robot Acknowledges Commands But Doesn't Move
**Most Common Cause: Concurrent Control System Conflict**

**Symptoms:**
- Commands are sent successfully
- Robot status shows normal operation
- No visible movement occurs

**Solution:**
1. **Check for ROS2/other robot drivers:**
   ```bash
   # Check for ROS2 processes
   ps aux | grep ros
   
   # Check for other UR connections
   netstat -an | grep 30002
   ```

2. **Reset robot control handshake:**
   - On teach pendant: Go to **Settings → Remote Control**
   - Toggle **Remote Control OFF** then **ON**
   - This clears all connection conflicts

3. **Ensure exclusive access:**
   - Stop all ROS2 nodes: `ros2 daemon stop`
   - Close other robot control software
   - Only run ONE robot control system at a time

**Prevention:** Always cleanly disconnect from one control system before starting another.

#### Commands Not Executing
1. Check if robot is paused: `status`
2. Verify queue has functions: `list`
3. Check network connection
4. Ensure robot is in proper mode (not emergency stop)

#### External Control Not Working
1. Check if main system is running
2. Verify control directory exists: `ls control/`
3. Check file permissions
4. Monitor response file: `tail -f control/robot_response.txt`

### Debug Mode
Enable verbose output by editing the main script and setting debug flags.

## 📈 Advanced Usage

### Batch Operations
```bash
# Create batch file
cat << EOF > my_batch.txt
speed 0.08
add home
add pickup
fast
add circle
add rectangle
slow
add dropoff
add home
EOF

# Execute batch
cat my_batch.txt > control/robot_commands.txt
```

### Status Monitoring Script
```python
import json
import time

while True:
    with open('control/robot_status.json', 'r') as f:
        status = json.load(f)
    print(f"Queue: {status['queue_size']}, Speed: {status['effective_speed']:.3f}")
    time.sleep(2)
```

### Custom Integration
Use `external_control_example.py` as a template for building your own control applications.

## 🎯 Best Practices

### Function Design
- Keep functions focused and modular
- Use descriptive function names
- Test functions individually before combining
- Include gripper commands where appropriate

### Speed Management
- Start with slow speeds for testing (0.05 m/s)
- Use function-specific speeds for precision tasks
- Use speed multipliers for dynamic control
- Monitor robot behavior during speed changes

### Queue Management
- Add functions strategically during execution
- Use pause/resume for timing control
- Monitor queue size to avoid overloading
- Clear queues with stop command when needed

### External Control
- Check robot status before sending commands
- Monitor response file for command confirmation
- Use CLI for quick operations
- Use file interface for batch operations

## 🆘 Support

### Documentation
- Check `docs/` directory for additional guides
- Review `examples/` for usage patterns
- Examine function files for coordinate examples

### Configuration
- Robot settings: `config/robot_config.yaml`
- Network settings: Modify IP in main script
- Speed limits: Adjust in main script constants

### Logging
- Status updates: `control/robot_status.json`
- Command responses: `control/robot_response.txt`
- Terminal output: Real-time in main terminal

---

## 🎉 Ready to Use!

Your enhanced robot control system is now ready for production use. The system provides:

✅ **Real-time Function Queuing** - Add functions while robot is moving  
✅ **Multi-Interface Control** - Terminal, CLI, file, and program interfaces  
✅ **Dynamic Speed Control** - Base speeds and real-time multipliers  
✅ **Pause/Resume/Stop** - Full execution control  
✅ **External Integration** - Control from other programs  
✅ **Status Monitoring** - Real-time status and progress tracking  
✅ **Safety Features** - Speed limits, error handling, graceful shutdown  
✅ **Comprehensive Functions** - 12 test functions ready to use  

Start with the basic examples and build your own custom robot control applications!
