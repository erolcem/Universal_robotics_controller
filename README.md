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
Step 1: Download + understand Docker
1.1: Get docker from here:
Docker Desktop: The #1 Containerization Tool for Developers
Docker contains containers
Images can exist in containers
Images are made from dockerfile + sample application
1.2: Do these in the learning centre:
You’ll learn how to make the container using code and dockerfile:
These will teach you how to pull and run a container from a code and thus image.
It will not teach you how to access files outside the container, nor how to access the
container's results persisting outside the container lifetime. There are other lessons you may
watch for that but are not necessary.
However, the docker app just needs to be open for the rest of the steps.Step 2: Prepare the Ursim container
2.1 - Get Ursim from here
Make a new directory first, Lets say ursim
Inside we pull the image from docker of the simulator.
docker pull universalrobots/ursim_e-series:latest
2.2 - Prepare the python venv
We make a virtual environment in python for clarity to store and containerise all the
necessary packages in line with the docker container, making everything rather neat and
tidy.
We also install ur_rtde package here, which allows us to control the simulated robot.
(This venv is called ur_venv)
python3 -m venv ur_venv
source ./ur_venv/bin/activate
pip install ur_rtde
Remember a venv can be closed via deactivate
2.3 - Placing necessary executables
Now we will also be putting two files, they should come attached with this documentation
ur_example.py, which is our executable python file,
And startDocker.sh, which is our executable docker container maker from the image we
made.
These all go under the main folder hence:
>>Ursim
​
>> ur_venv
​
>> startDocker.sh
​
>> ur_example.py
2.4 - You can start your docker container now,
Remember to still be in the folder; Ursim.
We use the docker executable for this, recall in some systems, you may need to provide
permissions to do this:
Eg. on Linux: chmod +x startDocker.py
./startDocker.sh
If you are curious what is in startDocker commands: it is:
docker run --rm -it \
-p 5900:5900 \
-p 6080:6080 \
-p 29999:29999 \
-p 30001-30004:30001-30004 \-e ROBOT_MODEL=UR5E \
-e URSIM_ROBOT_MODE=SIMULATION \
--name ursim_e_series \
universalrobots/ursim_e-series
Should you be successful, you should see the terminal print the following:
Step 3: Prepare the Ursim container
3.1 - Open the simulator:
Simply click on this link:
http://localhost:6080/vnc.htmlWhich should take you to here​
Press [Confirm Safety Configuration]
And then at the bottom right corner, turn ON [Simulation]
Then go to Program → Graphics: This is where the robot simulation will take place. Notice,
however, that there is no robot showing:
So to activate the robot arm we need a second step: Go to Move on the top left corner.When you go in this menu, you’ll notice that there is still no robot in the middle. But you get a
suggestion to power ON the robot via the bottom left button: Press that.
Press ON, then press START to take the robot out of the safety brake and allow all the 5
circles to be green; this means the robot is operational and readyHere, now just press EXIT at the bottom left corner, and then go back to PROGRAM ->
Graphics, you should see the robot like the following:
(Just double check that Simulation at the bottom right corner is still turned ON)Step 4: Run the test python script:
4.1 - Open a new terminal tab in the same directory
The python script is another node that runs concurrently with this docker container, it should
ideally run continuously and thus can take streaming data such as from a json file.
We do this by opening a new terminal in the same directory.
Remember to activate the venv!
>> ursim
source ./ur_venv/bin/activate
4.2 - Run the python file executable
./ur_example.py
Opening the website again while this is running, you should see the the robot do a series of
movement tests.
Ur_example.py is a testing document to validate that the simulation is working as expected.
And simply diagnoses the operational state of this simulation system.
If the system has worked correctly, we can move on with the more interesting python file,
ur_synchronous.py which will actuate commands based on the stream of json files
entering.Step 5: Operate the arm using json files:
5.1 - Place the operation files
Attached you will also find a python file called
ur_synchronous.py, using that, place under the ur_venv directory, same as all the other
files we’ve put so far.
Additionally, there is an example commands input jsonl file for use to test this code called
synchronous_deltas.jsonl
Your directory should look like this now:
>> ursim_test
​
>> ur_example.py
​
>> ur_synchronous.py
​
>> synchronous_deltas.jsonl
​
>> ur_venv
If you investigate the json file, you’ll find it simply moves the arm one direction and then
back, feel free to modify it to your preference.
5.2 - Operation
./ur_synchronous.py
You should find the arm moving left and then right and then left again.
5.3 - How to modify the json commands file?
How does the jsonl work?
Jsonl is a json file where each line represents an appendable, separate instance, in this case
it is an instruction.Here is synchronous_deltas.jsonl
{"dx": -0.05, "dy": 0.00, "dz": 0.00}
{"dx": -0.05, "dy": 0.00, "dz": 0.00}
{"dx": -0.05, "dy": 0.00, "dz": 0.00}
{"dx": 0.05, "dy": 0.00, "dz": 0.00}
{"dx": 0.05, "dy": 0.00, "dz": 0.00}
{"dx": 0.05, "dy": 0.00, "dz": 0.00}
{"dx": 0.05, "dy": 0.00, "dz": 0.00}
{"dx": -0.05, "dy": 0.00, "dz": 0.00}
{"dx": -0.05, "dy": 0.00, "dz": 0.00}
{"dx": -0.05, "dy": 0.00, "dz": 0.00}
{"dx": 0.00, "dy": 0.00, "dz": 0.00}
Note how it moves the arm left, then right and then left again (dx represents speed and it
applies once every second)
A valid extra 3 commands is also:
{"dx": 0.00, "dy": 0.00, "dz": 0.00 "drx": 0.00, "dry": 0.00, "drz":
0.00}
Where drx dry and drz represent rotation of the planes where the end of the arm is located
relative to its current coordinate orientation.
The python node will apply once every second to apply the next line in the jsonl file, if there
are no lines left, it will abort. However, jsonl files can have new lines dynamically added to
them. Thus if a software wishes to add commands in real time, it need only to add a
command once a second to achieve this.
Should you wish to change the frequency of these pre prepared commands, there are some
flags you can call with the function ur_synchronous.py.
parser = argparse.ArgumentParser(
description="Stream JSON delta movements once per second and
move the UR robot accordingly."
)
parser.add_argument(
"--robot-ip", default="127.0.0.1",
help="IP address of the UR robot or simulator"
)
parser.add_argument(
"--json-source", default="synchronous_deltas.jsonl",help="Path to JSON-line file of {'dx','dy','dz',…} messages
(use '-' for stdin)"
)
parser.add_argument(
"--json-log", default="synchronous_log.jsonl",
help="Path to append timestamped JSON log"
)
parser.add_argument(
"--speed", type=float, default=0.2,
help="Cartesian speed (unused with speedL, placeholder)"
)
parser.add_argument(
"--acceleration", type=float, default=0.5,
help="Acceleration for speedL (m/s²)"
)
parser.add_argument(
"--responsiveness", type=float, default=1.0,
help="How often each command line in json file takes effect
(seconds)"
)
The jsonl file that is logged, sourced from, robot ip can all be selected via arguments.
(However the defaults are conveniently preselected for you)
The acceleration argument changes the relative speed of the movements should you wish
an overall slower or faster robot.
The responsiveness command refers to the frequency of commands the robot takes from the
jsonl file, this is where the 1 second comes from, but can be customised to meet a more
dynamic and lower latency robot.
To apply these arguments, simply call in the terminal such as this example:
./ur_synchronous.py --responsiveness 2
In this case the robot commands only read the jsonl new line once every 2 seconds now.
Step 6: Having a streaming pipeline
6.1: - Place the new operation filesWhilst this synchronous file set can perform robot commands, it is still a step from being real
time responsive. As it is unlikely for commands to exactly match once a second (or arbitrary
time step); perfect synchronization is difficult and unnecessary.
This issue is solved with a different implementation, one of which is for users who wish for a
true streaming implementation of jsonl commands to the robot arm.
Attached you will also find a python file called
ur_asynchronous.py, using that, place under the ur_venv directory, same as all the other
files we’ve put so far.
Additionally, there is an example commands input jsonl file for use to test this code called
asynchronous_deltas.jsonl
Your directory should look like this now:
>> ursim_test
​
>> ur_example.py
​
>> ur_synchronous.py
​
>> synchronous_deltas.jsonl
>> ur_asynchronous.py
​
>> asynchronous_deltas.jsonl
​
>> ur_venv
6.2 - Operation
./ur_asynchronous.py
What you will find is that, there will be no movement, but rather, a constant reading thats
streamed to the robot without stopping. This streaming node is always on until it is stopped
via ctrl+c.
If you'd like to see the robot move, append a new line to the jsonl file.The asynchronous node will read the last line in the file every second, in essence applying
the most recent velocity to the robot simulation.
This update can be sped up with the responsiveness argument as before: refer to the
asynchronous arguments for any other requests:
description='Read tail of JSONL and apply delta velocities
each second'
)
parser.add_argument('--robot-ip', default='127.0.0.1', help='UR
IP')
parser.add_argument('--json-file',
default='asynchronous_deltas.jsonl', help='source jsonl file')
parser.add_argument('--acceleration', type=float, default=0.5,
help='Acceleration')
parser.add_argument('--responsiveness', type=float, default = 1.0,
help='responsiveness')
With this done, as long as your docker container is running for the robot, you have a working
simulation.
And as long as you have the ur_asynchronous.py running,
Whatever velocity information is in the final line of the asynchronous_deltas.jsonl file, it will
be streamed to the robot arm.
Step 7: BONUS: How to apply pipeline to a real UR arm.
TBA
