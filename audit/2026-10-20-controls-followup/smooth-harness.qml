import QtQuick
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
                property real wheelPosition: 0
                property real wheelDestination: 0
                property bool wheelAnimating: false
                onWheelPositionChanged: if (wheelAnimating) contentY = wheelPosition
                function stopWheel() {
                    wheelAnimating = false
                    menuWheelAnimation.stop()
                    cancelFlick()
                }
                function scrollWheel(delta) {
                    if (!delta) return
                    cancelFlick()
                    if (!menuWheelAnimation.running) {
                        wheelAnimating = false
                        wheelPosition = contentY
                        wheelDestination = contentY
                    }
                    wheelDestination = Math.max(0, Math.min(Math.max(0, contentHeight - height), wheelDestination - delta * 2.5))
                    wheelAnimating = true
                    wheelPosition = wheelDestination
                }
                onEnabledChanged: if (!enabled) stopWheel()
                onContentHeightChanged: stopWheel()
                onDraggingChanged: if (dragging) stopWheel()
                Behavior on wheelPosition {
                    enabled: menuFlick.wheelAnimating
                    SmoothedAnimation {
                        id: menuWheelAnimation
                        velocity: -1; duration: 160; maximumEasingTime: 80
                        reversingMode: SmoothedAnimation.Immediate
                    }
                }

 }
 }
 Timer {interval:100;running:true;onTriggered:{menuFlick.scrollWheel(-12);test.sent=true}}
 Timer {interval:125;running:true;onTriggered:menuFlick.scrollWheel(-12)}
 Timer {interval:150;running:true;onTriggered:menuFlick.scrollWheel(-12)}
 Timer {interval:175;running:true;onTriggered:menuFlick.scrollWheel(-12)}
 Timer {interval:16;running:true;repeat:true;onTriggered:{
  if(!test.sent)return
  if(menuFlick.contentY<test.previous-.01 || menuFlick.contentY>520.1){console.error("Non-monotonic motion");Qt.exit(1);return}
  if(menuFlick.contentY>test.previous+.01)test.moved++
  test.previous=menuFlick.contentY;test.samples++
 }}
 Timer {interval:240;running:true;onTriggered:{
  if(menuFlick.contentY<=400 || menuFlick.contentY>=520){console.error("No smooth trailing motion",menuFlick.contentY);Qt.exit(1);return}
 }}
 Timer {interval:650;running:true;onTriggered:{
  if(Math.abs(menuFlick.contentY-520)>.1 || menuWheelAnimation.running || test.moved<8){console.error("Did not settle smoothly",menuFlick.contentY,test.moved);Qt.exit(1);return}
  console.log("SMOOTH_PASS",test.moved,"moving frames");Qt.quit()
 }}
}