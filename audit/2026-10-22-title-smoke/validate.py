from pathlib import Path
import json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
marker=Path('/run/apx/active-graphical-environment-v1.json')
if not marker.exists():marker=Path('/run/apx/official-hub-graphical-v1.json')
home=Path('/var/lib/apx/environments')/json.loads(marker.read_text()).get('name','hub')/'home/apx'
stage=home/'.cache/apx-title-smoke-test';assert not stage.exists();stage.mkdir()
def section(start,end):return source[source.index(start):source.index(end,source.index(start))]
header=section('    component MenuHeader:', '    component SelectionIndicator:')
geometry=section('            readonly property Item scrollingHeader:', '            readonly property real viewportTargetHeight:')
sticky=section('            Rectangle {\n                id: stickyMenuHeader', '            // Content stays behind the translucent title')
helpers=section('    function ensureMenuItemVisible(', '    // Preserve layout')+section('    function menuButtonFits(', '    component MenuViewportGuard:')
qml="""import QtQuick
import QtTest
Item {
 id:root; width:340;height:240
 property string popupKind:"controls"
 property bool calendarEditor:false
 property real islandProgress:1
 property color popupPanel:"#101117"
 property color textMain:"white"
 property color controlButtonOutline:"gray"
 property int menuTitleSize:14
 property var popup:({open:true})
 QtObject {id:Appearance;property string fontFamily:"sans-serif";property int menuTitleInset:8}
 // HEADER
 // HELPERS
 Item {id:calendarMenuHeader;visible:false;property string title:"Calendário"}
 Item {id:calendarEditorHeader;visible:false;property string title:"Novo evento"}
 Rectangle {
  id:popupBackground;width:340;height:240;radius:20
  property real contentInset:10
  // GEOMETRY
  // STICKY
  Item {
   id:menuScrollClip;x:10;y:10;width:320;height:220;clip:true
  Flickable {
   id:menuFlick;x:0;y:0;width:320;height:220;contentHeight:900;clip:true
   property real headerInset:stickyMenuHeader.visible ? stickyMenuHeader.y+stickyMenuHeader.height-popupBackground.contentInset : 0
   function stopWheel() {cancelFlick()}
   Column {
    width:320;spacing:5
    MenuHeader {id:scrollingMenuHeader;title:"Central de Controlo"}
    Repeater {id:rows;model:12;Rectangle {id:row; width:320;height:56; color:"#1b1d26"; opacity:root.menuButtonFits(row) ? 1 : 0}}
   }
  }
 }
 }
 TestCase {
  name:"StickyTitle";when:windowShown
  function init() {menuFlick.contentY=0;wait(380)}
  function test_content_remains_under_the_title() {
   menuFlick.contentY=50;wait(500)
   compare(menuScrollClip.y,10);compare(menuFlick.y,0)
   compare(menuScrollClip.height,220);compare(menuFlick.headerInset,35)
   verify(menuScrollClip.clip)
  }
  function test_vertical_smoke_is_75_percent_opaque_at_three_quarters() {
   menuFlick.contentY=50;wait(500)
   compare(stickyMenuHeader.x,1);compare(stickyMenuHeader.y,1)
   compare(stickyMenuHeader.width,popupBackground.width-2)
   compare(stickyTitleBackdrop.radius,popupBackground.radius-1)
   var stops=stickyTitleBackdrop.gradient.stops
   compare(stickyTitleBackdrop.gradient.orientation,Gradient.Vertical)
   compare(stops.length,4)
   compare(stops[0].position,0);compare(stops[0].color.a,1)
   fuzzyCompare(stops[1].position*stickyTitleBackdrop.height,8,0.01);compare(stops[1].color.a,1)
   compare(stops[2].position,0.75);fuzzyCompare(stops[2].color.a,0.75,0.01)
   compare(stops[3].position,1);compare(stops[3].color.a,0)
  }
  function test_partial_rows_do_not_disappear_under_the_title() {
   for(var scroll=30;scroll<95;scroll+=3){
    menuFlick.contentY=scroll;wait(1)
    compare(rows.itemAt(0).opacity,1)
   }
   compare(rows.itemAt(1).opacity,1)
   // Existing bottom-card rule still applies beyond the viewport.
   compare(rows.itemAt(8).opacity,0)
  }
  function test_title_animation_and_return_remain_continuous() {
   menuFlick.contentY=50;wait(100)
   verify(stickyMenuHeader.revealProgress>0 && stickyMenuHeader.revealProgress<1)
   fuzzyCompare(stickyMenuHeader.backdropStrength,1,0.01)
   menuFlick.contentY=0;wait(30);verify(stickyMenuHeader.visible)
   menuFlick.contentY=50;wait(500);compare(stickyMenuHeader.revealProgress,1)
   menuFlick.contentY=0;wait(380);verify(!stickyMenuHeader.visible)
   compare(scrollingMenuHeader.opacity,1)
  }
  function test_keyboard_reveal_keeps_actions_below_title() {
   menuFlick.contentY=90
   root.ensureMenuItemVisible(rows.itemAt(1))
   var y=rows.itemAt(1).mapToItem(menuFlick.contentItem,0,0).y-menuFlick.contentY
   verify(y>=menuFlick.headerInset)
   root.ensureMenuItemVisible(rows.itemAt(0));compare(menuFlick.contentY,0)
  }
  function test_z_render_preview() {
   menuFlick.contentY=45;wait(500)
   var done=false
   root.grabToImage(function(result){result.saveToFile("/home/apx/.cache/apx-title-smoke-preview.png");done=true})
   tryVerify(function(){return done},1000)
  }
 }
}
""".replace(' // HEADER',header).replace(' // HELPERS',helpers).replace('  // GEOMETRY',geometry).replace('  // STICKY',sticky).replace('Appearance','appearance')
try:
 (stage/'tst_title.qml').write_text(qml)
 (Path(__file__).parent/'tst_title.qml').write_text(qml)
 meta=home.stat()
 for p in [stage]+list(stage.rglob('*')):os.chown(p,meta.st_uid,meta.st_gid)
 result=subprocess.run(['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=15)
 (Path(__file__).parent/'results.log').write_text(result.stdout+result.stderr)
 print(result.stdout+result.stderr);assert result.returncode==0
finally:shutil.rmtree(stage)
