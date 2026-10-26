from pathlib import Path
import json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
a=source.index('            layer.textureSize:',source.index('id: popupBackground\n'))
effect=source[a:source.index('\n            radius:',a)]
a=source.index('        Rectangle {\n            id: popupClipMask')
mask=source[a:source.index('        Rectangle {\n            id: popupBackground',a)]
marker=Path('/run/apx/active-graphical-environment-v1.json')
if not marker.exists():marker=Path('/run/apx/official-hub-graphical-v1.json')
home=Path('/var/lib/apx/environments')/json.loads(marker.read_text()).get('name','hub')/'home/apx'
stage=home/'.cache/apx-rounded-scroll-test';assert not stage.exists();stage.mkdir()
qml='''import QtQuick
import QtQuick.Window
import QtQuick.Effects
import QtTest
Rectangle {
 id:root;width:220;height:220;color:"#ff0000"
 property var popup:({open:true})
 // MASK
 Rectangle {
  id:popupBackground;readonly property real renderScale:Window.window.devicePixelRatio;readonly property real textureScale:Math.ceil(renderScale);x:20;y:20;width:180;height:180;radius:20;color:"#101117"
  clip:true;layer.enabled:popup.open
  // EFFECT
  Flickable {
   id:scroll;anchors.fill:parent;contentHeight:400;clip:true
   Column {
    width:180;spacing:8
    Repeater {model:5;Rectangle {width:180;height:70;radius:18;color:"#ffffff"}}
   }
  }
 }
 TestCase {
  name:"RoundedScrollClip";when:windowShown
  function test_same_corner_contour_at_every_scroll_position() {
   var positions=[0,20,65,85,140]
   for(var n=0;n<positions.length;n++) {
    scroll.contentY=positions[n];wait(35)
    var frame=grabImage(root)
    var dpr=frame.width/root.width
    function sample(x,y) {return frame.pixel(Math.floor(x*dpr),Math.floor(y*dpr))}
    frame.save(Qt.resolvedUrl("scroll-corners.png").toString().replace("file://",""))
    verify(sample(110,110)!==Qt.rgba(1,0,0,1), "Menu content must remain rendered")
    compare(sample(21,21),Qt.rgba(1,0,0,1))
    compare(sample(198,21),Qt.rgba(1,0,0,1))
    compare(sample(21,198),Qt.rgba(1,0,0,1))
    compare(sample(198,198),Qt.rgba(1,0,0,1))
    for(var delta=1;delta<18;delta+=4)
     fuzzyCompare(sample(20+delta,23).g,frame.pixel(frame.width-1-Math.floor((20+delta)*dpr),Math.floor(23*dpr)).g,0.06)
    if(n===1)frame.save(Qt.resolvedUrl("scroll-corners.png").toString().replace("file://",""))
   }
  }
 }
}
'''.replace(' // MASK',mask).replace('  // EFFECT',effect)
try:
 (stage/'tst_corners.qml').write_text(qml)
 (Path(__file__).parent/'tst_corners.qml').write_text(qml)
 meta=home.stat()
 for p in [stage]+list(stage.rglob('*')):os.chown(p,meta.st_uid,meta.st_gid)
 result=subprocess.run(['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=wayland','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=15)
 (Path(__file__).parent/'results.log').write_text(result.stdout+result.stderr)
 print(result.stdout+result.stderr)
 if (stage/'scroll-corners.png').exists():shutil.copy2(stage/'scroll-corners.png',Path(__file__).parent/'scroll-corners.png')
 assert result.returncode==0
finally:shutil.rmtree(stage)
