from pathlib import Path
p=Path('audit/2026-10-20-controls-followup/validate-candidate.py');s=p.read_text();src=Path('config/environment-shell-v1/quickshell/apx/shell.qml').read_text();functions=src[src.index('                function stopWheel()'):src.index('                onEnabledChanged:',src.index('                function stopWheel()'))]
harness='''import QtQuick
import Quickshell
ShellRoot {
 id: test
 property real previous:400
 property int samples:0
 property int moved:0
 property bool sent:false
 Item {width:300;height:300
 Flickable {
  id:menuFlick;width:300;height:300;contentWidth:300;contentHeight:2000;contentY:400
'''+functions+'''
  SmoothedAnimation {
   id:menuWheelAnimation;target:menuFlick;property:"contentY"
   velocity:-1;duration:180;maximumEasingTime:90
   reversingMode:SmoothedAnimation.Immediate
  }
 }
 }
 Timer {interval:100;running:true;onTriggered:{menuFlick.scrollWheel(-12);test.sent=true}}
 Timer {interval:125;running:true;onTriggered:menuFlick.scrollWheel(-12)}
 Timer {interval:150;running:true;onTriggered:menuFlick.scrollWheel(-12)}
 Timer {interval:175;running:true;onTriggered:menuFlick.scrollWheel(-12)}
 Timer {interval:16;running:true;repeat:true;onTriggered:{
  if(!test.sent)return
  if(menuFlick.contentY<test.previous-.01 || menuFlick.contentY>520.1){console.error("Non-monotonic motion");Qt.exit(1)}
  if(menuFlick.contentY>test.previous+.01)test.moved++
  test.previous=menuFlick.contentY;test.samples++
 }}
 Timer {interval:240;running:true;onTriggered:{
  if(menuFlick.contentY<=430 || menuFlick.contentY>=520){console.error("No smooth trailing motion",menuFlick.contentY);Qt.exit(1)}
 }}
 Timer {interval:650;running:true;onTriggered:{
  if(Math.abs(menuFlick.contentY-520)>.1 || menuWheelAnimation.running || test.moved<8){console.error("Did not settle smoothly",menuFlick.contentY,test.moved);Qt.exit(1)}
  console.log("SMOOTH_PASS",test.moved,"moving frames");Qt.quit()
 }}
}'''
s=s.replace(' for path in [stage]+'," (stage/'smooth.qml').write_text("+repr(harness)+")\n for path in [stage]+",1).replace("for name in ['parse']:","for name in ['parse','smooth']:");p.write_text(s)
