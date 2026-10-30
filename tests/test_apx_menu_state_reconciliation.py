"""Polling must preserve UI models while real changes still propagate."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
QML = ROOT / 'config/environment-shell-v1/quickshell/apx'


def function(source, signature):
    return source.split(signature + ' {', 1)[1].split('\n    }', 1)[0]


@unittest.skipUnless(shutil.which('node'), 'Node required')
class ReconciliationTests(unittest.TestCase):
    def run_js(self, code):
        result = subprocess.run(['node', '-e', "const assert=require('node:assert/strict');\n" + code], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_appearance_preserves_identity_and_accepts_changes(self):
        body = function((QML / 'Appearance.qml').read_text(), 'function acceptReport(text)')
        self.run_js("""
let state={effective_icon_color:'#d9dcea',opacity:{menus:95}}, error='';
function acceptReport(text) {""" + body + """}
let original=state;
for(let i=0;i<100;i++) acceptReport(JSON.stringify(original));
assert.equal(state,original);
acceptReport(JSON.stringify({...original,opacity:{menus:90}}));
assert.notEqual(state,original);assert.equal(state.opacity.menus,90);
original=state;acceptReport('{broken');assert.equal(state,original);
acceptReport(JSON.stringify({effective_icon_color:'invalid'}));assert.equal(state,original);
""")

    def test_notifications_do_not_replace_player_models_or_skip_feedback(self):
        body = function((QML / 'DesktopActivity.qml').read_text(), 'function accept(text)')
        self.run_js("""
let state={players:[],notifications:[],active_notifications:0}, clock=0;
let playbackChecks=0,seekChecks=0;
function settlePlaybackFeedback(){playbackChecks++;}
function settleSeekFeedback(){seekChecks++;}
function accept(text) {""" + body + """}
let original=state;
for(let i=0;i<100;i++) accept(JSON.stringify({notifications:[],active_notifications:0}));
assert.equal(state,original);assert.equal(playbackChecks,100);assert.equal(seekChecks,100);
accept(JSON.stringify({notifications:[{id:1,title:'New'}],active_notifications:1}));
assert.notEqual(state,original);assert.equal(state.players,original.players);
assert.equal(state.active_notifications,1);
original=state;accept('{broken');assert.equal(state,original);
""")

    def test_host_status_keeps_models_and_still_settles_pending_actions(self):
        source=(QML/'shell.qml').read_text()
        body=source.split('id: hostStatusProcess',1)[1].split('onStreamFinished: {',1)[1].split('\n            }\n        }',1)[0]
        self.run_js("""
const root={hostState:{network_name:'wifi',bluetooth_powered:true,bluetooth_devices:[]},
 bluetoothPairPhase:'',wifiTogglePhase:'connecting',wifiOptimisticOverride:true,
 bluetoothPowerPhase:'powering',bluetoothPowerActive:true,bluetoothPowerOverride:true,
 bluetoothDevicePendingAddress:'',bluetoothPairAddress:''};
const bluetoothDeviceActionProcess={running:false};
function accept(text) {"""+body+"""}
let original=root.hostState;
for(let i=0;i<100;i++) accept(JSON.stringify(original));
assert.equal(root.hostState,original);assert.equal(root.wifiTogglePhase,'');
assert.equal(root.bluetoothPowerPhase,'');assert.equal(root.bluetoothPowerOverride,false);
accept(JSON.stringify({...original,network_name:'other'}));
assert.notEqual(root.hostState,original);assert.equal(root.wifiLastNetwork,'other');
""")
