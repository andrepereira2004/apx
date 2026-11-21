from pathlib import Path
import subprocess, json, os
repo=Path(__file__).resolve().parents[2]
active=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
folder=Path('/var/lib/apx/environments')/active['name']/'home/apx/.local/state/apx-wallpaper-zoom-test';folder.mkdir(exist_ok=True);folder.chmod(0o755)
source=(repo/'config/environment-shell-v1/quickshell/apx/PersonalizationPanel.qml').read_text()
block=source[source.index('    property int pendingWallpaperZoom:'):source.index('    spacing: 8')]
(folder/'qmldir').write_text('module ZoomTest\nsingleton Appearance 1.0 Appearance.qml\n')
(folder/'Appearance.qml').write_text('''pragma Singleton
import QtQuick
QtObject {
 property bool busy: false
 property int wallpaperZoom: 100
 property int wallpaperOffsetX: 0
 property int wallpaperOffsetY: 0
 property int sentZoom: -1
 function change(op, value) { if (op === "wallpaper-zoom") sentZoom = Number(value); busy = true }
 function complete() { wallpaperZoom = sentZoom; busy = false }
}
''')
(folder/'tst_zoom.qml').write_text('''import QtQuick
import QtTest
import "."
TestCase {
 name: "WallpaperZoom"
 Column {
 id: panel
'''+block+'''
 }
 function test_rapid_changes_during_delayed_save() {
  panel.pendingWallpaperZoom = 120
  // Restart the real debounce timer through its child object.
  var timers = panel.resources
  var zoomTimer = null
  for (var i=0;i<timers.length;i++) if (timers[i].interval === 250) zoomTimer = timers[i]
  verify(zoomTimer !== null)
  zoomTimer.restart()
  tryCompare(Appearance, "busy", true, 1000)
  compare(panel.pendingWallpaperZoom, 120) // Must not jump to the old 100%.
  panel.pendingWallpaperZoom = 160
  zoomTimer.restart()
  Appearance.complete()
  compare(panel.pendingWallpaperZoom, 160) // Old completion must not discard newer input.
  tryCompare(Appearance, "busy", true, 1000)
  compare(Appearance.sentZoom, 160)
  compare(panel.pendingWallpaperZoom, 160)
  Appearance.complete()
  compare(panel.pendingWallpaperZoom, -1)
  compare(Appearance.wallpaperZoom, 160)
 }
}
''')
for path in folder.iterdir(): path.chmod(0o644)
r=subprocess.run(['nsenter','-t',str(active['pid']),'-U','-m','-u','-i','-n','-p','-r','-S','1000','-G','1000','env','HOME=/home/apx','XDG_RUNTIME_DIR=/run/apx/session-1000','QT_QUICK_BACKEND=software','QT_FORCE_STDERR_LOGGING=1','/usr/lib/qt6/bin/qmltestrunner','-platform','offscreen','-input','/home/apx/.local/state/apx-wallpaper-zoom-test','-o','-,txt'],capture_output=True,text=True)
print(r.stdout);print(r.stderr);raise SystemExit(r.returncode)
