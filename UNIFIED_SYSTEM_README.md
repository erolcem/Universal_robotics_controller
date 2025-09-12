# Unified Robot Control System

**Stage 2: Integrated UR Robot Arm + MIR Base Control**

A comprehensive control system that unifies UR robot arm operations with MIR base coordination for collaborative robotics workflows.

## 🌟 **Key Features**

### UR Robot Control
- **Real-time function queuing** - Add functions while others execute
- **Interactive terminal control** - Live command interface
- **Speed control & multipliers** - Dynamic speed adjustment
- **Pause/resume functionality** - Mid-execution control
- **External program interface** - CLI and file-based control
- **12 comprehensive test functions** - Complete movement library

### MIR Base Integration  
- **Automatic coordination** - MIR pauses during UR operations
- **Manual MIR control** - Independent pause/resume commands
- **Status monitoring** - Position, battery, state tracking
- **Collaborative workflows** - Synchronized multi-robot operations
- **Non-invasive integration** - Preserves existing MIR missions

### Unified Control
- **Single interface** - Control both robots from one terminal
- **Collaborative functions** - UR functions with automatic MIR pause
- **External CLI tool** - Command-line access for integration
- **Status monitoring** - Real-time system state tracking
- **Error handling** - Graceful degradation if MIR unavailable

## 🚀 **Quick Start**

### 1. Start the Unified Control System
```bash
python unified_robot_control.py --ur-ip 192.168.1.6 --mir-ip mir.com
```

### 2. Basic Commands
```
🤖 unified> status              # Show system status
🤖 unified> list                # List available UR functions  
🤖 unified> add home            # Add UR function (no MIR pause)
🤖 unified> collab pickup       # Add UR function with MIR pause
🤖 unified> mir pause           # Manually pause MIR
🤖 unified> mir resume          # Manually resume MIR
🤖 unified> pause               # Pause entire system
🤖 unified> resume              # Resume entire system
```

### 3. External CLI Tool
```bash
# UR robot control
python unified_robot_cli.py ur --add pickup --pause-mir
python unified_robot_cli.py ur --speed 0.2

# MIR base control  
python unified_robot_cli.py mir --pause
python unified_robot_cli.py mir --resume

# System control
python unified_robot_cli.py system --status
python unified_robot_cli.py system --pause

# Collaborative operations
python unified_robot_cli.py collab pickup --speed 0.15
```

## 📁 **System Architecture**

```
unified_robot_control.py     # Main unified control system
unified_robot_cli.py         # External CLI tool
functions/                   # UR robot function library
├── home.jsonl              # Return to home position
├── pickup.jsonl            # Pickup operation
├── dropoff.jsonl           # Dropoff operation  
├── square.jsonl            # Square movement pattern
├── circle.jsonl            # Circular movement pattern
├── pick_and_place.jsonl    # Complete pick/place sequence
└── ... (12 total functions)
control/                     # External control interface
├── robot_commands.txt      # Command input file
├── robot_status.json       # Real-time status
└── robot_response.txt      # Command responses
YW_MiR/                     # MIR control modules
├── simple_mir_control.py   # Simple MIR pause/resume
├── mir_api_control.py      # Advanced MIR API control
└── requirements.txt        # MIR dependencies
```

## 🤖 **Available UR Functions**

| Function | Description | Use Case |
|----------|-------------|----------|
| `home` | Return to home position | Reset/initialization |
| `pickup` | Pickup operation with gripper | Object collection |
| `dropoff` | Dropoff operation with gripper | Object placement |
| `square` | Square movement pattern | Path testing |
| `circle` | Circular movement pattern | Smooth motion testing |
| `rectangle` | Rectangle movement pattern | Area coverage |
| `diamond` | Diamond movement pattern | Precision testing |
| `cube_outline` | 3D cube outline | 3D space testing |
| `pick_and_place` | Complete sequence | Full operation test |
| `diagonal_transfer` | Diagonal movement | Complex path testing |
| `vertical_line` | Vertical movement | Z-axis testing |
| `z_oscillate` | Z-axis oscillation | Vibration/precision |

## 🚁 **MIR Base Features**

