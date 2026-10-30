from pathlib import Path
import json,subprocess,os,re
r=Path(__file__).resolve().parents[2];a=Path(__file__).parent
shell=(r/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text();start=shell.index('id: mediaIsland');end=shell.index('                transientActive:',start);block=shell[start:end]
geometry='\n'.join(line for line in block.splitlines() if line.strip().startswith(('width:','Behavior on width')))
harness='''import QtQuick
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
'''+geometry+'''
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
'''
(a/'exit-harness.qml').write_text(harness)
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());home=Path('/var/lib/apx/environments')/state['name']/'home/apx';p=home/'.cache/apx-osd-exit-test.qml';assert not p.exists();p.write_text(harness);st=home.stat();os.chown(p,st.st_uid,st.st_gid)
try:
 result=subprocess.run(['python',str(r/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','quickshell','--path','/home/apx/.cache/'+p.name,'--no-color'],text=True,capture_output=True,timeout=10)
 (a/'exit-validation.log').write_text(result.stdout+result.stderr);print(result.stdout+result.stderr)
 assert result.returncode==0 and 'EXIT_PASS' in result.stdout+result.stderr
finally:p.unlink()
