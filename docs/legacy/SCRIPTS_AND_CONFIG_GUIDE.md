# UR10e Scripts & Configuration Guide

## 📋 SCRIPTS DIRECTORY OVERVIEW

### ✅ ESSENTIAL SCRIPTS (Current Directory)

| Script | Purpose | When to Use | Command |
|--------|---------|-------------|---------|
| `quick_ur10e_test.py` | **Quick verification** - Test if robot works | Daily testing, troubleshooting | `python scripts/quick_ur10e_test.py` |
| `test_simple_movement.py` | **Basic movement test** - 1cm movement | Verify robot control | `python scripts/test_simple_movement.py` |
| `setup_physical_robot.py` | **Creates config files** - Auto-generates robot config | Initial setup, new robots | `python scripts/setup_physical_robot.py --test-ip 192.168.1.5` |

### 🔧 DIAGNOSTIC SCRIPTS (Troubleshooting)

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `diagnose_robot_connection.py` | Network & connection diagnostics | Connection problems |
| `debug_external_control.py` | External Control specific issues | External Control failures |
| `test_dashboard_only.py` | Read-only robot status | When External Control doesn't work |

### 📦 OTHER SCRIPTS (Legacy/Utility)

| Script | Purpose | Notes |
|--------|---------|-------|
| `check_robot_status.py` | Basic robot status check | Legacy script |
| `test_movement.py` | Alternative movement test | Similar to test_simple_movement.py |
| `visual_test.py` | Visual/GUI test | Rarely used |
| `startDocker.sh` | Docker startup script | For containerized setup |

### ✅ CLEANUP COMPLETE

Redundant scripts have been removed:
- ~~`test_external_control.py`~~ ✅ Deleted
- ~~`proper_external_control.py`~~ ✅ Deleted  
- ~~`test_urrtde_style.py`~~ ✅ Deleted
- ~~`streamlined_ur10e_setup.py`~~ ✅ Deleted
- ~~`setup_external_control.py`~~ ✅ Deleted

## 🔧 CONFIGURATION SYSTEM

### How Config Files Are Created

**The script that creates config files:**
```bash
python scripts/setup_physical_robot.py --test-ip 192.168.1.5
```

This creates: `config/robot_192_168_1_5.yaml`

### How Examples Choose Config Files

Examples use this priority order:

1. **Command line argument:**
   ```bash
   python examples/basic_example.py --config my_config.yaml
   ```

2. **Default fallback:**
   ```bash
   # Falls back to: config/robot_config.yaml
   python examples/basic_example.py
   ```

### Current Config Files ✅ CLEANED

| File | Purpose | Status |
|------|---------|--------|
| `robot_config.yaml` | **Default config** - Used by examples | ✅ Active |
| `robot_192_168_1_5.yaml` | **Auto-generated** - Your physical robot | ✅ Active |
| `robot_config_template.yaml` | Template for new configs | Reference only |

### ✅ Cleanup Complete
- ~~`robot_config copy.yaml`~~ ✅ Deleted

## 🚀 RECOMMENDED WORKFLOW

### Daily Robot Use (Simple)
```bash
# 1. Quick test (robot must be in Remote mode)
python scripts/quick_ur10e_test.py

# 2. Run examples
python examples/basic_example.py
python examples/asynchronous_control.py
```

### Initial Setup (One-time)
```bash
# 1. Create config for your robot
python scripts/setup_physical_robot.py --test-ip 192.168.1.5

# 2. Test basic movement
python scripts/test_simple_movement.py

# 3. Run examples
python examples/basic_example.py
```

### Troubleshooting (When things break)
```bash
# 1. Diagnose connection
python scripts/diagnose_robot_connection.py 192.168.1.5

# 2. Debug External Control
python scripts/debug_external_control.py

# 3. Test read-only connection
python scripts/test_dashboard_only.py
```

## 🧹 CLEANUP COMPLETE ✅

### Scripts Remaining (Clean):
- `quick_ur10e_test.py` ✅
- `test_simple_movement.py` ✅
- `setup_physical_robot.py` ✅
- `diagnose_robot_connection.py` ✅
- `debug_external_control.py` ✅
- `test_dashboard_only.py` ✅
- Plus legacy/utility scripts

### Scripts Removed:
- ~~`test_external_control.py`~~ ✅ Deleted
- ~~`proper_external_control.py`~~ ✅ Deleted
- ~~`test_urrtde_style.py`~~ ✅ Deleted
- ~~`streamlined_ur10e_setup.py`~~ ✅ Deleted
- ~~`setup_external_control.py`~~ ✅ Deleted

### Config Files Remaining (Clean):
- `robot_config.yaml` ✅ (default)
- `robot_192_168_1_5.yaml` ✅ (your robot)
- `robot_config_template.yaml` ✅ (reference)

### Config Files Removed:
- ~~`robot_config copy.yaml`~~ ✅ Deleted

## 🎯 EXAMPLES EXPLAINED

### How Examples Work
All examples default to `config/robot_config.yaml` unless specified:

```python
# In each example:
default_config = Path(__file__).parent.parent / "config" / "robot_config.yaml"
```

### To Use Your Physical Robot Config:
```bash
# Option 1: Use command line
python examples/basic_example.py --config config/robot_192_168_1_5.yaml

# Option 2: Replace default config
cp config/robot_192_168_1_5.yaml config/robot_config.yaml
python examples/basic_example.py
```

## 📝 SUMMARY

- **Main config:** `robot_config.yaml` (update this with your robot settings)
- **Daily use:** `quick_ur10e_test.py` then examples
- **Setup:** `setup_physical_robot.py` creates configs automatically
- **Troubleshooting:** Diagnostic scripts for when things break
- **Cleanup:** Delete 5 redundant scripts, keep 6 essential ones
