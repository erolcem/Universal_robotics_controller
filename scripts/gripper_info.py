#!/usr/bin/env python3
"""
Ultra-simple gripper test - just print the command that should work
"""

print("🔧 Based on your teach pendant discovery:")
print("   Tool Digital Output 0 and 1 control the gripper")
print("")
print("🤖 The corrected URScript command should be:")
print("   set_tool_digital_out(0, True)   # Close gripper")
print("   set_tool_digital_out(0, False)  # Open gripper")
print("")
print("📋 To test manually on teach pendant:")
print("   1. Go to I/O tab")
print("   2. Find 'Tool Digital Output 0'")
print("   3. Toggle it True/False to see gripper move")
print("")
print("✅ I've updated the ur_controller.py to use set_tool_digital_out()")
print("   instead of set_digital_out()")
print("")
print("🎯 Next step: Test the synchronous_pose_control_with_gripper.py")
print("   when terminal is stable")
