from pathlib import Path
import json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
start=source.index('    function menuHeightForCompleteActions(')
helper=source[start:source.index('    function menuButtonFits(',start)]
marker=Path('/run/apx/active-graphical-environment-v1.json')
if not marker.exists():marker=Path('/run/apx/official-hub-graphical-v1.json')
home=Path('/var/lib/apx/environments')/json.loads(marker.read_text()).get('name','hub')/'home/apx'
stage=home/'.cache/apx-whole-card-height-test';assert not stage.exists();stage.mkdir()
qml='''import QtQuick
import QtTest
Item {
 id:root;width:340;height:440
 // HELPER
 Rectangle {
  id:popupBackground
  property real contentInset:10
  property real contentBottomInset:12
  property real viewportHeight:400
  width:340;height:root.menuHeightForCompleteActions(viewportHeight);clip:true
  Flickable {
   id:menuFlick;x:10;y:10;width:320
   height:popupBackground.viewportHeight-22
   contentHeight:menuContent.implicitHeight;clip:true
   property real headerInset:0
   Column {
    id:menuContent;width:320;spacing:8
    Item {height:27;width:320}
    Repeater {
     id:rows;model:12
     Rectangle {
      width:320;height:56;activeFocusOnTab:true
      Rectangle {x:10;y:5;width:32;height:32;activeFocusOnTab:true}
     }
    }
   }
  }
 }
 TestCase {
  name:'WholeCardHeight';when:windowShown
  function init() {menuFlick.contentY=0;menuFlick.headerInset=0;popupBackground.viewportHeight=400;wait(5)}
  function test_frame_ends_after_last_whole_card() {
   compare(rows.itemAt(4).y+56,347)
   compare(popupBackground.height,369)
   compare(menuFlick.height,378)
   verify(rows.itemAt(5).y+56>378)
  }
  function test_repeated_layout_does_not_collapse_the_scroll_viewport() {
   for(var i=0;i<20;i++) {wait(1);compare(popupBackground.height,369);compare(menuFlick.height,378)}
  }
  function test_scrolling_fits_to_the_new_last_card_and_returns() {
   menuFlick.contentY=64
   compare(popupBackground.height,369)
   menuFlick.contentY=35
   compare(popupBackground.height,400)
   menuFlick.contentY=0;compare(popupBackground.height,369)
  }
  function test_end_of_content_preserves_normal_padding_and_bounds() {
   menuFlick.contentY=menuFlick.contentHeight-menuFlick.height
   compare(popupBackground.height,400)
   compare(menuFlick.contentY,menuFlick.contentHeight-menuFlick.height)
  }
  function test_nested_buttons_do_not_define_the_outer_card_cutoff() {
   // The last nested button fits, but its enclosing card is clipped.
   menuFlick.contentY=14
   compare(popupBackground.height,355)
   compare(menuFlick.height,378)
  }
 }
}
'''.replace(' // HELPER',helper)
try:
 (stage/'tst_height.qml').write_text(qml)
 (Path(__file__).parent/'tst_height.qml').write_text(qml)
 meta=home.stat()
 for p in [stage]+list(stage.rglob('*')):os.chown(p,meta.st_uid,meta.st_gid)
 result=subprocess.run(['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=15)
 (Path(__file__).parent/'results.log').write_text(result.stdout+result.stderr)
 print(result.stdout+result.stderr);assert result.returncode==0
finally:shutil.rmtree(stage)
