# MIR WiFi Testing Instructions

## 🚁 **COMPLETE MIR TESTING PLAN**

Since you can only connect to MIR via WiFi, here's everything to test at once:

### **BEFORE DISCONNECTING FROM MAIN NETWORK:**

1. **Prepare the test environment:**
   ```bash
   cd /home/erolc/Projects/ursim_pipeline
   ls -la test_mir_wifi*
   # You should see:
   # test_mir_wifi.sh
   # test_mir_wifi_comprehensive.py
   ```

### **WHEN CONNECTED TO MIR WIFI:**

2. **Run the comprehensive test:**
   ```bash
   python3 test_mir_wifi_comprehensive.py
   ```

   This will test:
   - ✅ MIR network connectivity
   - ✅ MIR API access
   - ✅ Python MIR control import
   - ✅ MIR pause/resume functionality  
   - ✅ Direct API requests
   - ✅ Unified system components
   - ✅ Save MIR configuration for later

3. **Alternative bash script test:**
   ```bash
   ./test_mir_wifi.sh
   ```

4. **Manual verification commands:**
   ```bash
   # Test network
   ping -c 3 mir.com
   
   # Test API directly
   curl -u "Distributor:distributor" "http://mir.com/api/v2.0.0/status"
   
   # Test Python import
   python3 -c "import sys; sys.path.append('YW_MiR'); from simple_mir_control import SimpleMiRControl; print('Import OK')"
   ```

### **EXPECTED OUTPUTS:**

**✅ SUCCESS - You should see:**
```
🚁 MIR WiFi Comprehensive Test
=============================
🔌 Testing MIR Connection...
✅ MIR Connection Successful!
   Robot Name: MiR_R###
   State: Ready / Executing / Paused
   Battery: XX.X%
   Position: x=X.XX, y=X.XX, θ=XXX.X°

⏯️  Testing MIR Control...
Initial State: Ready
Testing pause...
✅ Pause command successful
State after pause: Paused
Testing resume...
✅ Resume command successful
State after resume: Ready

🌐 Testing MIR API Directly...
✅ Direct API access successful
   Robot: MiR_R###
   State ID: 3
✅ Found X missions
✅ Mission queue has X items

🤖 Testing Unified System with MIR...
✅ Control directory ready
✅ Test commands written
✅ Status file created

💾 Saving MIR Configuration...
✅ Configuration saved to mir_wifi_config.json

📊 Test Results Summary:
✅ Connection: PASS
✅ Control: PASS
✅ Api: PASS
✅ Unified: PASS
✅ Config: PASS

🏁 Overall: 5/5 tests passed
✅ MIR WiFi testing successful!
```

### **FILES CREATED DURING TEST:**
- `mir_wifi_config.json` - MIR connection details
- `integration_test_commands.txt` - Commands to run later
- `control/robot_commands.txt` - Test commands
- `control/robot_status.json` - Test status file

### **AFTER RECONNECTING TO MAIN NETWORK:**

5. **Test the complete unified system:**
   ```bash
   # Start unified system with both UR and MIR
   python3 unified_robot_control.py --ur-ip 192.168.1.6 --mir-ip mir.com
   ```

6. **In the interactive interface, test these commands:**
   ```
   🤖 unified> status          # Show both UR and MIR status
   🤖 unified> mir status      # MIR-specific status
   🤖 unified> collab home     # UR function with MIR auto-pause
   🤖 unified> mir pause       # Manual MIR pause
   🤖 unified> add square 0.2  # UR function without MIR pause
   🤖 unified> mir resume      # Manual MIR resume
   ```

7. **Test CLI tool (in separate terminal):**
   ```bash
   python3 unified_robot_cli.py system --status
   python3 unified_robot_cli.py mir --status
   python3 unified_robot_cli.py collab pickup --speed 0.15
   python3 unified_robot_cli.py mir --pause
   python3 unified_robot_cli.py mir --resume
   ```

8. **Test file-based control:**
   ```bash
   echo "mir_status" > control/robot_commands.txt
   echo "collab pickup 0.1" >> control/robot_commands.txt
   cat control/robot_response.txt  # Check responses
   ```

### **TROUBLESHOOTING:**

**❌ If MIR connection fails:**
- Check WiFi connection: `ping mir.com`
- Verify MIR IP address (might not be mir.com)
- Try: `nmap -sP 192.168.1.0/24` to find MIR IP

**❌ If API access fails:**
- Check credentials (default: Distributor/distributor)
- Verify API is enabled on MIR web interface
- Try web interface: `http://mir.com/` in browser

**❌ If Python import fails:**
- Check: `pip3 install requests`
- Verify YW_MiR directory exists
- Test: `ls -la YW_MiR/simple_mir_control.py`

### **KEY INFORMATION TO COLLECT:**

1. **MIR Network Details:**
   - IP address (if not mir.com)
   - Robot name and model
   - Current firmware version
   - Available missions

2. **MIR Status Information:**
   - Battery level
   - Current position
   - State (Ready/Executing/Paused/Error)
   - Mission queue status

3. **API Capabilities:**
   - Available endpoints
   - Authentication working
   - Pause/resume responsiveness
   - Mission control capabilities

### **INTEGRATION VERIFICATION:**

After testing on MIR WiFi, you'll be able to:

✅ **Collaborative UR + MIR Operations:**
- UR functions automatically pause MIR
- Manual MIR control independent of UR
- Unified status monitoring
- External program control

✅ **Real-world Workflow:**
```bash
# Example collaborative assembly sequence
python3 unified_robot_control.py

🤖 unified> collab pickup 0.1    # Slow pickup, MIR pauses
🤖 unified> add square 0.3        # Fast pattern, MIR continues
🤖 unified> collab dropoff 0.1    # Slow dropoff, MIR pauses
🤖 unified> status                # Verify all systems
```

## 🎯 **SUCCESS CRITERIA:**

✅ MIR responds to pause/resume commands
✅ Python control module works
✅ API access functional
✅ Configuration saved for offline use
✅ Integration commands generated

**Once you complete this testing, you'll have a fully integrated UR + MIR collaborative robotics system!**
