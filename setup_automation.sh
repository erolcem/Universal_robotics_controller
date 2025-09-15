#!/bin/bash
# MIR Automation Setup Script
echo "🚀 Setting up MIR automation..."

cd /home/erolc/Projects/ursim_pipeline

# Create trigger examples
python3 -c "
from file_auto_controller import FileBasedAutoController
controller = FileBasedAutoController()
controller.create_trigger_files()
print('📁 Trigger files created!')
"

echo ""
echo "✅ SETUP COMPLETE!"
echo ""
echo "📋 Now you have these automation options:"
echo ""
echo "1️⃣  SIMPLE FILE AUTOMATION (Recommended):"
echo "   python3 file_auto_controller.py"
echo "   Then type 'start' to begin monitoring"
echo ""
echo "2️⃣  MANUAL TESTING:"
echo "   python3 simple_mission_controller.py"
echo ""
echo "3️⃣  API AUTOMATION (Advanced):"
echo "   pip install requests"
echo "   python3 true_auto_controller.py"
echo ""
echo "🎯 QUICK TEST:"
echo "   touch mir_triggers/p_start.trigger"
echo "   # This will trigger pickup+compact"
echo ""