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
cards=[]
for n in ['trackpadScrollCard','trackpadWorkspacesCard']:
 p=s.index('id: '+n);b=s.rfind('Rectangle {',0,p);cards.append(block('Rectangle {',b))
qml='''import QtQuick
import QtQuick.Controls
import QtTest
Item {
 id: root; width: 420; height: 220
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
 QtObject { id: appearance; property int menuLabelInset: 54; property string fontFamily: "sans-serif" }
 QtObject { id: trackpadGesturesProcess; property bool running: false }
 QtObject { id: trackpadGesturesStatusProcess; property bool running: false }
 function navigateGenericMenu(event) {}
 function setTrackpadGesture(kind,value) {
  const next = {scroll:trackpadGestures.scroll,workspaces:trackpadGestures.workspaces}
  next[kind]=Math.round(value);trackpadGestures=next;calls.push({kind:kind,value:Math.round(value)})
 }
 COMPONENT
 Column { width: parent.width; spacing: 10
 CARDS
 }
 TestCase {
  name: "IndependentGestureSliders"; when: windowShown
  function init() { root.calls=[];root.trackpadGestures={scroll:55,workspaces:100};wait(10) }
  function test_scroll_drag_keeps_released_value() {
   mousePress(trackpadScrollSlider,60,8);mouseMove(trackpadScrollSlider,240,8,40);mouseRelease(trackpadScrollSlider,240,8)
   compare(root.calls.length,1);compare(root.calls[0].kind,"scroll")
   verify(root.trackpadGestures.scroll>100);compare(root.trackpadGestures.workspaces,100)
   compare(Math.round(trackpadScrollSlider.value),root.trackpadGestures.scroll)
  }
  function test_workspace_drag_does_not_change_scroll() {
   mousePress(trackpadWorkspacesSlider,100,8);mouseMove(trackpadWorkspacesSlider,250,8,40);mouseRelease(trackpadWorkspacesSlider,250,8)
   compare(root.calls.length,1);compare(root.calls[0].kind,"workspaces")
   verify(root.trackpadGestures.workspaces>100);compare(root.trackpadGestures.scroll,55)
  }
  function test_keyboard_controls_remain_independent() {
   trackpadScrollSlider.keyboardValueChanged(75)
   compare(root.trackpadGestures.scroll,75);compare(root.trackpadGestures.workspaces,100)
   trackpadWorkspacesSlider.keyboardValueChanged(120)
   compare(root.trackpadGestures.scroll,75);compare(root.trackpadGestures.workspaces,120)
  }
 }
}
'''.replace('COMPONENT',component).replace('CARDS','\n'.join(cards)).replace('Appearance','appearance')
home=Path('/var/lib/apx/environments/hytale/home/apx');stage=home/'.cache/apx-gesture-sliders-validation';stage.mkdir();p=stage/'tst_sliders.qml';p.write_text(qml);(Path(__file__).parent/'tst_sliders.qml').write_text(qml)
meta=home.stat()
for f in [stage,p]:os.chown(f,meta.st_uid,meta.st_gid)
try:
 result=subprocess.run(['python',str(R/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=20)
 (Path(__file__).parent/'sliders.log').write_text(result.stdout+result.stderr);print(result.stdout+result.stderr);assert result.returncode==0
finally:shutil.rmtree(stage)
