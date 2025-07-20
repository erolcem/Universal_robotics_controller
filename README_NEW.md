# UR Robot Controller

A Python library for controlling Universal Robots (UR) arms through RTDE. Supports both simulation (URSim) and physical robots including UR10e models.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Features

- **Dual Mode Support**: Works with both UR simulator and physical robots
- **Safety First**: Built-in safety checks for physical robot operations
- **Flexible Control**: Supports both position and velocity control
- **Command Streaming**: Execute commands from JSONL files synchronously or asynchronously
- **Configuration Management**: YAML-based configuration for different robot setups
- **Physical Robot Support**: Optimized for UR10e and other UR e-Series robots
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## 📋 Requirements

- Python 3.8+
- Universal Robots e-Series robot or URSim simulator
- Network connection to robot/simulator

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd ursim_pipeline
```

### 2. Setup Python Environment
```bash
# Create virtual environment
python3 -m venv ur_venv
source ur_venv/bin/activate  # On Windows: ur_venv\Scripts\activate

# Install required packages
pip install ur-rtde PyYAML

# Or install all dependencies from requirements.txt (if needed)
# pip install -r requirements.txt
```

### 3. Setup Docker (for simulation)
```bash
# Install Docker Desktop from https://docker.com
# Pull UR simulator image
docker pull universalrobots/ursim_e-series:latest
```

## 🏃‍♂️ Quick Start

### Simulation Mode

1. **Start the simulator**:
```bash
./scripts/startDocker.sh
```

2. **Open simulator interface**: http://localhost:6080/vnc.html

3. **Configure simulator**:
   - Press "Confirm Safety Configuration"
   - Turn ON "Simulation" (bottom right)
   - Go to Program → Graphics
   - Go to Move → Press "ON" → Press "START"
   - Return to Program → Graphics

4. **Run basic example**:
```bash
# Make sure virtual environment is activated
source ur_venv/bin/activate

# Run the example
python examples/basic_example.py
```

### Physical Robot Mode

1. **Setup robot connection**:
```bash
# Make sure virtual environment is activated
source ur_venv/bin/activate

python scripts/setup_physical_robot.py --scan
```

2. **Test connection**:
```bash
python scripts/setup_physical_robot.py --test-ip 192.168.1.100
```

3. **Run with physical robot**:
```bash
python examples/basic_example.py --robot-type physical --robot-ip 192.168.1.100
```

## 📖 Usage Examples

### Basic Robot Control

```python
from src.ur_controller import URRobotController

# Initialize controller
controller = URRobotController(
    robot_ip="127.0.0.1",  # or your robot's IP
    robot_type="simulation"  # or "physical"
)

# Connect to robot
if controller.connect():
    # Get current position
    pose = controller.get_tcp_pose()
    print(f"Current pose: {pose}")
    
    # Move to new position
    target = [0.3, -0.3, 0.5, 0.0, 3.14, 0.0]
    controller.move_linear(target, speed=0.1)
    
    # Apply velocity
    velocity = [0.05, 0.0, 0.0, 0.0, 0.0, 0.0]  # 5cm/s in X
    controller.move_velocity(velocity, duration=2.0)
    
    controller.disconnect()
```

### Command File Execution

**Synchronous mode** (executes commands sequentially):
```bash
# Make sure virtual environment is activated
source ur_venv/bin/activate

python examples/synchronous_control.py --json-source examples/synchronous_deltas.jsonl
```

**Asynchronous mode** (streams latest command continuously):
```bash
# Make sure virtual environment is activated
source ur_venv/bin/activate

python examples/asynchronous_control.py --json-file examples/asynchronous_deltas.jsonl
```

### Configuration File Usage

Create a robot configuration file:
```yaml
robot:
  type: "physical"
  ip: "192.168.1.100"
  model: "UR10e"

physical:
  safety:
    max_velocity: 0.5
    max_acceleration: 1.0
    workspace_limits:
      x: [-1.3, 1.3]
      y: [-1.3, 1.3]
      z: [0.0, 1.9]
```

Use with scripts:
```bash
# Make sure virtual environment is activated
source ur_venv/bin/activate

python examples/basic_example.py --config config/my_robot.yaml
```

## 📁 Project Structure

```
ursim_pipeline/
├── src/
│   └── ur_controller.py          # Main library
├── examples/
│   ├── basic_example.py          # Basic robot control examples
│   ├── synchronous_control.py    # Sequential command execution
│   ├── asynchronous_control.py   # Streaming command execution
│   ├── synchronous_deltas.jsonl  # Example commands (sync)
│   └── asynchronous_deltas.jsonl # Example commands (async)
├── scripts/
│   ├── startDocker.sh            # Start UR simulator
│   └── setup_physical_robot.py   # Physical robot setup tool
├── config/
│   └── robot_config_template.yaml # Configuration template
├── docs/
│   └── Documentation_Arm_simulationv1.pdf
├── requirements.txt              # Python dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🔧 Command File Format

Commands are stored in JSONL (JSON Lines) format. Each line represents a delta movement:

```json
{"dx": 0.05, "dy": 0.0, "dz": 0.0}
{"dx": 0.0, "dy": 0.05, "dz": 0.0}
{"dx": 0.0, "dy": 0.0, "dz": 0.05, "drx": 0.1}
```

- `dx`, `dy`, `dz`: Linear movement deltas (meters)
- `drx`, `dry`, `drz`: Rotational movement deltas (radians)

## 🛡️ Safety Features

### Physical Robot Safety
- Configurable velocity and acceleration limits
- Workspace boundary checking
- Emergency stop functionality
- Connection verification before movement
- Conservative default parameters

### Simulation Safety
- Automatic connection validation
- Error handling and recovery
- Comprehensive logging

## 📊 Supported Robot Models

| Model | Payload | Reach | Status |
|-------|---------|-------|--------|
| UR3e  | 3 kg    | 500 mm | ✅ Supported |
| UR5e  | 5 kg    | 850 mm | ✅ Supported |
| UR10e | 10 kg   | 1300 mm | ✅ Supported |
| UR16e | 16 kg   | 900 mm | ✅ Supported |
| UR20  | 20 kg   | 1750 mm | ✅ Supported |

## 🔍 Troubleshooting

### Connection Issues
- Verify robot IP address and network connectivity
- Check firewall settings (ports 29999, 29998)
- Ensure RTDE is enabled on physical robots

### Simulation Issues
- Verify Docker is running
- Check if simulator ports are available
- Restart Docker container if needed

### Physical Robot Issues
- Verify robot is in remote control mode
- Check safety system status
- Ensure External Control URCap is installed

### Virtual Environment Issues
If you encounter `externally-managed-environment` error:
```bash
# Remove and recreate virtual environment
rm -rf ur_venv
python3 -m venv ur_venv
source ur_venv/bin/activate
pip install ur-rtde PyYAML
```

## 🚀 Future Development: ROS 2 Integration

This project is designed to be the foundation for ROS 2 integration. Future development will include:

- ROS 2 nodes for robot control
- MoveIt integration
- tf2 transforms
- Standard ROS 2 interfaces
- Launch files for easy deployment

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the example scripts
- Open an issue on GitHub

## 🙏 Acknowledgments

- Universal Robots for the RTDE interface and simulator
- The UR robotics community for documentation and examples
