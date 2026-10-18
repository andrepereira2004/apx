import QtQuick
import Quickshell
import "file:/home/apx/.config/quickshell/apx" as Apx
ShellRoot {
 id: test
 property int step: 0
 property real previousWidth: 88
 property var samples: []
 FloatingWindow {
  visible: true; implicitWidth: 500; implicitHeight: 100
  Apx.MediaIsland {
   id: mediaIsland
   readonly property real availableWidth: 300
   transientProgress: 50; transientDetail: "50%"
                width: Math.min(showingTransient ? 88 : (selected ? 36 : 220), availableWidth) * presence
                Behavior on width { enabled: mediaIsland.presence === 1; NumberAnimation { duration: 300; easing.type: Easing.OutCubic } }
  }
 }
 function check(condition, message) { if (!condition) { console.error("FAIL " + message + " width=" + mediaIsland.width); Qt.exit(1) } }
 function stopReaders() {
  Apx.DesktopActivity.watchRestart.running = false
  Apx.DesktopActivity.watchProcess.running = false
  Apx.DesktopActivity.notificationsTimer.running = false
  Apx.DesktopActivity.timer.running = false
  Apx.DesktopActivity.readProcess.running = false
 }
 Component.onCompleted: {
  stopReaders()
  Apx.DesktopActivity.state = ({players: [], notifications: []})
  mediaIsland.transientActive = true
 }
 Timer {
  interval: 50; running: true; repeat: true
  onTriggered: {
   ++test.step
   if (test.step === 10) {
    test.check(Math.abs(mediaIsland.width - 88) < .1, "compact feedback settled")
    mediaIsland.transientActive = false
   }
   if (test.step > 10 && test.step < 18) {
    test.samples.push({step: test.step, width: mediaIsland.width, opacity: mediaIsland.opacity})
    test.check(mediaIsland.width <= test.previousWidth + .1, "exit never enlarges without playback")
    test.previousWidth = mediaIsland.width
   }
   if (test.step === 18) {
    test.check(mediaIsland.width < .1 && mediaIsland.presence === 0, "fully collapsed")
    Apx.DesktopActivity.state = ({players: [{name: "test", track_id: "/one", status: "Playing", title: "Test", length: 120, position: 10, sampled_at: Date.now()}], notifications: []})
   }
   if (test.step === 28) {
    test.check(Math.abs(mediaIsland.width - 220) < .1, "media settled")
    mediaIsland.transientActive = true
   }
   if (test.step === 38) {
    test.check(Math.abs(mediaIsland.width - 88) < .1, "media temporarily compact")
    mediaIsland.transientActive = false
   }
   if (test.step === 48) {
    test.check(Math.abs(mediaIsland.width - 220) < .1 && mediaIsland.presence === 1, "media width restored")
    console.log("EXIT_PASS " + JSON.stringify(test.samples)); Qt.quit()
   }
  }
 }
}
