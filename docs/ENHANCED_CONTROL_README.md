# Enhanced Robot Control System

A multi-interface robot control system with real-time function queuing, speed control, and external program integration.

## Features

- **Real-time Function Queuing**: Add functions to execution queue while robot is running
- **Speed Control**: Adjustable base speed and dynamic speed multipliers
- **Pause/Resume**: Stop and resume execution at any time
- **Multi-Interface Control**: Terminal commands + external program control
- **External Integration**: Control from other programs via file-based interface
- **Status Monitoring**: Real-time status updates and monitoring

## Quick Start

1. **Start the robot controller:**
```bash
python interactive_robot_control.py
```

2. **Use terminal commands:**
```
add pickup          # Add pickup function to queue
pause              # Pause execution
fast               # Double the speed
resume             # Resume execution
status             # Show current status
```

3. **Control from external program:**
```bash
python robot_cli.py pause        # Pause via CLI
python robot_cli.py speed 0.2    # Set speed via CLI
python external_control_example.py  # Run example external control
```

## Terminal Commands

| Command | Description | Example |
|---------|-------------|---------|
| `help` | Show available commands | `help` |
| `list` | List available functions | `list` |
| `add <func> [speed]` | Add function to queue | `add pickup 0.05` |
| `pause` | Pause execution | `pause` |
| `resume` | Resume execution | `resume` |
| `stop` | Stop and clear queues | `stop` |
| `status` | Show current status | `status` |
| `speed <value>` | Set base speed (0.01-1.0 m/s) | `speed 0.1` |
| `multiplier <val>` | Set speed multiplier (0.1-5.0x) | `multiplier 2.0` |
| `slow` | Halve current speed | `slow` |
| `fast` | Double current speed | `fast` |
| `quit` | Exit program | `quit` |

## External Control Interface

### File-based Control
The system creates a `control/` directory with these files:

- **`robot_commands.txt`**: Write commands here for external control
- **`robot_status.json`**: Read current robot status
- **`robot_response.txt`**: Read responses to external commands

### External Commands
Write any of these commands to `control/robot_commands.txt`:

```
pause                    # Pause execution
resume                   # Resume execution
stop                     # Stop execution
slow                     # Slow down (halve speed)
fast                     # Speed up (double speed)
speed 0.15              # Set base speed
multiplier 1.5          # Set speed multiplier
add pickup 0.05         # Add function with specific speed
add home                # Add function with default speed
status                  # Get status update
```

### Command Line Interface
Use `robot_cli.py` for quick external commands:

```bash
python robot_cli.py status              # Show status
python robot_cli.py pause               # Pause robot
python robot_cli.py add pickup 0.05     # Add function
python robot_cli.py fast                # Speed up
python robot_cli.py speed 0.2           # Set speed
```

### External Program Integration
See `external_control_example.py` for a complete example of controlling the robot from another Python program.

## Function Files

Create function files in the `functions/` directory as JSONL files:

**Example: `functions/pickup.jsonl`**
```json
{"x": 0.3, "y": 0.2, "z": 0.3, "rx": 3.14, "ry": 0, "rz": 0}
{"x": 0.3, "y": 0.2, "z": 0.25, "rx": 3.14, "ry": 0, "rz": 0}
{"x": 0.3, "y": 0.2, "z": 0.25, "rx": 3.14, "ry": 0, "rz": 0, "gripper": 1}
{"x": 0.3, "y": 0.2, "z": 0.3, "rx": 3.14, "ry": 0, "rz": 0}
{"x": 0.2, "y": 0.3, "z": 0.4, "rx": 3.14, "ry": 0, "rz": 0}
```

## Speed Control

The system uses a two-level speed control:

1. **Base Speed**: The fundamental movement speed (0.01-1.0 m/s)
2. **Speed Multiplier**: Dynamic multiplier applied to base speed (0.1-5.0x)

**Effective Speed = Base Speed × Speed Multiplier**

This allows you to:
- Set a base speed for each function
- Dynamically slow down or speed up during execution
- Quickly return to normal speed by resetting multiplier to 1.0

## Status Monitoring

The system provides real-time status in multiple formats:

### Terminal Status
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

## Architecture

- **Main Thread**: User interface and coordination
- **Worker Thread**: Robot command execution
- **Input Thread**: Terminal command processing  
- **Monitor Thread**: External command file monitoring
- **Queue System**: Thread-safe function and command queuing
- **Socket Communication**: Direct URScript commands to robot

## Safety Features

- **Graceful Shutdown**: Ctrl+C handling and proper thread cleanup
- **Queue Management**: Automatic queue clearing on stop command
- **Error Handling**: Robust error handling for network and file operations
- **Speed Limits**: Enforced speed ranges for safety
- **Pause Capability**: Immediate pause/resume without losing queue state

## Use Cases

1. **Interactive Development**: Test and refine robot functions in real-time
2. **Production Automation**: Queue multiple functions for continuous operation
3. **External Integration**: Control robot from other applications or scripts
4. **Speed Optimization**: Dynamically adjust speeds for different operations
5. **Emergency Control**: Quick pause/stop capabilities for safety
6. **Monitoring**: Real-time status monitoring for supervisory systems
