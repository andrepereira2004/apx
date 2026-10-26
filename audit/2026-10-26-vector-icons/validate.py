from pathlib import Path
import shutil,os,subprocess,json
r=Path(__file__).resolve().parents[2];a=Path(__file__).parent
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text())
home=Path('/proc')/str(state['pid'])/'root/home/apx';stage=home/'.cache/apx-vector-icon-check';stage.mkdir(exist_ok=True)
b=r/'config/environment-shell-v1/quickshell/apx'
for name in ['ControlIcon.qml','LucidePaths.js']:shutil.copy2(b/name,stage/name)
shutil.copy2(a/'ControlIcon.before.qml',stage/'OldIcon.qml')
(stage/'icons/lucide').mkdir(parents=True,exist_ok=True)
for p in (b/'icons/lucide').glob('*.svg'):shutil.copy2(p,stage/'icons/lucide'/p.name)
(stage/'tst_icons.qml').write_text('''import QtQuick
import QtQuick.Shapes
import "LucidePaths.js" as Paths
import QtTest
Rectangle {
 id: root; width: 600; height: 240; color: "#1b1d26"
 Repeater {
  model: ["wifi", "bluetooth", "bluetooth-off", "settings", "sun", "calendar-days", "cpu", "pause"]
  delegate: Item {
   required property string modelData
   required property int index
   x: 20 + index * 72; y: 30; width: 32; height: 180
   Text {text: "old";color:"white";y:0}
   OldIcon {x:8;y:30;width:14;height:14;source:"icons/lucide/"+parent.modelData+".svg";tint:"#d5d8e5"}
   Text {text: "vector";color:"white";y:65}
   ControlIcon {x:8;y:95;width:14;height:14;source:"icons/lucide/"+parent.modelData+".svg";tint:"#d5d8e5"}
   ControlIcon {x:4;y:135;width:24;height:24;source:"icons/lucide/"+parent.modelData+".svg";tint:"#d5d8e5"}
  }
 }
 TestCase {
  name:"VectorIcons";when:windowShown
  function test_all_paths() {
   wait(250)
   grabImage(root).save("/home/apx/.cache/apx-vector-icon-check/comparison.png")
   var factory = Qt.createComponent("ControlIcon.qml")
   compare(factory.status, Component.Ready)
   var names = Object.keys(Paths.paths)
   compare(names.length, 97)
   for (var i = 0; i < names.length; i++) {
    var item = factory.createObject(root, {source: Qt.resolvedUrl("icons/lucide/" + names[i] + ".svg"), width:20, height:20, tint:"#ff3366"})
    verify(item !== null, names[i])
    verify(item.vectorPath.length > 0, names[i])
    compare(item.lucideName, names[i])
    compare(item.children[0].preferredRendererType, Shape.CurveRenderer)
    compare(item.children[0].data[0].strokeColor.toString(), "#ff3366")
    compare(item.children[1].visible, false)
    item.destroy()
   }
  }
 }
}''')
stat=home.stat()
for p in [stage]+list(stage.rglob('*')):os.chown(p,stat.st_uid,stat.st_gid)
cmd=['python3',str(r/'audit/2026-10-16-lucide-bar/session-command.py'),'/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/apx-vector-icon-check','-o','-,txt']
p=subprocess.run(cmd,capture_output=True,text=True,timeout=25)
(a/'validation.log').write_text(p.stdout+p.stderr)
print(p.stdout+p.stderr)
if (stage/'comparison.png').exists():shutil.copy2(stage/'comparison.png',a/'comparison.png')
assert p.returncode==0
