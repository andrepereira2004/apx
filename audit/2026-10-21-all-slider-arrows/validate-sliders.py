from pathlib import Path
import os,shutil,subprocess
R=Path(__file__).resolve().parents[2]
s=(R/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
def block(start, offset=0):
 p=s.index(start, offset);b=s.index('{',p);depth=1;i=b+1
 while depth:
  if s[i]=='{':depth+=1
  elif s[i]=='}':depth-=1
  i+=1
 return s[p:i]
component=block('    component MenuSlider: Slider')
functions='\n'.join(block('    function '+n) for n in ['setTrackpadGesture(kind, value)', 'flushTrackpadGestures()', 'readTrackpadGestures(text)', 'setMouseSensitivity(value)', 'flushMouseSensitivity()', 'readMouseSensitivity(text)', 'commitMicrophoneVolume(value)', 'dispatchMicrophoneVolume()'])
cards=[]
for n in ['trackpadScrollCard','trackpadWorkspacesCard']:
 p=s.index('id: '+n);b=s.rfind('Rectangle {',0,p);cards.append(block('Rectangle {',b))
qml='''import QtQuick
import QtQuick.Controls
import QtTest
Item {
 id: root; width: 420; height: 300
 property bool menuKeyboardNavigation: false
 property var editingMenuSlider: null
 property color cyan: "cyan"
 property color textMain: "white"
 property color controlButtonSurface: "#222222"
 property color controlButtonOutline: "#555555"
 property int menuBodySize: 14
 property var pointerDevices: ({trackpad:{available:true,enabled:true}})
 property var trackpadGestures: ({scroll:55,workspaces:100})
 property var calls: []
 property real pendingMouseSensitivity: NaN
 property int mouseSensitivity: 0
 property string mouseSensitivityError: ""
 property int microphonePending: -1
 property int microphoneVolume: 50
 property bool microphoneMuted: false
 property string microphoneText: "50%"
 function showHotkeyOsd(icon,title,detail,progress) {}
 QtObject { id: mouseSensitivityProcess; property bool running: false; property var command: [] }
 QtObject { id: mouseSensitivityStatusProcess; property bool running: false; property var command: [] }
 QtObject { id: microphoneSetProcess; property bool running: false; property var command: [] }
 property int testVolume: 50
 property int testBrightness: 50
 MenuSlider { id: sound; x:0; y:170; width:300; height:24; from:0; to:100; value:root.testVolume; onKeyboardValueChanged: n => root.testVolume=n }
 MenuSlider { id: brightness; x:0; y:200; width:300; height:24; from:5; to:100; value:root.testBrightness; onKeyboardValueChanged: n => root.testBrightness=n }
 MenuSlider { id: mouse; x:0; y:230; width:300; height:24; from:-100; to:100; value:root.mouseSensitivity; onKeyboardValueChanged: n => root.setMouseSensitivity(n) }
 ControlSlider { id: opacityControl; x:0; y:260; width:300; height:24; from:0; to:100; value:50; property int moves:0; onMoved: moves++ }

 property var pendingTrackpadGestures: ({})
 property string trackpadGesturesError: ""
 QtObject { id: appearance; property int menuLabelInset: 54; property string fontFamily: "sans-serif" }
 QtObject { id: trackpadGesturesProcess; property bool running: false; property var command: [] }
 QtObject { id: trackpadGesturesStatusProcess; property bool running: false; property var command: [] }
 function navigateGenericMenu(event) {}
 FUNCTIONS
 COMPONENT
 Column { width: parent.width; spacing: 10
 CARDS
 }
 TestCase {
  name: "IndependentGestureSliders"; when: windowShown
  function init() {
   trackpadGesturesProcess.running=false;trackpadGesturesStatusProcess.running=false
   trackpadGesturesProcess.command=[];root.pendingTrackpadGestures={};root.trackpadGestures={scroll:55,workspaces:100};wait(10)
  }
  function test_scroll_drag_keeps_released_value() {
   mousePress(trackpadScrollSlider,60,8);mouseMove(trackpadScrollSlider,240,8,40);mouseRelease(trackpadScrollSlider,240,8)
   verify(root.trackpadGestures.scroll>100);compare(root.trackpadGestures.workspaces,100)
   compare(trackpadGesturesProcess.command[2],"scroll")
   compare(Number(trackpadGesturesProcess.command[3]),root.trackpadGestures.scroll)
  }
  function test_workspace_drag_does_not_change_scroll() {
   mousePress(trackpadWorkspacesSlider,100,8);mouseMove(trackpadWorkspacesSlider,250,8,40);mouseRelease(trackpadWorkspacesSlider,250,8)
   verify(root.trackpadGestures.workspaces>100);compare(root.trackpadGestures.scroll,55)
   compare(trackpadGesturesProcess.command[2],"workspaces")
  }
  function test_direct_arrows_and_shift() {
   trackpadScrollSlider.forceActiveFocus()
   const initial=Math.round(trackpadScrollSlider.value)
   keyClick(Qt.Key_Right)
   compare(Math.round(trackpadScrollSlider.value),initial+1)
   keyClick(Qt.Key_Right,Qt.ShiftModifier)
   compare(Math.round(trackpadScrollSlider.value),initial+6)
   compare(root.trackpadGestures.workspaces,100)
  }
  function test_pending_keys_preserve_latest_value() {
   trackpadScrollSlider.forceActiveFocus()
   for(let i=0;i<12;i++) keyClick(Qt.Key_Right)
   const desired=root.trackpadGestures.scroll
   verify(root.pendingTrackpadGestures.scroll!==undefined)
   root.readTrackpadGestures(JSON.stringify({scroll:57,workspaces:100}))
   compare(root.trackpadGestures.scroll,desired)
   trackpadGesturesProcess.running=false;root.flushTrackpadGestures()
   compare(Number(trackpadGesturesProcess.command[3]),desired)
  }
  function test_sound_and_brightness_arrows() {
   root.testVolume=50;root.testBrightness=50
   sound.forceActiveFocus();keyClick(Qt.Key_Right);compare(root.testVolume,51)
   keyClick(Qt.Key_Left,Qt.ShiftModifier);compare(root.testVolume,46)
   brightness.forceActiveFocus();keyClick(Qt.Key_Right);compare(root.testBrightness,51)
   root.testBrightness=5;keyClick(Qt.Key_Left);compare(root.testBrightness,5)
   root.testVolume=100;sound.forceActiveFocus();keyClick(Qt.Key_Right);compare(root.testVolume,100)
  }
  function test_mouse_held_keys_queue_last_value() {
   root.mouseSensitivity=0;root.pendingMouseSensitivity=NaN
   mouseSensitivityProcess.running=false;mouseSensitivityStatusProcess.running=false
   mouse.forceActiveFocus()
   for(let i=0;i<12;i++) keyClick(Qt.Key_Right)
   compare(root.mouseSensitivity,12);compare(root.pendingMouseSensitivity,12)
   root.readMouseSensitivity("1");compare(root.mouseSensitivity,12)
   mouseSensitivityProcess.running=false;root.flushMouseSensitivity()
   compare(mouseSensitivityProcess.command[2],"12")
  }
  function test_microphone_latest_write_survives_busy_process() {
   microphoneSetProcess.running=false;root.microphonePending=-1
   root.commitMicrophoneVolume(51);root.commitMicrophoneVolume(52);root.commitMicrophoneVolume(53)
   compare(root.microphonePending,53);compare(root.microphoneVolume,53)
   microphoneSetProcess.running=false;root.dispatchMicrophoneVolume()
   compare(microphoneSetProcess.command[5],"53%")
  }
  function test_opacity_keys_emit_updates() {
   opacityControl.value=50;opacityControl.moves=0
   opacityControl.forceActiveFocus();keyClick(Qt.Key_Right);compare(opacityControl.value,51)
   keyClick(Qt.Key_Left,Qt.ShiftModifier);compare(opacityControl.value,46)
   compare(opacityControl.moves,2)
  }
  function test_ranges_and_normalization() {
   compare(trackpadScrollSlider.from,0);compare(trackpadScrollSlider.to,100)
   compare(trackpadWorkspacesSlider.from,0);compare(trackpadWorkspacesSlider.to,100)
   root.setTrackpadGesture("scroll",0);compare(root.trackpadGestures.scroll,25)
   root.setTrackpadGesture("scroll",100);compare(root.trackpadGestures.scroll,200)
   root.setTrackpadGesture("workspaces",100);compare(root.trackpadGestures.workspaces,200)
  }
 }
}
'''.replace('FUNCTIONS',functions).replace('COMPONENT',component).replace('CARDS','\n'.join(cards)).replace('Appearance','appearance')
home=Path('/var/lib/apx/environments/hytale/home/apx');stage=home/'.cache/apx-all-sliders-validation';stage.mkdir();p=stage/'tst_sliders.qml';p.write_text(qml);(Path(__file__).parent/'tst_sliders.qml').write_text(qml)
control=stage/'ControlSlider.qml';control.write_text((R/'config/environment-shell-v1/quickshell/apx/ControlSlider.qml').read_text().replace('Appearance.iconColor','"white"'))
meta=home.stat()
for f in [stage,p,control]:os.chown(f,meta.st_uid,meta.st_gid)
try:
 result=subprocess.run(['python',str(R/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=20)
 (Path(__file__).parent/'sliders.log').write_text(result.stdout+result.stderr);print(result.stdout+result.stderr);assert result.returncode==0
finally:shutil.rmtree(stage)
