#!/usr/bin/env python3
"""
INTEGRATED MIR-UR AUTOMATION SYSTEM
Complete integration of MIR API monitoring with UR robot control
"""

import time
import threading
import requests
from pathlib import Path
import json
import subprocess
import sys
import re
from collections import deque

class IntegratedMirUrController:
    """Complete MIR API + UR Robot automation"""
    
    def __init__(self, mir_ip="118.138.122.43"):
        self.mir_ip = mir_ip
        self.mir_base_url = f"http://{mir_ip}/api/v2.0.0"
        # Use a session with default MiR credentials for reliable control
        self.session = requests.Session()
        self.session.auth = ("Distributor", "distributor")
        self.control_dir = Path("control")
        self.control_dir.mkdir(exist_ok=True)
        
        # Monitoring state
        self.monitoring = False
        self.last_mission_text = ""
        self.last_position = None
        self.executed_positions = set()
        # Pause behavior: keep MiR paused for the entire workflow at a position
        # instead of pausing/resuming between each individual UR function
        self.pause_mir_entire_workflow = True
        # Motion/arrival helpers
        self.position_samples = deque(maxlen=6)  # (t, x, y)
        self.arrival_distance_threshold = 0.01  # meters (treat 0.2m as near-goal)
        self.stationary_speed_threshold = 0.01  # m/s over recent samples
        self.last_target_position = None       # canonical name like 'p_start', 'pl1'
        self.last_target_time = 0.0
        self.last_meters_to_goal = None

        # Debounce / state controls
        self.cooldown_sec = 60  # minimum seconds between triggering the same position
        self.position_cooldowns = {}  # pos -> last_trigger_time
        self.trigger_lock_until = 0.0  # global lock to avoid overlapping workflows
        self.require_leave = True  # require leaving a position before re-triggering
        self.last_detected_position = None
        self.last_detected_change_time = 0.0
        
        # FYP Mission workflows
        self.position_workflows = {
            "p_start": {
                "commands": ["pickup", "compact"],
                "description": "Pickup station - grab item and compact",
                "patterns": ["p_start", "start", "pickup", "p start", "beginning"]
            },
            "pl1": {
                "commands": ["home", "dropoff1", "home", "compact"],
                "description": "Left position 1 - dropoff and return",
                "patterns": ["pl1", "pl 1", "left 1", "left1", "position 1"]
            },
            "pl2": {
                "commands": ["home", "dropoff2", "home", "compact"],
                "description": "Left position 2 - dropoff and return", 
                "patterns": ["pl2", "pl 2", "left 2", "left2", "position 2"]
            },
            "pr1": {
                "commands": ["home", "dropoff4", "home", "compact"],
                "description": "Right position 1 - safe dropoff and return",
                "patterns": ["pr1", "pr 1", "right 1", "right1", "position 3"]
            },
            "pr2": {
                "commands": ["home", "dropoff3", "home", "compact"],
                "description": "Right position 2 - safe dropoff and return",
                "patterns": ["pr2", "pr 2", "right 2", "right2", "position 4"]
            }
        }

        # Arrival detection keywords
        self._arrived_keywords = ["reached", "arrived", "waiting", "at "]
        self._moving_keywords = ["moving", "driving", "navigating", "going to"]

    # ----- Internal helpers -----
    def _get_status(self):
        try:
            response = self.session.get(f"{self.mir_base_url}/status", timeout=5)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return None

    def _is_stationary(self, state_text: str) -> bool:
        st = (state_text or "").lower()
        # Stationary if paused or ready or waiting
        if any(k in st for k in ["pause", "paused", "ready", "waiting"]):
            return True
        # Or based on motion over recent samples
        if len(self.position_samples) >= 2:
            t0, x0, y0 = self.position_samples[0]
            t1, x1, y1 = self.position_samples[-1]
            dt = max(1e-3, t1 - t0)
            dist = ((x1 - x0)**2 + (y1 - y0)**2) ** 0.5
            speed = dist / dt
            return speed <= self.stationary_speed_threshold
        return False

    def _is_arrival_text(self, mission_text: str) -> bool:
        mt = (mission_text or "").lower()
        if any(k in mt for k in self._moving_keywords):
            return False
        if any(k in mt for k in self._arrived_keywords):
            return True
        # Fallback: if it names a known goal and NOT moving terms, accept
        return True

    def _parse_meters_to_goal(self, mission_text: str):
        """Extract meters to goal as float from mission text like "(0.9 meters to goal)" if present."""
        if not mission_text:
            return None
        m = re.search(r"\(([-+]?[0-9]*\.?[0-9]+)\s*meters?\s*to\s*goal\)", mission_text)
        if m:
            try:
                return float(m.group(1))
            except ValueError:
                return None
        return None

    def _wait_for_mir_paused(self, timeout: float = 8.0) -> bool:
        """Wait until MiR reports paused. Returns True if paused within timeout."""
        start = time.time()
        while time.time() - start < timeout:
            status = self._get_status()
            if status:
                state = (status.get('state_text', '') or '').lower()
                state_id = status.get('state_id')
                if 'pause' in state or state_id == 4:
                    time.sleep(1)
                    return True
            time.sleep(0.5)
        return False

    def _direct_pause(self) -> bool:
        """Attempt to pause MiR directly via API (fallback when controller isn't pausing)."""
        try:
            resp = self.session.put(f"{self.mir_base_url}/status", json={"state_id": 4}, timeout=5)
            if resp.status_code in (200, 204):
                return True
        except Exception:
            pass
        return False

    def _ensure_mir_paused(self, timeout: float = 8.0) -> bool:
        """First rely on UR controller (mir_pause command), then fallback to direct API pause if needed."""
        # 1) Wait for pause via UR controller command processing
        if self._wait_for_mir_paused(timeout=timeout):
            return True
        # 2) Fallback to direct API pause
        print("  🔁 Falling back to direct MiR API pause...")
        if self._direct_pause():
            if self._wait_for_mir_paused(timeout=5.0):
                print("  ✅ MiR paused via direct API")
                return True
        print("  ❌ Failed to pause MiR via controller and direct API")
        return False
    
    def test_mir_connection(self):
        """Test MIR API connection"""
        try:
            print(f"🧪 Testing MIR connection to {self.mir_ip}...")
            response = self.session.get(f"{self.mir_base_url}/status", timeout=5)
            
            if response.status_code == 200:
                status = response.json()
                state = status.get('state_text', 'unknown')
                mission = status.get('mission_text', 'none')
                battery = status.get('battery_percentage', 0)
                
                print(f"✅ MIR Connected!")
                print(f"   State: {state}")
                print(f"   Mission: {mission}")
                print(f"   Battery: {battery:.1f}%")
                return True
            else:
                print(f"❌ MIR connection failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ MIR connection error: {e}")
            return False
    
    def detect_position_from_mission(self, mission_text):
        """Detect current position from mission text"""
        if not mission_text:
            return None
            
        mission_lower = mission_text.lower()
        
        # Check each position's patterns
        for position, config in self.position_workflows.items():
            for pattern in config["patterns"]:
                if pattern in mission_lower:
                    return position
        
        return None
    
    def monitor_mir_status(self):
        """Monitor MIR status and trigger UR operations"""
        print("🔍 Starting MIR monitoring...")
        consecutive_errors = 0
        
        while self.monitoring:
            try:
                # Get MIR status
                response = self.session.get(f"{self.mir_base_url}/status", timeout=5)
                
                if response.status_code == 200:
                    consecutive_errors = 0
                    status = response.json()
                    
                    state = (status.get('state_text', '') or '').strip()
                    mission_text = (status.get('mission_text', '') or '').strip()
                    battery = status.get('battery_percentage', 0)
                    pos = status.get('position') or {}
                    px = float(pos.get('x') or 0.0)
                    py = float(pos.get('y') or 0.0)
                    now = time.time()
                    # Track recent positions for motion estimation
                    self.position_samples.append((now, px, py))

                    # Track last moving target from mission text (e.g., Moving to 'P_start')
                    mt_lower = mission_text.lower()
                    m = re.search(r"moving to\s*'([^']+)'", mt_lower)
                    if m:
                        raw_name = m.group(1)
                        # Map raw_name to canonical position using existing detector
                        mapped = self.detect_position_from_mission(raw_name)
                        if mapped:
                            self.last_target_position = mapped
                            self.last_target_time = now
                    # Track last meters-to-goal when available
                    meters_to_goal_now = self._parse_meters_to_goal(mission_text)
                    if meters_to_goal_now is not None:
                        self.last_meters_to_goal = meters_to_goal_now
                    
                    # Print status every ~3 seconds (faster feedback)
                    if int(now * 2) % 6 == 0:
                        print(f"📊 MIR Status: {state} | Mission: {mission_text} | Battery: {battery:.1f}%")
                    
                    # Guardrails: don't trigger while MIR is in error/failed/e-stop
                    mission_lower = mission_text.lower()
                    state_lower = state.lower()
                    blocked_reasons = []
                    if any(s in state_lower for s in ["error", "e-stop", "emergency"]):
                        blocked_reasons.append(f"state='{state}'")
                    if "failed" in mission_lower or "failed to reach" in mission_lower:
                        blocked_reasons.append(f"mission='{mission_text}'")
                    if blocked_reasons:
                        # Reset edge detection to require a fresh arrival after recovery
                        if self.last_detected_position is not None:
                            self.last_detected_position = None
                            self.last_detected_change_time = now
                        if int(now) % 10 == 0:
                            print(f"⏸️  Triggering blocked due to MIR condition: {', '.join(blocked_reasons)}")
                        time.sleep(2)
                        continue

                    # Detect position and arrival
                    candidate_position = self.detect_position_from_mission(mission_text)
                    meters_to_goal = self._parse_meters_to_goal(mission_text)
                    is_stationary = self._is_stationary(state) or ("waiting" in mt_lower)
                    arrival_text_ok = self._is_arrival_text(mission_text)
                    near_goal = (
                        (meters_to_goal is not None and meters_to_goal <= self.arrival_distance_threshold)
                        or (
                            self.last_meters_to_goal is not None
                            and self.last_meters_to_goal <= self.arrival_distance_threshold
                            and (now - self.last_target_time) <= 12.0
                        )
                    )

                    current_position = None
                    if candidate_position and ((is_stationary and arrival_text_ok) or near_goal):
                        current_position = candidate_position
                    # Fallback: if we're stationary or waiting at the goal without explicit name in mission text
                    elif ("waiting" in mt_lower) or (
                        self.last_meters_to_goal is not None and self.last_meters_to_goal <= self.arrival_distance_threshold
                    ):
                        if self.last_target_position and ((now - self.last_target_time) <= 30.0):
                            current_position = self.last_target_position
                    # Edge detection: only consider new arrivals
                    if current_position != self.last_detected_position:
                        self.last_detected_change_time = now
                        self.last_detected_position = current_position
                    
                    # Only trigger on a new stable detection (debounced)
                    if current_position:
                        stable_for = now - self.last_detected_change_time
                        # Require position to be stable for at least 2 seconds
                        min_stable = 1.0 if meters_to_goal is not None and meters_to_goal <= 0.05 else 2.0
                        if stable_for < min_stable:
                            time.sleep(0.25)
                            continue

                        # Global lock: avoid retriggering while a workflow is in flight
                        if now < self.trigger_lock_until:
                            # Still cooling down from a previous trigger
                            time.sleep(0.25)
                            continue

                        # Per-position cooldown
                        last_t = self.position_cooldowns.get(current_position, 0.0)
                        if (now - last_t) < self.cooldown_sec:
                            # Within cooldown window
                            time.sleep(0.25)
                            continue

                        # If require_leave is enabled, ensure we left the previous position
                        if self.require_leave and self.last_position == current_position:
                            # We haven't left since last trigger
                            time.sleep(0.25)
                            continue

                        print(f"\n🎯 POSITION DETECTED: {current_position.upper()}")
                        print(f"📍 Mission text: {mission_text}")

                        # Execute UR workflow
                        queued = self.execute_ur_workflow(current_position)
                        if queued:
                            self.position_cooldowns[current_position] = now
                            self.last_position = current_position
                            # Estimate lock duration based on number of commands (approx 6s per command)
                            cmds_count = len(self.position_workflows.get(current_position, {}).get("commands", []))
                            self.trigger_lock_until = now + max(30, cmds_count * 6)
                        else:
                            # If not queued, don't set cooldown
                            pass
                
                else:
                    consecutive_errors += 1
                    if consecutive_errors > 3:
                        print(f"⚠️ MIR connection issues: HTTP {response.status_code}")
                
                time.sleep(0.5)  # Check twice per second for responsiveness
                
            except Exception as e:
                consecutive_errors += 1
                if consecutive_errors > 5:
                    print(f"❌ MIR monitoring error: {e}")
                    time.sleep(5)  # Wait longer after errors
                else:
                    time.sleep(2)
    
    def execute_ur_workflow(self, position):
        """Execute UR workflow for detected position"""
        if position not in self.position_workflows:
            print(f"❌ Unknown position: {position}")
            return False
        
        config = self.position_workflows[position]
        commands = config["commands"]
        description = config["description"]
        
        print(f"🤖 Executing {position.upper()}: {description}")
        print(f"📋 Sequence: {' → '.join(commands)}")
        
        # Send commands to UR via external control file
        command_file = self.control_dir / "robot_commands.txt"
        speed = 0.1
        
        # Phase 1: request MiR pause and wait until paused
        if self.pause_mir_entire_workflow:
            with open(command_file, "a") as f:
                f.write("mir_pause\n")
            print("  ⏸️  Requesting MIR pause (waiting up to 8s)")
            if not self._ensure_mir_paused(timeout=8.0):
                print("  ⚠️  Proceeding without confirmed pause; behavior may be suboptimal")
        
        # Phase 2: queue UR functions
        with open(command_file, "a") as f:
            for i, command in enumerate(commands):
                if self.pause_mir_entire_workflow:
                    f.write(f"add {command} {speed}\n")
                    print(f"  📤 {i+1}/{len(commands)} {command}")
                else:
                    pause_mir = command != "compact"
                    if pause_mir:
                        f.write(f"add {command} {speed} true\n")
                    else:
                        f.write(f"add {command} {speed}\n")
                    print(f"  📤 {i+1}/{len(commands)} {command} {'(pause MIR)' if pause_mir else ''}")

            if self.pause_mir_entire_workflow:
                f.write("mir_resume\n")
                print("  ▶️  MIR will resume after UR queue completes (deferred by controller)")
        
            print(f"✅ {position.upper()} workflow queued!")
        return True
    
    def start_monitoring(self):
        """Start MIR monitoring"""
        if self.monitoring:
            print("⚠️ Already monitoring")
            return
        
        # Test connection first
        if not self.test_mir_connection():
            print("❌ Cannot start - MIR connection failed")
            return
        
        print("\n🚀 STARTING INTEGRATED MIR-UR AUTOMATION")
        print("=" * 50)
        print("🔍 Monitoring MIR mission status")
        print("🤖 Will trigger UR operations automatically")
        print()
        print("📋 Position workflows:")
        for pos, config in self.position_workflows.items():
            print(f"   {pos.upper()}: {' → '.join(config['commands'])}")
        print()
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_mir_status)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        print("✅ Monitoring started!")
        print("💡 Start your 'FYP moving test' mission on the MIR")
        print("🎯 UR operations will trigger automatically at each position")
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        print("🛑 Monitoring stopped")
    
    def reset_executions(self):
        """Reset executed positions (for testing)"""
        self.executed_positions.clear()
        print("🔄 Reset executed positions")
    
    def manual_trigger(self, position):
        """Manual trigger for testing"""
        if position in self.position_workflows:
            print(f"🎯 Manual trigger: {position}")
            self.execute_ur_workflow(position)
        else:
            print(f"❌ Unknown position: {position}")
            print(f"Available: {list(self.position_workflows.keys())}")

