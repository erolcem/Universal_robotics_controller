"""
UR Robot Controller

A Python library for controlling Universal Robots (UR) arms through RTDE.
Supports both simulation (URSim) and physical robots.
"""

from .ur_controller import URRobotController, URCommandProcessor

__version__ = "1.0.0"
__author__ = "Erol Cemiloglu"
__license__ = "MIT"

__all__ = ["URRobotController", "URCommandProcessor"]
