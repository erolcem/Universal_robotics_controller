# Archive Directory Contents

This directory contains files that have been archived during the workspace cleanup to create a focused, production-ready robot control system.

## Archive Structure

### `unused_jsonl/`
Archived JSONL files that are no longer needed with the new enhanced control system:
- `asynchronous_deltas.jsonl` - Old delta movement commands
- `synchronous_deltas.jsonl` - Old synchronous delta commands  
- `asynchronous_poses.jsonl` - Old asynchronous pose sequences
- `synchronous_poses.jsonl` - Old synchronous pose sequences

**Note**: These files used different formats and are superseded by the new function-based JSONL files in the `functions/` directory.

### `unused_scripts/`
Archived control scripts that have been replaced by the enhanced interactive control system:
- `asynchronous_control.py` - Old async control implementation
- `simple_control.py` - Basic control script
- `split_control.py` - Split control implementation
- `synchronous_control.py` - Old sync control implementation
- `web_control.py` - Web-based control interface (replaced by multi-interface system)
- `interactive_control.py` - Old interactive control (superseded by enhanced version)
- `visual_test.py` - Old visual movement test script

**Note**: All functionality from these scripts has been integrated into the new `interactive_robot_control.py` system with enhanced features.

## Why These Files Were Archived

1. **Reduce Clutter**: Too many similar control scripts made the workspace confusing
2. **Focus on Best Solution**: The enhanced interactive control system provides all functionality with better features
3. **Maintain History**: Files are preserved for reference but moved out of active workspace
4. **Clear Structure**: New users can focus on the single, comprehensive control system

## Current Active System

The workspace now focuses on:
- **`interactive_robot_control.py`** - Main enhanced control system
- **`robot_cli.py`** - External command-line interface
- **`external_control_example.py`** - Integration example
- **`functions/`** - 12 comprehensive test functions
- **`control/`** - External control interface

This provides a much cleaner, more focused development environment while preserving all the historical work.
