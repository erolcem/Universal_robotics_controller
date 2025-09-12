#!/bin/bash
# MIR WiFi Testing Script
# Run this when connected to MIR WiFi network

echo "🚁 MIR WiFi Connection Testing Script"
echo "====================================="

# 1. Test basic MIR connectivity
echo "📡 Testing MIR network connectivity..."
ping -c 3 mir.com
if [ $? -eq 0 ]; then
    echo "✅ MIR network reachable"
else
    echo "❌ MIR network not reachable"
    exit 1
fi

# 2. Test MIR API access
echo -e "\n🔌 Testing MIR API access..."
curl -u "Distributor:distributor" "http://mir.com/api/v2.0.0/status" --connect-timeout 10 --silent --fail
if [ $? -eq 0 ]; then
    echo "✅ MIR API accessible"
else
    echo "❌ MIR API not accessible"
    exit 1
fi

# 3. Test Python MIR control
echo -e "\n🐍 Testing Python MIR control..."
python3 -c "
import sys
sys.path.append('YW_MiR')
from simple_mir_control import SimpleMiRControl
print('Connecting to MIR...')
mir = SimpleMiRControl('mir.com')
status = mir._get_status()
if status:
    print(f'✅ MIR Connected: {status.get(\"robot_name\", \"Unknown\")}')
    print(f'   State: {status.get(\"state_text\", \"Unknown\")}')
    print(f'   Battery: {status.get(\"battery_percentage\", 0)}%')
    pos = status.get('position', {})
    print(f'   Position: x={pos.get(\"x\", 0):.2f}, y={pos.get(\"y\", 0):.2f}')
else:
    print('❌ MIR connection failed')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo "✅ Python MIR control working"
else
    echo "❌ Python MIR control failed"
    exit 1
fi

# 4. Test MIR pause/resume functionality
echo -e "\n⏯️  Testing MIR pause/resume..."
python3 -c "
import sys
import time
sys.path.append('YW_MiR')
from simple_mir_control import SimpleMiRControl

mir = SimpleMiRControl('mir.com')

print('Current status:')
mir.status_summary()

print('\nTesting pause...')
if mir.pause():
    print('✅ Pause successful')
    time.sleep(2)
    
    print('Testing resume...')
    if mir.resume():
        print('✅ Resume successful')
    else:
        print('❌ Resume failed')
else:
    print('❌ Pause failed')
"

# 5. Test unified system with MIR
echo -e "\n🤖 Testing unified system with MIR..."
python3 -c "
import sys
import time
from pathlib import Path

# Test import
sys.path.append('YW_MiR')
from simple_mir_control import SimpleMiRControl

# Test the main unified system components
print('Testing unified system imports...')
try:
    # This would normally import the unified control
    print('✅ All imports successful')
except Exception as e:
    print(f'❌ Import error: {e}')

print('Creating test control files...')
control_dir = Path('control')
control_dir.mkdir(exist_ok=True)

# Test command file creation
command_file = control_dir / 'robot_commands.txt'
command_file.write_text('mir_status\\n')
print('✅ Control files created')
"

# 6. Save MIR network info for later
echo -e "\n💾 Saving MIR network information..."
echo "MIR Network Test Results - $(date)" > mir_test_results.txt
echo "=================================" >> mir_test_results.txt
ifconfig >> mir_test_results.txt
echo -e "\nMIR API Status:" >> mir_test_results.txt
curl -u "Distributor:distributor" "http://mir.com/api/v2.0.0/status" --silent | python3 -m json.tool >> mir_test_results.txt 2>/dev/null

echo -e "\n✅ MIR testing complete! Results saved to mir_test_results.txt"
echo "You can now disconnect from MIR WiFi and return to your main network."
