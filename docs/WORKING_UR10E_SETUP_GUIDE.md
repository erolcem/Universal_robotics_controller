# UR10e Physical Robot Connection Guide - WORKING PROCESS

## 🎯 This is the EXACT process that worked successfully!

### Prerequisites
- UR10e robot with External Control URCap installed
- Computer and robot on same network (192.168.1.x)
- ur-rtde library installed (`pip install ur-rtde`)

## 📋 Step-by-Step Working Process

### Step 1: Network Configuration
```bash
# Verify your computer's IP
ip route get 192.168.1.5 | grep -oP 'src \K\S+'
# Should return: 192.168.1.155 (or your computer's IP)
```

### Step 2: Robot Configuration (Critical Settings)
**On Robot Teach Pendant:**

1. **External Control URCap Settings:**
   - Host IP: `192.168.1.155` (your computer's IP)
   - Custom Port: `50002`
   - Host Name: `192.168.1.155` (MUST match Host IP - this was key!)

2. **Create External Control Program:**
   ```
   Program Structure:
   └── External Control (192.168.1.155:50002)
   ```
   - **NO loops or waits** - just the External Control node alone
   - **NO additional commands**

### Step 3: The Working Execution Sequence

**CRITICAL ORDER - This sequence is what made it work:**

1. **Start Python script FIRST:**
   ```bash
   cd /home/erolc/Projects/ursim_pipeline
   source ur_venv/bin/activate
   python scripts/test_simple_movement.py
   ```

2. **Robot steps (while Python script is running):**
   - Put robot in **LOCAL mode**
   - Load External Control program
   - Press **PLAY** (program starts)
   - Switch robot to **REMOTE mode**
   - Robot shows "External Control Active" ✅

3. **Python script connects and moves robot** ✅

## 🔧 Key Technical Details That Made It Work

### The Critical Configuration Fix
- **Host Name field** was set to `192.168.56.1` (WRONG)
- **Changed to** `192.168.1.155` (CORRECT - matches Host IP)
- This field controls the actual connection target

### The Working Script Structure
```python
# This is what worked:
rtde_c = rtde_control.RTDEControlInterface("192.168.1.5")
if rtde_c.isConnected():
    # Get current position
    current_pose = rtde_c.getActualTCPPose()
    
    # Move 1cm in X direction
    new_pose = current_pose.copy()
    new_pose[0] += 0.01  # +1cm in X
    rtde_c.moveL(new_pose, 0.1, 0.3)  # speed=0.1, accel=0.3
    
    # Return to start
    rtde_c.moveL(current_pose, 0.1, 0.3)
```

## 🎯 Troubleshooting - What We Fixed

### Issue 1: "Receive program failed"
**Problem:** Robot couldn't connect back to computer
**Solution:** Fixed Host Name field to match Host IP

### Issue 2: "Connection refused"  
**Problem:** Wrong execution order
**Solution:** Start Python script BEFORE starting robot program

### Issue 3: Program loops/timeouts
**Problem:** External Control in a loop with waits
**Solution:** External Control as standalone program node

## 📋 Quick Test Checklist

Before trying to move the robot, verify:

```bash
# 1. Network connectivity
ping 192.168.1.5

# 2. Python environment
source ur_venv/bin/activate
python -c "import rtde_control; print('ur-rtde OK')"

# 3. Basic connection test
python scripts/test_simple_movement.py
```

## 🚀 Next Steps - Now That It Works

### Test the Examples
```bash
# Basic movements
python examples/basic_example.py

# More complex control
python examples/synchronous_control.py
python examples/asynchronous_control.py
```

### Modify for Your Needs
- Update `config/robot_192_168_1_5.yaml` for your workspace limits
- Adjust speeds/accelerations for safety
- Add your custom movement sequences

## 🛡️ Safety Reminders

- **Always have emergency stop accessible**
- **Start with slow movements** (speed ≤ 0.1 m/s)
- **Clear workspace** before running programs
- **Stay alert** - physical robots can cause injury

## 🎉 Success Indicators

When everything is working correctly:
- ✅ Robot shows "External Control Active"
- ✅ Python script connects without errors
- ✅ Robot responds to movement commands
- ✅ Movements are smooth and controlled

---

## 📞 Emergency Contacts / References

- **Emergency Stop:** Physical red button on robot
- **ur-rtde docs:** https://sdurobotics.gitlab.io/ur_rtde/
- **UR Manual:** [Robot teach pendant → Help → Manual]

**🎯 This process worked on:** `2025-07-21` with UR10e robot
**✅ Verified working setup**
