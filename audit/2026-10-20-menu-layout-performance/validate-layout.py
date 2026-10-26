"""Run actual menu sizing expressions in Qt with wrapped content during reveal."""
from pathlib import Path
import json,os,re,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
marker=Path('/run/apx/active-graphical-environment-v1.json');marker=marker if marker.exists() else Path('/run/apx/official-hub-graphical-v1.json')
state=json.loads(marker.read_text());state.setdefault('name','hub')
home=Path('/var/lib/apx/environments')/state['name']/'home/apx'
stage=home/'.cache/apx-menu-layout-test-20261020'
assert not stage.exists();stage.mkdir();meta=home.stat()
source=(ROOT/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
width=re.search(r'width: ([^\n]+)',source.split('id: menuFlick',1)[1]).group(1)
height=source.split('readonly property real targetHeight: ',1)[1].split('            property real settledHeight:',1)[0].strip()
qml="""import QtQuick
import QtTest
Item {
 id: root; width:1280; height:720
 property real islandProgress:0
 property rect islandOrigin:Qt.rect(1100,8,72,32)
 property int widthChanges:0
 property var appearance: ({menuTop:65,menuMaxHeight:400})
 property var popup: ({height:720})
 Rectangle {
  id:popupBackground
  property real targetWidth:340
  property real contentInset:10
  property real contentBottomInset:12
  readonly property real targetHeight: HEIGHT
  width:root.islandOrigin.width+(targetWidth-root.islandOrigin.width)*root.islandProgress
  height:root.islandOrigin.height+(targetHeight-root.islandOrigin.height)*root.islandProgress
  clip:true
  Flickable {
   id:menuFlick; width: WIDTH; height:parent.height
   contentWidth:width;contentHeight:menuContent.implicitHeight
   onWidthChanged:root.widthChanges++
   Column {
    id:menuContent; width:parent.width
    Rectangle {id:extraContent;width:parent.width;height:0}
    Text {width:parent.width;wrapMode:Text.WordWrap;text:'Long text in a menu must keep the same wrapping throughout the reveal without forcing a different height on every frame.'}
   }
  }
 }
 NumberAnimation {id:opening;target:root;property:'islandProgress';to:1;duration:300;easing.type:Easing.OutCubic}
 TestCase {
  name:'StableMenuLayout';when:windowShown
  function test_tall_content_is_capped_and_scrollable() {
   extraContent.height=2000;wait(30)
   compare(popupBackground.targetHeight,400)
   root.islandProgress=1;wait(30)
   verify(menuFlick.contentHeight>menuFlick.height)
   menuFlick.contentY=150;compare(menuFlick.contentY,150)
   extraContent.height=0;menuFlick.contentY=0;root.islandProgress=0;wait(30)
  }
  function test_reveal_does_not_reflow() {
   wait(50)
   var expectedHeight=popupBackground.targetHeight
   var expectedWidth=menuFlick.width
   root.widthChanges=0
   opening.start()
   for(var i=0;i<24;i++) {
    wait(16)
    compare(menuFlick.width,expectedWidth)
    compare(popupBackground.targetHeight,expectedHeight)
   }
   compare(root.widthChanges,0)
   compare(root.islandProgress,1)
   compare(menuFlick.width,popupBackground.width-20)
   // A real destination resize must still update the content and wrapped height.
   popupBackground.targetWidth=260;wait(30)
   compare(menuFlick.width,240)
   verify(popupBackground.targetHeight>=expectedHeight)
  }
 }
}
""".replace('WIDTH',width).replace('HEIGHT',height.replace('Appearance.', 'root.appearance.'))
try:
 (stage/'tst_layout.qml').write_text(qml)
 (Path(__file__).parent/'tst_layout.qml').write_text(qml)
 for p in [stage]+list(stage.rglob('*')):os.chown(p,meta.st_uid,meta.st_gid)
 runner=['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt']
 result=subprocess.run(runner,capture_output=True,text=True,timeout=15)
 (Path(__file__).parent/'layout-test.log').write_text(result.stdout+result.stderr)
 print(result.stdout+result.stderr);assert result.returncode==0
finally:shutil.rmtree(stage)