### Automatic Coordination
- **Auto-pause during UR operations** - Prevents collisions
- **Configurable behavior** - Enable/disable per function
- **Safety-first design** - MIR stops when uncertain

### Manual Control
- **Independent operation** - Control MIR without affecting UR
- **Status monitoring** - Position, battery, state tracking
- **Error handling** - Graceful fallback if MIR unavailable

### Integration Options
```python
# Auto-pause enabled (default for collaborative functions)
collab pickup

# Manual MIR control
add pickup false    # UR function without MIR pause
mir pause          # Manual MIR pause
mir resume         # Manual MIR resume

# Configure auto-pause behavior
mir auto true      # Enable auto-pause (default)
mir auto false     # Disable auto-pause
```

## 🛠️ **Installation & Setup**

### Prerequisites
```bash
# UR robot at 192.168.1.6 (or specified IP)
# MIR base accessible at mir.com (or specified IP)
# Python 3.7+ with required packages
```

### Install Dependencies
```bash
# Install MIR control dependencies
cd YW_MiR
pip install -r requirements.txt

# Return to main directory  
cd ..
```

### Network Configuration
```bash
# Verify UR robot connection
ping 192.168.1.6

# Verify MIR base connection  
ping mir.com
```

### Test Installation
```bash
# Test UR robot connection
python unified_robot_control.py --ur-ip 192.168.1.6 --mir-ip offline

# Test MIR connection (if available)
python unified_robot_control.py --ur-ip offline --mir-ip mir.com

# Test unified system
python unified_robot_control.py
```

## 🔧 **Configuration Options**

### Command Line Arguments
```bash
python unified_robot_control.py --help

Options:
  --ur-ip IP          UR robot IP address (default: 192.168.1.6)
  --mir-ip IP         MIR base IP address (default: mir.com)  
  --functions-dir DIR Directory for UR functions (default: functions)
  --control-dir DIR   Directory for external control (default: control)
  --cli               Start in CLI mode for external control
```

### Runtime Configuration
```
# UR speed control
speed 0.2              # Set base speed to 0.2 m/s
multiplier 1.5         # Set speed multiplier to 1.5x
slow                   # Halve current speed
fast                   # Double current speed

# MIR coordination
mir auto true          # Enable auto-pause during UR functions
mir auto false         # Disable auto-pause (manual control only)
```

## 📊 **Status Monitoring**

### System Status Display
```
📊 Unified Robot System Status:
   System Running: ✅
   System Paused: ▶️
   Uptime: 125.3s

🤖 UR Robot Arm:
   IP: 192.168.1.6
   Base Speed: 0.1 m/s
   Speed Multiplier: 1.0x
   Effective Speed: 0.100 m/s
   Functions Executed: 5
   Commands Executed: 47
   Queue Size: 2

🚁 MIR Base:
   IP: mir.com
   Enabled: ✅
   Auto-pause: ✅
   Operations: 12
   Position: x=1.25, y=0.43, θ=45.2°
   Battery: 87.3%
   Ready: ✅
   Paused: ▶️
```

### External Status File
Real-time JSON status available at `control/robot_status.json`:
```json
{
  "systems": {
    "ur_robot": {
      "running": true,
      "paused": false,
      "current_speed": 0.1,
      "functions_executed": 5,
      "queue_size": 2
    },
    "mir_base": {
      "enabled": true,
      "auto_pause": true,
      "position": {"x": 1.25, "y": 0.43, "orientation": 45.2},
      "battery": 87.3,
      "ready": true,
      "paused": false
    }
  },
  "timestamp": 1703123456.789,
  "uptime": 125.3
}
```

## 🔄 **Workflow Examples**

### Basic Collaborative Sequence
```bash
# Start system
python unified_robot_control.py

# Execute collaborative pickup (MIR auto-pauses)
🤖 unified> collab pickup

# Manual coordination
🤖 unified> mir pause      # Stop MIR
🤖 unified> add dropoff    # UR operation without auto-pause
🤖 unified> mir resume     # Resume MIR

# Complex sequence
🤖 unified> collab pickup 0.15       # Slow pickup with MIR pause
🤖 unified> add square 0.2           # Fast pattern without MIR pause  
🤖 unified> collab dropoff 0.1       # Slow dropoff with MIR pause
```

