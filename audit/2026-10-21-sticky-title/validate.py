from pathlib import Path
import json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
source=(ROOT/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
marker=Path('/run/apx/active-graphical-environment-v1.json')
if not marker.exists():marker=Path('/run/apx/official-hub-graphical-v1.json')
home=Path('/var/lib/apx/environments')/json.loads(marker.read_text()).get('name','hub')/'home/apx'
stage=home/'.cache/apx-sticky-title-test';assert not stage.exists();stage.mkdir()
def section(start,end):return source[source.index(start):source.index(end,source.index(start))]
header=section('    component MenuHeader:', '    component SelectionIndicator:')
geometry=section('            readonly property Item scrollingHeader:', '            readonly property real viewportTargetHeight:')
sticky=section('            Rectangle {\n                id: stickyMenuHeader', '            // Reserve the pinned title area')
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
 QtObject {id:Appearance;property string fontFamily:"sans-serif"}
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
   id:menuScrollClip;x:10;y:10+menuFlick.headerInset;width:320;height:220-menuFlick.headerInset;clip:true
  Flickable {
   id:menuFlick;x:0;y:-headerInset;width:320;height:220;contentHeight:900;clip:true
   property real headerInset:stickyMenuHeader.visible ? stickyMenuHeader.height-popupBackground.contentInset : 0
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
  function test_all_content_is_clipped_below_title_without_moving_scroll_geometry() {
   compare(menuScrollClip.y+menuFlick.y,10)
   menuFlick.contentY=50;wait(500)
   compare(menuScrollClip.y,45)
   compare(menuScrollClip.height,185)
   compare(menuScrollClip.y+menuFlick.y,10)
   verify(menuScrollClip.clip)
   menuFlick.contentY=0;wait(380)
   compare(menuScrollClip.y,10)
   compare(menuScrollClip.height,220)
  }
  function test_entrance_keeps_steady_dark_backdrop_while_text_animates() {
   menuFlick.contentY=50;wait(260)
   verify(stickyMenuHeader.revealProgress>0.4 && stickyMenuHeader.revealProgress<0.95)
   fuzzyCompare(stickyMenuHeader.backdropFill.a,0.65,0.01)
   verify(stickyMenuHeader.backdropFill.r<root.popupPanel.r)
   wait(240);compare(stickyMenuHeader.revealProgress,1)
  }
  function test_title_animates_in_and_out_and_reverses_cleanly() {
   menuFlick.contentY=50;wait(60)
   verify(stickyMenuHeader.revealProgress>0 && stickyMenuHeader.revealProgress<1)
   fuzzyCompare(stickyMenuHeader.backdropFill.a,0.65,0.01)
   fuzzyCompare(scrollingMenuHeader.opacity+stickyMenuHeader.revealProgress,1,0.001)
   verify(stickyMenuHeader.visible)
   menuFlick.contentY=0;wait(30)
   verify(stickyMenuHeader.visible)
   menuFlick.contentY=50;wait(500)
   compare(stickyMenuHeader.revealProgress,1)
   menuFlick.contentY=0;wait(60)
   verify(stickyMenuHeader.revealProgress>0 && stickyMenuHeader.revealProgress<1)
   wait(320);compare(stickyMenuHeader.revealProgress,0);verify(!stickyMenuHeader.visible)
  }
  function test_original_title_returns_as_the_backdrop_dissolves() {
   menuFlick.contentY=50;wait(500)
   fuzzyCompare(stickyMenuHeader.backdropFill.a,0.65,0.01)
   menuFlick.contentY=0
   compare(scrollingMenuHeader.opacity,0)
   wait(80)
   verify(scrollingMenuHeader.opacity>0 && scrollingMenuHeader.opacity<1)
   verify(stickyMenuHeader.backdropFill.a>0 && stickyMenuHeader.backdropFill.a<1)
   fuzzyCompare(stickyMenuHeader.backdropFill.a,stickyMenuHeader.revealProgress*0.65,0.01)
   fuzzyCompare(scrollingMenuHeader.opacity+stickyMenuHeader.revealProgress,1,0.001)
   wait(300);compare(scrollingMenuHeader.opacity,1);verify(!stickyMenuHeader.visible)
  }
  function test_translucent_backdrop_covers_full_top_width_and_margin() {
   menuFlick.contentY=50;wait(500)
   compare(stickyMenuHeader.x,0);compare(stickyMenuHeader.y,0)
   compare(stickyMenuHeader.width,popupBackground.width)
   compare(stickyMenuHeader.height,45);compare(menuFlick.headerInset,35)
   verify(stickyMenuHeader.backdropFill.a>0 && stickyMenuHeader.backdropFill.a<1)
   compare(stickyTitleBackdrop.radius,popupBackground.radius)
   verify(stickyTitleBackdrop.height>stickyMenuHeader.height)
   var stops=stickyTitleBackdrop.gradient.stops
   fuzzyCompare(stops[0].color.a,0.65,0.01)
   fuzzyCompare(stops[1].position*stickyTitleBackdrop.height,35,0.01)
   fuzzyCompare(stops[2].position*stickyTitleBackdrop.height,45,0.01)
   compare(stops[2].color.a,0)
  }
  function test_opaque_rows_do_not_slide_under_the_translucent_title() {
   menuFlick.contentY=50;wait(500)
   compare(rows.itemAt(0).opacity,0)
   compare(rows.itemAt(1).opacity,1)
   fuzzyCompare(stickyMenuHeader.backdropFill.a,0.65,0.01)
   menuFlick.contentY=0;wait(380)
   compare(rows.itemAt(0).opacity,1)
  }
  function test_original_title_stays_left_until_it_has_scrolled_out() {
   verify(!stickyMenuHeader.visible)
   compare(scrollingMenuHeader.children[0].horizontalAlignment,Text.AlignLeft)
   menuFlick.contentY=20;verify(!stickyMenuHeader.visible)
   menuFlick.contentY=30;verify(stickyMenuHeader.visible)
   compare(stickyTitleText.horizontalAlignment,Text.AlignHCenter)
   compare(stickyTitleText.text,"Central de Controlo")
  }
  function test_pinned_position_is_constant_and_restores_on_return() {
   menuFlick.contentY=50;var y=stickyMenuHeader.y
   menuFlick.contentY=200;compare(stickyMenuHeader.y,y)
   compare(menuFlick.headerInset,35)
   menuFlick.contentY=0;wait(380);verify(!stickyMenuHeader.visible)
   compare(menuFlick.headerInset,0)
  }
  function test_arrow_reveal_does_not_put_the_card_under_the_title() {
   menuFlick.contentY=90
   root.ensureMenuItemVisible(rows.itemAt(1))
   var y=rows.itemAt(1).mapToItem(menuFlick.contentItem,0,0).y-menuFlick.contentY
   verify(y>=menuFlick.headerInset)
   root.ensureMenuItemVisible(rows.itemAt(0))
   compare(menuFlick.contentY,0);wait(380);verify(!stickyMenuHeader.visible)
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
