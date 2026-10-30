from pathlib import Path
import subprocess,json,os,shutil
r=Path(__file__).resolve().parents[2];a=Path(__file__).parent
state=json.loads(Path('/run/apx/active-graphical-environment-v1.json').read_text());home=Path('/proc')/str(state['pid'])/'root/home/apx';stage=home/'.cache/apx-original-svg-check';stage.mkdir(exist_ok=True)
b=r/'config/environment-shell-v1/quickshell/apx'
shutil.copy2(b/'ControlIcon.qml',stage/'OldIcon.qml')
(stage/'icons/lucide').mkdir(parents=True,exist_ok=True)
for p in (b/'icons/lucide').glob('*.svg'):shutil.copy2(p,stage/'icons/lucide'/p.name)
(stage/'tst_icons.qml').write_text('''import QtQuick
import QtQuick.Controls.impl as Impl
import QtTest
Rectangle {
 id:root;width:600;height:250;color:"#1b1d26"
 Repeater {
  model:["wifi","bluetooth","bluetooth-off","settings","sun","calendar-days","cpu","pause"]
  delegate:Item {
   required property string modelData
   required property int index
   x:20+index*72;y:10;width:32;height:230
   OldIcon {x:8;y:20;width:14;height:14;source:"icons/lucide/"+parent.modelData+".svg";tint:"#d5d8e5"}
   Impl.IconImage {x:8;y:70;width:14;height:14;source:"icons/lucide/"+parent.modelData+".svg";color:"#d5d8e5";sourceSize:Qt.size(14,14);smooth:true}
   Impl.IconImage {x:8;y:120;width:14;height:14;source:"icons/lucide/"+parent.modelData+".svg";color:"#d5d8e5";sourceSize:Qt.size(28,28);smooth:true}
   Impl.IconImage {x:8;y:170;width:14;height:14;source:"icons/lucide/"+parent.modelData+".svg";color:"#d5d8e5";sourceSize:Qt.size(56,56);smooth:true;mipmap:true}
  }
 }
 TestCase {
  name:"OriginalSvgResolution";when:windowShown
  function test_capture() {wait(200);grabImage(root).save("/home/apx/.cache/apx-original-svg-check/comparison.png")}
 }
}''')
stat=home.stat()
for p in [stage]+list(stage.rglob('*')):os.chown(p,stat.st_uid,stat.st_gid)
cmd=['python3',str(r/'audit/2026-10-16-lucide-bar/session-command.py'),'/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/apx-original-svg-check','-o','-,txt']
p=subprocess.run(cmd,capture_output=True,text=True,timeout=20);(a/'validation.log').write_text(p.stdout+p.stderr);print(p.stdout+p.stderr)
if (stage/'comparison.png').exists():shutil.copy2(stage/'comparison.png',a/'comparison.png')
assert p.returncode==0