def main():
    """Main control interface"""
    controller = IntegratedMirUrController()
    
    print("🤖 INTEGRATED MIR-UR AUTOMATION SYSTEM")
    print("=" * 45)
    print("🎯 Full automation: MIR API → UR Robot")
    print()
    print("📋 Commands:")
    print("   test     - Test MIR connection")
    print("   start    - Start full automation")
    print("   stop     - Stop automation")
    print("   reset    - Reset executed positions")
    print("   trigger <pos> - Manual trigger")
    print("   status   - Check current status")
    print("   positions - Show available positions")
    print("   quit     - Exit")
    print()
    print("💡 Make sure your UR robot control system is running!")
    
    try:
        while True:
            cmd = input("\n🤖 Command: ").strip().lower()
            
            if cmd == "quit":
                break
            elif cmd == "test":
                controller.test_mir_connection()
            elif cmd == "start":
                controller.start_monitoring()
            elif cmd == "stop":
                controller.stop_monitoring()
            elif cmd == "reset":
                controller.reset_executions()
            elif cmd == "positions":
                print("📍 Available positions:")
                for pos, config in controller.position_workflows.items():
                    print(f"   {pos.upper()}: {config['description']}")
                    print(f"      Commands: {' → '.join(config['commands'])}")
            elif cmd == "status":
                controller.test_mir_connection()
            elif cmd.startswith("trigger"):
                parts = cmd.split()
                if len(parts) > 1:
                    controller.manual_trigger(parts[1])
                else:
                    print("Usage: trigger <position>")
                    print(f"Available: {list(controller.position_workflows.keys())}")
            else:
                print("❌ Unknown command. Type commands above.")
    
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop_monitoring()
        print("\n✅ Integrated automation shut down")

if __name__ == "__main__":
    main()