### External Program Integration
```python
#!/usr/bin/env python3
"""Example external program using the unified robot system"""

import subprocess
import time

def collaborative_assembly():
    # Start pickup operation
    subprocess.run(["python", "unified_robot_cli.py", "collab", "pickup"])
    
    # Wait for completion (monitor status file)
    while True:
        result = subprocess.run(["python", "unified_robot_cli.py", "system", "--status", "--wait"], 
                              capture_output=True, text=True)
        if "Queue Size: 0" in result.stdout:
            break
        time.sleep(1)
    
    # Continue with next operation
    subprocess.run(["python", "unified_robot_cli.py", "ur", "--add", "square"])

if __name__ == "__main__":
    collaborative_assembly()
```

### File-Based Control
```bash
# Write commands to control file
echo "collab pickup 0.15" > control/robot_commands.txt
echo "mir status" >> control/robot_commands.txt
echo "system status" >> control/robot_commands.txt

# Commands are automatically executed
# Responses appear in control/robot_response.txt
```

## 🛡️ **Safety Features**

### UR Robot Safety
- **Speed limits** - 0.01 to 1.0 m/s base speed
- **Graceful degradation** - Continue without MIR if unavailable
- **Emergency stop** - System-wide stop command
- **Queue clearing** - Stop and clear all pending operations

### MIR Base Safety  
- **Auto-pause default** - Collaborative functions pause MIR by default
- **Manual override** - Always possible to manually pause/resume
- **Battery monitoring** - Low battery warnings
- **Connection monitoring** - Graceful handling of MIR disconnection

### System Safety
- **Concurrent control prevention** - Single control interface
- **State synchronization** - Consistent system state tracking
- **Error recovery** - Automatic recovery from communication errors
- **Controlled shutdown** - Proper cleanup on exit

## 🚨 **Troubleshooting**

### UR Robot Issues
```bash
# Test UR connection
python unified_robot_control.py --mir-ip offline

# Check if Remote Control is enabled on UR pendant
# Toggle Remote Control OFF then ON if robot doesn't move

# Verify network connection
ping 192.168.1.6
```

### MIR Base Issues  
```bash
# Test MIR connection
python unified_robot_control.py --ur-ip offline

# Check MIR status from web interface
# Verify API is enabled on MIR

# Test basic connectivity
ping mir.com
```

### System Issues
```bash
# Start in debug mode
python unified_robot_control.py --cli

# Check control files
cat control/robot_status.json
cat control/robot_response.txt

# Reset system
rm -rf control/*
python unified_robot_control.py
```

### Common Error Solutions

| Error | Solution |
|-------|----------|
| "MIR not enabled" | Check MIR IP address and network connectivity |
| "UR Socket error" | Verify UR robot IP and enable Remote Control |
| "Function not found" | Check function file exists in functions/ directory |
| "Import could not be resolved" | Install MIR dependencies: `pip install requests` |
| "Connection timeout" | Check network connectivity and robot availability |

## 🔮 **Future Enhancements**

### Planned Features
- **Vision integration** - Camera-based coordination
- **Advanced path planning** - Multi-robot path optimization  
- **Web interface** - Browser-based control dashboard
- **ROS integration** - ROS topic/service interface
- **Database logging** - Operation history and analytics

### Extensibility
- **Plugin system** - Custom function modules
- **API expansion** - REST API for external integration
- **Multi-robot support** - Support for additional robot types
- **Cloud integration** - Remote monitoring and control

## 📞 **Support**

For technical support or feature requests:
1. Check troubleshooting section above
2. Review error messages in `control/robot_response.txt`
3. Test individual components (UR only, MIR only)
4. Verify network connectivity and robot accessibility

## 📋 **Version History**

- **v2.0** - Unified UR + MIR control system
- **v1.5** - Enhanced interactive UR control with external CLI
- **v1.0** - Basic interactive UR robot control system

---

**🤖 Ready for collaborative robotics! The unified system provides seamless coordination between UR robot arm operations and MIR base movement for efficient, safe, and flexible automated workflows.**
