#!/bin/bash
echo "🚀 STARTING COMPLETE MIR-UR AUTOMATION SYSTEM"
echo "=" * 50

cd /home/erolc/Projects/ursim_pipeline

echo "🤖 Step 1: Starting UR Robot Control System..."
python3 unified_robot_control_simple.py --robot-ip 192.168.1.6 --mir-ip offline &
UR_PID=$!

echo "⏳ Waiting 3 seconds for UR system to initialize..."
sleep 3

echo "🔍 Step 2: Testing MIR API connection..."
./ur_venv/bin/python3 -c "
from integrated_mir_ur_controller import IntegratedMirUrController
controller = IntegratedMirUrController()
if controller.test_mir_connection():
    print('✅ MIR API ready!')
else:
    print('❌ MIR connection failed')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SYSTEM READY FOR AUTOMATION!"
    echo "=" * 40
    echo ""
    echo "📋 Next steps:"
    echo "1. Run: ./ur_venv/bin/python3 integrated_mir_ur_controller.py"
    echo "2. Type: start"
    echo "3. Start your 'FYP moving test' mission on MIR"
    echo "4. Watch automatic UR operations trigger!"
    echo ""
    echo "🎯 When MIR reaches positions, UR will automatically:"
    echo "   P_start → pickup + compact"
    echo "   PL1 → home + dropoff1 + home + compact"  
    echo "   PL2 → home + dropoff2 + home + compact"
    echo "   PR1 → home + dropoff3_safe + home + compact"
    echo "   PR2 → home + dropoff4_safe + home + compact"
    echo ""
    echo "💡 Press Ctrl+C to stop automation, then:"
    echo "   kill $UR_PID  # to stop UR control system"
else
    echo "❌ Setup failed - stopping UR system"
    kill $UR_PID
fi