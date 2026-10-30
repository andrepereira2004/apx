from pathlib import Path
import shutil
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'config/environment-shell-v1/quickshell/apx/shell.qml'
class RadioFeedbackTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_immediate_feedback_stale_status_failure_and_confirmed_state(self):
        source=SOURCE.read_text()
        code=source[source.index('    function wifiDisplayPowered()'):source.index('    Process {\n        id: wifiPowerProcess')]
        script='''const assert=require('node:assert/strict');
let wifiPowerOverride=false,wifiPowerActive=true,wifiMessage='';
let hostState={wifi_powered:true,network_name:'test'},cancelled=0;
const hostStatusProcess={running:true};
const wifiPowerProcess={running:false};
function cancelWifiPassword(){cancelled++}
'''+code+'''
assert.equal(wifiDisplayPowered(),true);
toggleWifiPower();assert.equal(wifiDisplayPowered(),false);assert.equal(cancelled,1);
assert.equal(wifiPowerProcess.command.at(-1),'off');
// An old polling response cannot undo the pending click.
hostState={wifi_powered:true,network_name:'test'};
assert.equal(wifiDisplayPowered(),false);
toggleWifiPower();assert.equal(cancelled,1);
wifiPowerProcess.running=false;finishWifiPower(false);
assert.equal(wifiDisplayPowered(),true);assert.ok(wifiMessage.length);
toggleWifiPower();wifiPowerProcess.running=false;finishWifiPower(true);
assert.equal(wifiDisplayPowered(),false);assert.equal(hostState.network_name,null);
assert.equal(wifiPowerOverride,false);assert.equal(hostStatusProcess.running,true);
toggleWifiPower();assert.equal(wifiDisplayPowered(),true);assert.equal(wifiPowerProcess.command.at(-1),'on');
wifiPowerProcess.running=false;finishWifiPower(true);
assert.equal(hostState.wifi_powered,true);
'''
        result=subprocess.run(['node','-e',script],capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr)

    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_connected_signal_uses_only_measured_current_network(self):
        source=SOURCE.read_text()
        function=source[source.index('    function wifiCurrentSignal()'):source.index('    function wifiSignalBars(')]
        script='''const assert=require('node:assert/strict');
let active=true;
const wifiDisplayActive=()=>active;
let hostState={network_name:'current',network_details:[{ssid:'other',signal:100,security:'psk'},{ssid:'current',signal:72.6,security:'psk'}]};
'''+function+'''
assert.equal(wifiCurrentSignal(),73);
active=false;assert.equal(wifiCurrentSignal(),-1);active=true;
hostState.network_details=[{ssid:'current',signal:0,security:'unknown'}];assert.equal(wifiCurrentSignal(),-1);
hostState.network_details=[{ssid:'current',signal:0,security:'psk'}];assert.equal(wifiCurrentSignal(),0);
hostState.network_details=[{ssid:'current',signal:null,security:'psk'}];assert.equal(wifiCurrentSignal(),-1);
hostState.network_details=[{ssid:'current',signal:150,security:'psk'}];assert.equal(wifiCurrentSignal(),100);
hostState.network_details=[];assert.equal(wifiCurrentSignal(),-1);
'''
        result=subprocess.run(['node','-e',script],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
