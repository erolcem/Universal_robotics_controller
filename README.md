# UR Robot Controller

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![RTDE](https://img.shields.io/badge/RTDE-1.6+-green.svg)](https://sdurobotics.gitlab.io/ur_rtde/)

A comprehensive Python library for controlling Universal Robots (UR) arms through Real-Time Data Exchange (RTDE). Supports both simulation environments and physical robots with built-in safety features.

![RobotArm](images/ursim_pipeline_1.png)

## Project Function

This library lets you **control Universal Robots** (6-axis robot arms) using Python code. You can:

- **Control robot movements**: Make the robot move to specific positions, follow paths, or apply forces
- **Work with simulation**: Practice and test your code safely using a virtual robot
- **Connect to real robots**: Control actual UR robots in labs
- **Run command sequences**: Execute pre-programmed or streaming movement sequences from files
- **Stay safe**: Built-in safety checks prevent dangerous or impossible movements on robots

## Installation

### 1. System requirements

Please make sure you have the following ready, notably, python and docker.
Which can be found on their respective websites.

- **Python**: 3.8 or higher
- **Operating System**: Linux (Ubuntu 20.04+), Windows 10/11, macOS 10.15+
- **Robot Hardware**: Universal Robots e-Series (UR3e, UR5e, UR10e, UR16e, UR20) if relevant
- **Network**: Ethernet connection to robot (also relevant for physical robots)
- **Docker**: Required for simulation mode

### 2. Environment setup

Simply clone and in the virtual environment, install dependencies, which can be found in requirements.txt

```bash
# Clone the repository
git clone https://github.com/erolcem/Universal_robotics_controller.git
cd Universal_robotics_controller

# Create and activate virtual environment (this example is for linux)
python3 -m venv ur_venv
source ur_venv/bin/activate  # On Windows: ur_venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Complete Guide:

### **Step 1: Basic Concept**

**The robot uses RTDE** Real-Time Data Exchange - it's the communication protocol that lets your computer talk to UR robots. This is the core dependency you'll find in requirements.txt.

**Simulation vs Physical Robot:**
- **Simulation**: RTDE controls the polyscope of the robot arm, which is a 1:1 simulation available anytime. 
- **Physical Robot**: Control real UR robots (but requires actual robot hardware and network connection)

### **Step 2: Start with Simulation (Recommended)**

The simulator lets you test everything safely before touching real robots.

Please make sure all the installation step above is done and the virtual environment is activated.

```bash
# Run this to start the virtual robot (default model 5e)
./scripts/startDocker.sh
```
**What this does**: Both downloads AND starts a virtual UR robot that runs in Docker, can be found in startDocker.sh. The simulated model of the robot can be selected via:

```bash
# OPTIONAL: supported models UR3e, UR5e, UR10e, UR16e, UR20
ROBOT_MODEL="UR10e" ./startDocker.sh
```

```bash
# Open this website to see your virtual robot
# http://localhost:6080/vnc.html
```
**What you'll see**: A web-based interface showing a 3D robot that you can control

**One-time setup in simulator:**
1. Click "Confirm Safety Configuration" (acknowledges you understand robot safety)
2. Turn ON "Simulation" switch (bottom right - enables simulation mode)
3. Go to Move → Press "ON" → Press "START" (starts the robot program)
4. Go to Program → Graphics (shows the robot visually + ensure simulation is still on)

Note: Keep this simulator window open, both website and terminal!

### **Step 3: Test Your Simulation Setup**

Open a **new terminal** (keep simulator terminal running) and test these commands:

```bash
# Activate your Python environment again if not already
source ur_venv/bin/activate

# Test 1/3: Check if robot is ready
python scripts/check_robot_status.py
# In scripts, there are 3 testing files, this is the first of 2 you'll use for simulations.
```
**What this does**: Connects to robot and shows its current status (position, safety mode, etc.) 
and will help to do some preliminary troubleshooting.

```bash
# Test 2/3: Make the robot move visually  
python scripts/visual_test.py
# There is a 3rd testing file, but that is only for physical robots.
```
**What this does**: Moves the robot around slowly so you can see it moving in the simulator web interface. 
refer to output in terminal to see expected movements.

```bash
# Test 3/3: Run full examples
python examples/basic_example.py
# There are 3 example files in total here, all of which are suitable for both sim or physical. 
# Other 2 examples will be explained later.
```
**What this does**: Demonstrates advanced types of robot actions (linear, relative, velocity control, lock)

These 3 tests provide full confirmation of functionality of the simulated robot! 

###  **Step 4: Understanding Physical Robot Connection**

**Requirements for Physical Robots:**
- UR robot (UR3e, UR5e, UR10e, UR16e, or UR20)
- Ethernet cable connecting your computer to the robot
- Robot must be in "Remote Control" mode
- "External Control" URCap installed on robot

**Find your robot on the network:**
```bash
python scripts/setup_physical_robot.py --scan
```
**What this does**: Scans your network to find UR robots and shows their IP addresses

**Test connection to specific robot:**
```bash
python scripts/setup_physical_robot.py --test-ip 192.168.1.100
```
**What this does**: Tests if you can communicate with a robot at that IP address

**Connect to physical robot:**
```bash
python examples/basic_example.py --robot-type physical --robot-ip 192.168.1.100
```
**What this does**: Runs the same examples but on a real robot instead of simulator

## 🔧 **Available Scripts and What They Do**

### 📁 **examples/** - Learn by doing
```bash
# Basic robot control (connects, moves, disconnects)
python examples/basic_example.py
# Shows: connection testing, linear movements, velocity control

# Execute commands from a file, one by one
python examples/synchronous_control.py --json-source examples/synchronous_deltas.jsonl  
# Shows: how to run pre-programmed sequences step-by-step

# Stream commands continuously to robot
python examples/asynchronous_control.py --json-file examples/asynchronous_deltas.jsonl
# Shows: real-time control, continuous movement streaming
```

### 🛠️ **scripts/** - Diagnostic and setup tools
```bash
# Check if robot is working and ready
python scripts/check_robot_status.py
# Shows: connection status, robot mode, safety status, current position

# Visual test - see robot move slowly
python scripts/visual_test.py  
# Shows: slow movements you can watch in simulator interface

# Find physical robots on your network
python scripts/setup_physical_robot.py --scan
# Shows: IP addresses of UR robots found on network

# Test connection to specific robot
python scripts/setup_physical_robot.py --test-ip 192.168.1.100
# Shows: whether you can connect to robot at that IP

# Start the robot simulator
./scripts/startDocker.sh
# Shows: starts virtual robot environment in Docker
```

### 📂 **legacy/** - Original working examples
```bash
# Your original working scripts (preserved for reference)
python legacy/ur_example.py          # Basic UR robot examples
python legacy/ur_synchronous.py      # Sequential command execution  
python legacy/ur_asynchronous.py     # Streaming command execution
```

## 💡 **How to Write Your Own Robot Code**

Instead of starting from scratch, you can use this library in your own Python programs:

```python
# This is example code you can copy and modify
from src.ur_controller import URRobotController

# Connect to robot (simulator or physical)
robot = URRobotController(
    robot_ip="127.0.0.1",        # Use 127.0.0.1 for simulator
    robot_type="simulation"       # Use "physical" for real robots
)

if robot.connect():
    print("Robot connected!")
    
    # Get where robot currently is
    current_position = robot.get_tcp_pose()
    print(f"Robot is at: {current_position}")
    
    # Move robot 10cm to the right
    robot.move_linear_relative([0.1, 0, 0], speed=0.1)
    
    robot.disconnect()
else:
    print("Could not connect to robot")
```

**Why use this approach?** This library handles all the complex communication with the robot, so you can focus on what you want the robot to do, not how to talk to it.

## 📋 **Command Files: Pre-Programming Robot Movements**

You can create files with robot movements and run them later:

**Create a file called `my_movements.jsonl`:**
```json
{"dx": 0.05, "dy": 0.0, "dz": 0.0}
{"dx": 0.0, "dy": 0.05, "dz": 0.0}  
{"dx": 0.0, "dy": 0.0, "dz": 0.05}
```

**Run the movements:**
```bash
python examples/synchronous_control.py --json-source my_movements.jsonl
```

**What each line means:**
- `dx, dy, dz`: Move in X, Y, Z directions (in meters)
- `drx, dry, drz`: Rotate around X, Y, Z axes (in radians)

## ⚙️ **Configuration Files: Save Robot Settings**

Create `my_robot_config.yaml` to save settings:
```yaml
robot:
  type: "physical"           # or "simulation"  
  ip: "192.168.1.100"       # your robot's IP address
  model: "UR10e"            # your robot model

movement:
  default_speed: 0.1        # how fast robot moves (m/s)
  default_acceleration: 0.3 # how quickly it speeds up (m/s²)
```

**Use your config:**
```bash
python examples/basic_example.py --config my_robot_config.yaml
```

## 📁 **Project Files Explained**

### 🔍 **What Each File/Folder Does**

```
ur-robot-controller/
├── 📂 src/
│   └── ur_controller.py              # Main library - the "brain" that talks to robots
├── 📂 examples/                      # Example scripts you can run and learn from
│   ├── basic_example.py              # ➤ python examples/basic_example.py
│   ├── synchronous_control.py        # ➤ python examples/synchronous_control.py --json-source file.jsonl
│   ├── asynchronous_control.py       # ➤ python examples/asynchronous_control.py --json-file file.jsonl
│   ├── synchronous_deltas.jsonl      # Example movement commands (step-by-step)
│   └── asynchronous_deltas.jsonl     # Example movement commands (continuous)
├── 📂 scripts/                       # Utility tools for setup and diagnostics
│   ├── startDocker.sh                # ➤ ./scripts/startDocker.sh (starts simulator)
│   ├── setup_physical_robot.py       # ➤ python scripts/setup_physical_robot.py --scan
│   ├── check_robot_status.py         # ➤ python scripts/check_robot_status.py
│   └── visual_test.py                # ➤ python scripts/visual_test.py
├── 📂 config/
│   └── robot_config_template.yaml    # Template for robot settings (copy and modify)
├── 📂 legacy/                        # Your original working scripts (preserved)
│   ├── ur_example.py                 # ➤ python legacy/ur_example.py
│   ├── ur_synchronous.py             # ➤ python legacy/ur_synchronous.py  
│   └── ur_asynchronous.py            # ➤ python legacy/ur_asynchronous.py
├── 📂 docs/
│   └── Documentation_Arm_simulationv1.pdf  # Visual guide for simulator setup
├── requirements.txt                  # List of Python packages needed
├── setup.py                         # Makes this into a proper Python package
├── .gitignore                       # Tells Git what files to ignore
├── LICENSE                          # MIT license (free to use)
└── README.md                        # This guide you're reading
```

### 🤔 **What is setup.py?**

`setup.py` is a special file that makes this project into a **proper Python package**. Think of it like creating an "installer" for your code.

**What it does:**
- Lets you install this robot controller as a system-wide Python package
- Makes it easy to share your code with others
- Handles dependencies automatically
- Creates command-line tools

**How to use it:**
```bash
# Install this package system-wide (optional)
pip install -e .

# After installing, you can use it from anywhere:
python -c "from src.ur_controller import URRobotController; print('Package installed!')"
```

**Do you need it?** No! You can use everything without running setup.py. It's just for advanced users who want to install the package properly.

## 🤖 **Complete Physical Robot Setup Guide**

### 📋 **Prerequisites**
- UR robot (UR3e, UR5e, UR10e, UR16e, or UR20)
- Ethernet cable
- Computer connected to same network as robot
- Robot powered on and safety configured

### 🔌 **Step 1: Physical Connection**

**Option A: Direct Connection**
1. Connect ethernet cable from your computer directly to robot's ethernet port
2. Set your computer's IP to `192.168.1.XXX` (where XXX is 1-254, but not 100)
3. Robot will typically be at `192.168.1.100`

**Option B: Network Connection**
1. Connect robot to your local network via ethernet
2. Robot will get IP address from your router (check robot's teach pendant for IP)
3. Your computer must be on same network

### 🖥️ **Step 2: Robot Configuration**

**On the robot's teach pendant:**
1. Go to **Settings** → **System** → **Network**
2. Note the IP address (e.g., `192.168.1.100`)
3. Go to **Settings** → **Features** → **External Control**
4. Install **External Control URCap** if not already installed
5. Create a simple program:
   ```
   BeforeStart:
   1. External Control (localhost, 50002)
   
   Robot Program:
   1. External Control (localhost, 50002) 
   ```
6. Save this program as "External_Control"

### 🔍 **Step 3: Test Connection**

```bash
# Find your robot on the network
python scripts/setup_physical_robot.py --scan
```
**Expected output:**
```
🔍 Scanning for UR robots...
Found robot at: 192.168.1.100 (UR10e)
```

```bash
# Test specific robot connection
python scripts/setup_physical_robot.py --test-ip 192.168.1.100
```
**Expected output:**
```
✅ Connection successful to 192.168.1.100
✅ Robot mode: RUNNING
✅ Safety mode: NORMAL
```

### 🎮 **Step 4: Control Physical Robot**

```bash
# Run basic example with physical robot
python examples/basic_example.py --robot-type physical --robot-ip 192.168.1.100
```

**⚠️ SAFETY NOTES:**
- Always have emergency stop button ready
- Start with slow movements (speed=0.05)
- Keep clear of robot workspace
- Ensure robot workspace is free of obstacles
- Test in manual mode first

### 🛠️ **Troubleshooting Physical Connections**

**Can't find robot:**
```bash
# Check network connectivity
ping 192.168.1.100

# Check if robot ports are open
telnet 192.168.1.100 29999
```

**Robot not responding:**
1. Check robot is in **Remote Control** mode (teach pendant)
2. Verify **External Control** program is running
3. Check firewall settings on your computer
4. Ensure robot safety system is normal (no protective stops)

**Connection timeout:**
- Robot might be in wrong mode
- External Control URCap not properly configured
- Network issues (firewall, wrong IP)

### 📋 **Physical Robot Checklist**

Before running any script with physical robot:

- [ ] Robot is powered on and initialized
- [ ] Safety system shows normal status  
- [ ] Robot is in "Remote Control" mode
- [ ] External Control URCap is installed
- [ ] External Control program is loaded and running
- [ ] Network connection is established
- [ ] Emergency stop is accessible
- [ ] Workspace is clear of people and obstacles
- [ ] You've tested with simulator first

### 🔧 **Advanced: Custom Robot Configuration**

Create `my_physical_robot.yaml`:
```yaml
robot:
  type: "physical"
  ip: "192.168.1.100"  # Your robot's IP
  model: "UR10e"       # Your robot model
  frequency: 500.0

physical:
  safety:
    max_velocity: 0.2        # Slower for safety
    max_acceleration: 0.5    # Gentle acceleration
    workspace_limits:        # Define safe workspace
      x: [-0.8, 0.8]        # X limits in meters
      y: [-0.8, 0.8]        # Y limits in meters  
      z: [0.1, 1.5]         # Z limits in meters

movement:
  default_speed: 0.05       # Start slow!
  default_acceleration: 0.1
```

Use with any script:
```bash
python examples/basic_example.py --config my_physical_robot.yaml
```

## 🛠️ **Programming Reference (API)**

### URRobotController Class - Main Functions

| Function | What It Does | How To Use |
|----------|--------------|------------|
| `connect()` | Connect to robot | `robot.connect()` → Returns `True` if successful |
| `disconnect()` | Disconnect from robot | `robot.disconnect()` |
| `get_tcp_pose()` | Get robot's current position | `pose = robot.get_tcp_pose()` → Returns `[x,y,z,rx,ry,rz]` |
| `move_linear(pose, speed)` | Move to exact position | `robot.move_linear([0.3,-0.3,0.5,0,3.14,0], 0.1)` |
| `move_linear_relative(delta, speed)` | Move relative to current position | `robot.move_linear_relative([0.1,0,0], 0.1)` |
| `move_velocity(velocity, duration)` | Apply velocity for time period | `robot.move_velocity([0.05,0,0,0,0,0], 2.0)` |
| `stop_movement()` | Emergency stop | `robot.stop_movement()` |

### 📏 **Understanding Coordinates**

**Position format:** `[x, y, z, rx, ry, rz]`
- `x, y, z`: Position in meters (+ = right, forward, up)
- `rx, ry, rz`: Rotation in radians around each axis

**Example positions:**
```python
# 30cm right, 40cm back, 50cm up from robot base
position = [0.3, -0.4, 0.5, 0.0, 3.14, 0.0]

# Move 10cm to the right from current position  
relative_move = [0.1, 0.0, 0.0, 0.0, 0.0, 0.0]
```

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

## 🧪 **Testing Your Setup (Step by Step)**

### 🎯 **Quick Tests to Verify Everything Works**

**Test 1: Basic Connection**
```bash
source ur_venv/bin/activate
python scripts/check_robot_status.py
```
**What you should see:**
```
✅ Connection successful!
🤖 Robot Mode: ROBOT_MODE_RUNNING (7)
🛡️ Safety Mode: NORMAL (1)
📍 TCP Pose: [-0.144, -0.436, 0.202, -0.001, 3.116, 0.039]
✅ Robot is ready for control!
```
**If it fails:** Check simulator is running, or robot IP is correct

**Test 2: Visual Movement**
```bash
python scripts/visual_test.py
```
**What you should see:** Robot moving slowly in simulator interface, with output like:
```
🔄 Move UP 10cm...
✅ Movement completed
🔄 Move DOWN to start...
✅ Movement completed
```
**If it fails:** Robot might not be in correct mode, check simulator configuration

**Test 3: Full Functionality**
```bash
python examples/basic_example.py
```
**What you should see:**
```
✅ Connection successful!
📍 Current TCP pose: [-0.144, -0.436, 0.202, ...]
🔄 Moving +10cm in X...
✅ Movement completed
✅ All tests completed successfully!
```
**If it fails:** Check previous tests passed first

### 🔧 **Advanced Tests**

**Test Pre-programmed Sequences:**
```bash
python examples/synchronous_control.py --json-source examples/synchronous_deltas.jsonl
```
**What this tests:** File-based command execution

**Test Real-time Streaming:**
```bash  
python examples/asynchronous_control.py --json-file examples/asynchronous_deltas.jsonl
```
**What this tests:** Continuous command streaming

**Test Physical Robot (if available):**
```bash
python scripts/setup_physical_robot.py --scan
python examples/basic_example.py --robot-type physical --robot-ip YOUR_ROBOT_IP
```
**What this tests:** Real robot connection and control

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
git clone https://github.com/yourusername/ursim_pipeline.git
cd ursim_pipeline

# Install development dependencies
pip install -r requirements.txt
# pip install pytest black flake8  # Optional dev tools
```

---

## 📚 **Quick Navigation**

- [🎯 What This Project Does](#-what-this-project-does) - Understanding the basics
- [🚀 Quick Start](#-quick-start) - Get running in 5 minutes  
- [📖 Complete Guide](#-complete-guide-from-beginner-to-advanced) - Step-by-step tutorial
- [🔧 Available Scripts](#-available-scripts-and-what-they-do) - All commands explained
- [🤖 Physical Robot Setup](#-complete-physical-robot-setup-guide) - Connect to real robots
- [🧪 Testing](#-testing-your-setup-step-by-step) - Verify everything works
- [🛠️ Programming Reference](#-programming-reference-api) - Code examples and API

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Universal Robots** for the RTDE interface and URSim simulator
- **SDU Robotics** for the excellent `ur_rtde` Python library
- **The UR robotics community** for documentation and examples
- **Contributors** who helped improve this project

## 📞 Support

- 📖 **Documentation**: Check this README and run the examples
- 🐛 **Issues**: [Open an issue](https://github.com/erolcem/ursim_pipeline/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/erolcem/ursim_pipeline/discussions)
- 📧 **Email**: Contact the repository owner

## 🏷️ Version History

- **v1.0.0** - Initial release with full simulation and physical robot support
- **v0.9.0** - Beta release with core functionality
- **v0.1.0** - Initial development version

---

<div align="center">

**⭐ Star this repository if it helped you! ⭐**

[🔗 View on GitHub](https://github.com/erolcem/ursim_pipeline) | [📋 Report Bug](https://github.com/erolcem/ursim_pipeline/issues) | [💡 Request Feature](https://github.com/erolcem/ursim_pipeline/issues)

</div>
