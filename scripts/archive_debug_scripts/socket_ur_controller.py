#!/usr/bin/env python3
"""
Socket-Based UR Controller - Uses sockets for both poses and gripper
"""

import socket
import time
import logging
from typing import List, Optional
import yaml

class SocketURController:
    """UR Robot controller using socket-based URScript commands"""
    
    def __init__(self, config_path: str = "config/robot_config.yaml"):
        self.robot_ip = "192.168.1.6"
        self.port = 30002
        self.logger = logging.getLogger('SocketURController')
        self.setup_logging()
        
        # Load config
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Could not load config: {e}")
            self.config = {}
    
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def send_script(self, script: str) -> bool:
        """Send URScript command via socket"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            
            sock.connect((self.robot_ip, self.port))
            sock.send((script + "\n").encode('utf-8'))
            sock.close()
            
            return True
        except Exception as e:
            self.logger.error(f"Socket command failed: {e}")
            return False
    
    def move_to_pose(self, pose: List[float], speed: float = 0.2, acceleration: float = 0.5) -> bool:
        """Move to pose using socket URScript"""
        x, y, z, rx, ry, rz = pose
        
        script = f"""
movel(p[{x}, {y}, {z}, {rx}, {ry}, {rz}], {speed}, {acceleration})
"""
        
        result = self.send_script(script)
        if result:
            self.logger.info(f"Moving to pose: {pose} at speed {speed}")
        return result
    
    def set_gripper(self, state: int, pin: int = 0) -> bool:
        """Control gripper using socket URScript"""
        if state not in [0, 1]:
            self.logger.error(f"Invalid gripper state: {state}")
            return False
        
        script = f"set_tool_digital_out({pin}, {bool(state)})"
        
        result = self.send_script(script)
        if result:
            self.logger.info(f"Gripper {'closed' if state else 'opened'} (tool pin {pin}) via socket")
        return result
    
    def connect(self) -> bool:
        """Test connection to robot"""
        test_script = "# Connection test"
        result = self.send_script(test_script)
        if result:
            self.logger.info("Socket connection verified")
        return result
    
    def disconnect(self):
        """Disconnect (no persistent connection needed for socket)"""
        self.logger.info("Socket controller ready")

def test_socket_controller():
    """Test our new socket-based controller"""
    print("🤖 Testing Socket-Based UR Controller")
    print("=" * 45)
    
    controller = SocketURController()
    
    if not controller.connect():
        print("❌ Connection test failed")
        return
    
    print("✅ Socket controller ready!")
    
    # Test gripper
    print("\n🤏 Testing gripper...")
    controller.set_gripper(0)  # Open
    time.sleep(2)
    controller.set_gripper(1)  # Close
    time.sleep(2)
    controller.set_gripper(0)  # Open again
    
    # Test movement
    print("\n🎯 Testing movement...")
    # Simple relative movements
    scripts = [
        "movel(pose_trans(get_forward_kin(), p[0, 0, 0.03, 0, 0, 0]), 0.2, 0.5)",  # Up 3cm
        "movel(pose_trans(get_forward_kin(), p[0, 0, -0.03, 0, 0, 0]), 0.2, 0.5)", # Down 3cm
    ]
    
    for i, script in enumerate(scripts):
        print(f"   Move {i+1}...")
        controller.send_script(script)
        time.sleep(3)
    
    print("✅ Socket controller test completed!")

if __name__ == "__main__":
    test_socket_controller()
