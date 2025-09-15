#!/bin/bash
# Start API-based automation
echo "🤖 Starting TRUE API automation..."
echo "This will automatically detect when MIR reaches positions!"
echo ""

cd /home/erolc/Projects/ursim_pipeline

# Start the API automation in the background
./ur_venv/bin/python3 -c "
from true_auto_controller import TrueAutoController
import time

print('🚀 STARTING TRUE AUTOMATION')
print('📡 Connecting to MIR API at 118.138.107.60...')

controller = TrueAutoController()

# Test connection first
print('🧪 Testing connection...')
if controller.test_connection():
    print('✅ MIR connected! Starting automatic monitoring...')
    print()
    print('📋 The system will now automatically:')
    print('   🔍 Monitor MIR mission status')
    print('   🎯 Detect when MIR reaches positions') 
    print('   🤖 Trigger UR operations automatically')
    print()
    print('💡 Your MIR should run \"FYP moving test\" mission')
    print('   P_start → PL1 → P_start → PL2 → P_start → PR1 → P_start → PR2')
    print()
    
    # Start monitoring
    controller.start_automation()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('\n🛑 Stopping automation...')
        controller.stop_automation()
        print('✅ Automation stopped')
else:
    print('❌ Could not connect to MIR')
"