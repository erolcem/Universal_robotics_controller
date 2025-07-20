# 🤖 UR Robot Controller

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![RTDE](https://img.shields.io/badge/RTDE-1.6+-green.svg)](https://sdurobotics.gitlab.io/ur_rtde/)

A comprehensive Python library for controlling Universal Robots (UR) arms through Real-Time Data Exchange (RTDE). Supports both simulation environments and physical robots with built-in safety features.

## ✨ Features

- **🎯 Dual Mode Support**: Seamlessly works with UR simulator (URSim) and physical robots
- **🛡️ Safety First**: Built-in safety checks and configurable limits for physical robot operations
- **🎮 Flexible Control**: Position control, velocity control, and real-time streaming
- **📁 Command Streaming**: Execute commands from JSONL files (synchronous/asynchronous modes)
- **⚙️ Configuration Management**: YAML-based configuration for different robot setups
- **🔧 Physical Robot Ready**: Optimized for UR3e, UR5e, UR10e, UR16e, and UR20 models
- **📊 Comprehensive Logging**: Detailed logging for debugging and monitoring
- **🔍 Diagnostic Tools**: Built-in status checking and troubleshooting utilities

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux (Ubuntu 20.04+), Windows 10/11, macOS 10.15+
- **Robot Hardware**: Universal Robots e-Series (UR3e, UR5e, UR10e, UR16e, UR20) or URSim
- **Network**: Ethernet connection to robot (for physical robots)
- **Docker**: Required for simulation mode

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ur-robot-controller.git
cd ur-robot-controller

# Create and activate virtual environment
python3 -m venv ur_venv
source ur_venv/bin/activate  # On Windows: ur_venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Simulation Setup

```bash
# Install Docker Desktop from https://docker.com
# Start the UR simulator
./scripts/startDocker.sh

# Open simulator web interface
# Navigate to: http://localhost:6080/vnc.html

# Configure simulator (one-time setup):
# 1. Click "Confirm Safety Configuration"
# 2. Turn ON "Simulation" (bottom right switch)
# 3. Go to Program → Graphics
# 4. Go to Move → Press "ON" → Press "START"
# 5. Return to Program → Graphics
```

### 3. Run Your First Example

```bash
# Activate virtual environment
source ur_venv/bin/activate

# Test basic functionality
python examples/basic_example.py

# Check robot status
python scripts/check_robot_status.py

# Visual movement test
python scripts/visual_test.py
```

## 📖 Usage Examples

### Basic Robot Control

```python
from src.ur_controller import URRobotController

# Initialize controller
controller = URRobotController(
    robot_ip="127.0.0.1",      # Simulator IP
    robot_type="simulation"     # or "physical"
)

# Connect and control
if controller.connect():
    # Get current position
    pose = controller.get_tcp_pose()
    print(f"Current pose: {pose}")
    
    # Move to new position (relative movement)
    controller.move_linear_relative([0.1, 0, 0], speed=0.1)  # Move 10cm in X
    
    # Move to absolute position
    target = [0.3, -0.3, 0.5, 0.0, 3.14, 0.0]
    controller.move_linear(target, speed=0.1)
    
    # Velocity control
    velocity = [0.05, 0.0, 0.0, 0.0, 0.0, 0.0]  # 5cm/s in X
    controller.move_velocity(velocity, duration=2.0)
    
    controller.disconnect()
```

### Physical Robot Setup

```bash
# Scan for robots on network
python scripts/setup_physical_robot.py --scan

# Test connection to specific robot
python scripts/setup_physical_robot.py --test-ip 192.168.1.100

# Run example with physical robot
python examples/basic_example.py --robot-type physical --robot-ip 192.168.1.100
```

### Command File Execution

Create command files in JSONL format:
```json
{"dx": 0.05, "dy": 0.0, "dz": 0.0}
{"dx": 0.0, "dy": 0.05, "dz": 0.0}
{"dx": 0.0, "dy": 0.0, "dz": 0.05, "drx": 0.1}
```

Execute commands:
```bash
# Synchronous execution (waits for each command to complete)
python examples/synchronous_control.py --json-source examples/synchronous_deltas.jsonl

# Asynchronous execution (continuous streaming)
python examples/asynchronous_control.py --json-file examples/asynchronous_deltas.jsonl
```

### Configuration-Based Control

Create a robot configuration file (`config/my_robot.yaml`):
```yaml
robot:
  type: "physical"
  ip: "192.168.1.100"
  model: "UR10e"
  frequency: 500.0

physical:
  safety:
    max_velocity: 0.5
    max_acceleration: 1.0
    workspace_limits:
      x: [-1.3, 1.3]
      y: [-1.3, 1.3]
      z: [0.0, 1.9]

movement:
  default_speed: 0.1
  default_acceleration: 0.3
```

Use with any script:
```bash
python examples/basic_example.py --config config/my_robot.yaml
```

## 📁 Project Structure

```
ur-robot-controller/
├── 📂 src/
│   └── ur_controller.py              # Main library
├── 📂 examples/
│   ├── basic_example.py              # Basic robot control demo
│   ├── synchronous_control.py        # Sequential command execution
│   ├── asynchronous_control.py       # Streaming command execution
│   ├── synchronous_deltas.jsonl      # Example commands (sync)
│   └── asynchronous_deltas.jsonl     # Example commands (async)
├── 📂 scripts/
│   ├── startDocker.sh                # Start UR simulator
│   ├── setup_physical_robot.py       # Physical robot setup tool
│   ├── check_robot_status.py         # Robot diagnostics
│   └── visual_test.py                # Visual movement verification
├── 📂 config/
│   └── robot_config_template.yaml    # Configuration template
├── 📂 legacy/
│   ├── ur_example.py                 # Original working examples
│   ├── ur_synchronous.py             # Legacy sync control
│   └── ur_asynchronous.py            # Legacy async control
├── 📂 docs/
│   └── Documentation_Arm_simulationv1.pdf
├── requirements.txt                  # Python dependencies
├── setup.py                         # Package setup
├── .gitignore                       # Git ignore rules
├── LICENSE                          # MIT license
└── README.md                        # This file
```

## 🛠️ API Reference

### URRobotController Class

| Method | Description | Parameters |
|--------|-------------|------------|
| `connect()` | Connect to robot | Returns: `bool` |
| `disconnect()` | Disconnect from robot | None |
| `get_tcp_pose()` | Get current TCP position | Returns: `List[float]` |
| `move_linear(pose, speed, acceleration)` | Move to absolute pose | `pose`: target pose, `speed`: m/s, `acceleration`: m/s² |
| `move_linear_relative(delta, speed)` | Move relative to current pose | `delta`: [dx,dy,dz,drx,dry,drz], `speed`: m/s |
| `move_velocity(velocity, duration)` | Apply velocity for duration | `velocity`: [vx,vy,vz,vrx,vry,vrz], `duration`: seconds |
| `stop_movement()` | Emergency stop | None |

### Command File Format

Commands use JSONL format (one JSON object per line):
```json
{"dx": 0.05, "dy": 0.0, "dz": 0.0}                    // Linear movement
{"dx": 0.0, "dy": 0.0, "dz": 0.0, "drx": 0.1}        // Rotational movement
{"dx": 0.02, "dy": 0.02, "dz": 0.01, "dry": 0.05}    // Combined movement
```

- `dx`, `dy`, `dz`: Linear deltas in meters
- `drx`, `dry`, `drz`: Rotational deltas in radians

## 🛡️ Safety Features

### Physical Robot Safety
- ✅ Configurable velocity and acceleration limits
- ✅ Workspace boundary checking
- ✅ Emergency stop functionality
- ✅ Connection verification before movement
- ✅ Conservative default parameters
- ✅ Robot mode and safety status validation

### Simulation Safety
- ✅ Automatic connection validation
- ✅ Error handling and recovery
- ✅ Comprehensive logging
- ✅ Non-destructive testing environment

## 📊 Supported Robot Models

| Model | Payload | Reach | Status | Tested |
|-------|---------|-------|--------|--------|
| UR3e  | 3 kg    | 500 mm | ✅ Supported | ✅ |
| UR5e  | 5 kg    | 850 mm | ✅ Supported | ✅ |
| UR10e | 10 kg   | 1300 mm | ✅ Supported | ✅ |
| UR16e | 16 kg   | 900 mm | ✅ Supported | ⚠️ |
| UR20  | 20 kg   | 1750 mm | ✅ Supported | ⚠️ |

*⚠️ = Supported but not physically tested*

## 🔧 Troubleshooting

### Common Issues

#### Connection Problems
```bash
# Check robot status
python scripts/check_robot_status.py

# Test connection with diagnostic
python scripts/visual_test.py
```

**Solutions:**
- Verify robot IP address and network connectivity
- Check firewall settings (ports 29999, 30004)
- Ensure RTDE is enabled on physical robots
- For simulation: verify Docker container is running

#### Simulation Issues
```bash
# Check Docker status
docker ps | grep ursim

# Restart simulator if needed
./scripts/startDocker.sh
```

**Solutions:**
- Verify Docker Desktop is running
- Check if simulator ports are available (6080, 29999, 30004)
- Ensure VNC interface is accessible at http://localhost:6080/vnc.html
- Complete simulator configuration steps

#### Physical Robot Issues
**Robot not responding:**
- Verify robot is in remote control mode
- Check External Control URCap is installed and configured
- Ensure robot program is running
- Verify safety system status

#### Installation Issues
```bash
# Fix virtual environment issues
rm -rf ur_venv
python3 -m venv ur_venv
source ur_venv/bin/activate
pip install -r requirements.txt
```

### Error Codes

| Error | Cause | Solution |
|-------|-------|----------|
| Connection timeout | Network/IP issues | Check IP and network connectivity |
| RTDE not available | RTDE not enabled | Enable RTDE in robot settings |
| Safety violation | Movement outside limits | Check workspace configuration |
| Robot not ready | Wrong robot mode | Set robot to remote control mode |

## 🧪 Testing

Run the test suite to verify installation:

```bash
# Activate environment
source ur_venv/bin/activate

# Basic connection test
python scripts/check_robot_status.py

# Visual movement test (with simulator open)
python scripts/visual_test.py

# Full functionality test
python examples/basic_example.py
```

## 🚀 Future Development: ROS 2 Integration

This project is designed as the foundation for ROS 2 integration. Planned features:

- 🔄 ROS 2 nodes for robot control
- 🤖 MoveIt integration for motion planning
- 📡 tf2 transforms for coordinate frames
- 📋 Standard ROS 2 interfaces (action servers, services)
- 🚀 Launch files for easy deployment
- 📊 RViz visualization support

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/ur-robot-controller.git
cd ur-robot-controller

# Install development dependencies
pip install -r requirements.txt
# pip install pytest black flake8  # Optional dev tools
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Universal Robots** for the RTDE interface and URSim simulator
- **SDU Robotics** for the excellent `ur_rtde` Python library
- **The UR robotics community** for documentation and examples
- **Contributors** who helped improve this project

## 📞 Support

- 📖 **Documentation**: Check this README and the examples
- 🐛 **Issues**: [Open an issue](https://github.com/yourusername/ur-robot-controller/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/ur-robot-controller/discussions)
- 📧 **Email**: your.email@example.com

## 🏷️ Version History

- **v1.0.0** - Initial release with full simulation and physical robot support
- **v0.9.0** - Beta release with core functionality
- **v0.1.0** - Initial development version

---

<div align="center">

**⭐ Star this repository if it helped you! ⭐**

[🔗 View on GitHub](https://github.com/yourusername/ur-robot-controller) | [📋 Report Bug](https://github.com/yourusername/ur-robot-controller/issues) | [💡 Request Feature](https://github.com/yourusername/ur-robot-controller/issues)

</div>
