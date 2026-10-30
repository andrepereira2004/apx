from pathlib import Path
import shutil
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'config/environment-shell-v1/quickshell/apx/shell.qml'
class BluetoothMenuTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_device_groups_are_unique_disjoint_and_respect_radio_power(self):
        s=SOURCE.read_text();functions=s[s.index('    function bluetoothDevicesUnique()'):s.index('    function revealBluetoothForm()')]
        script='''const assert=require('node:assert/strict');
let powered=true;
const bluetoothDisplayPowered=()=>powered;
const hostState={bluetooth_devices:[{address:'A',paired:true,connected:true},{address:'B',paired:true,connected:false},{address:'C',paired:false,connected:false},{address:'A',paired:true,connected:true},{address:'D',paired:false,connected:true}]};
'''+functions+'''
assert.deepEqual(bluetoothConnectedDevices().map(x=>x.address),['A','D']);
assert.deepEqual(bluetoothKnownDevices().map(x=>x.address),['B']);
assert.deepEqual(bluetoothAvailableDevices().map(x=>x.address),['C']);
powered=false;
assert.deepEqual(bluetoothConnectedDevices(),[]);assert.deepEqual(bluetoothKnownDevices(),[]);assert.deepEqual(bluetoothAvailableDevices(),[]);
'''
        r=subprocess.run(['node','-e',script],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)

    @unittest.skipUnless(shutil.which('node'),'Node required')
    def test_pairing_prompt_is_brought_into_view_before_pin_focus(self):
        s=SOURCE.read_text();function=s[s.index('    function revealBluetoothForm()'):s.index('    function applyBluetoothPairResult(')]
        script='''const assert=require('node:assert/strict');
let queued,focused=0,stopped=0;
const Qt={callLater(fn){queued=fn}};
const menuFlick={contentY:500,stopWheel(){stopped++}};
const root={bluetoothPairPhase:'needs-response',bluetoothPairChallenge:'pin'};
const bluetoothPinInput={forceActiveFocus(){focused++}};
'''+function+'''
revealBluetoothForm();queued();assert.equal(menuFlick.contentY,0);assert.equal(stopped,1);assert.equal(focused,1);
root.bluetoothPairChallenge='confirm';menuFlick.contentY=500;revealBluetoothForm();queued();assert.equal(menuFlick.contentY,0);assert.equal(focused,1);
'''
        r=subprocess.run(['node','-e',script],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr)
