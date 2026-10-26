"""Exercise current shell navigation helpers and real icon/body controls in Qt."""
from pathlib import Path
import json, os, shutil, subprocess

ROOT = Path(__file__).resolve().parents[2]
marker = Path('/run/apx/active-graphical-environment-v1.json')
if not marker.exists(): marker = Path('/run/apx/official-hub-graphical-v1.json')
home = Path('/var/lib/apx/environments') / json.loads(marker.read_text()).get('name', 'hub') / 'home/apx'
stage = home / '.cache/apx-arrow-navigation-test'
assert not stage.exists()
stage.mkdir()
source = (ROOT / 'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()

def function(name):
    start = source.index('    function ' + name + '(')
    end = source.index('\n    }', start) + len('\n    }')
    return source[start:end]

helpers = '\n'.join(function(name) for name in (
    'genericMenuItems', 'clearPendingMenuFocus', 'focusMenuItem',
    'revealKeyboardMenuItem', 'flushMenuReveal', 'ensureMenuItemVisible', 'menuNavigationRect',
    'menuEntryIndex', 'menuItemIntersectsViewport',
    'spatialMenuIndex', 'navigateGenericMenu', 'environmentIsOpenable',
    'moveEnvironmentFocus', 'moveEnvironmentCreateFocus', 'moveEnvironmentCreateVertical'))
recovery = source[source.index('    Timer {', source.index('    function navigateGenericMenu(')):source.index('    property var hardwareProfile:', source.index('    function navigateGenericMenu('))]
qml = '''import QtQuick
import QtTest
import "apx"
Item {
 id: root; width:340; height:240
 Keys.onPressed:event=>root.navigateGenericMenu(event)
 property var popup: ({open:true})
 property bool menuKeyboardNavigation:false
 property Item focusedMenuItem:null
 property Item pendingMenuRevealItem:null
 property real menuNavigationColumn:NaN
 property string popupKind:"controls"
 property bool isHub:true
 property bool controlsAppearanceOpen:false
 property bool wifiPasswordVisible:false
 property bool controlPageCapturing:false
 property bool environmentManagementBusy:false
 property bool environmentMetadataBusy:false
 property bool environmentDeleteConfirm:false
 property bool environmentEditOpen:false
 property int environmentFocusIndex:-1
 property int environmentCreateFocusIndex:-1
 property string selectedEnvironmentName:""
 property var environmentCatalog:[{state:"stopped"},{state:"active"},{state:"ready"}]
 function environmentCreateVisibleFocusIndices() { return [0,1,3,5,8] }
 property var controlPageAnimation: ({running:false})
 property var personalizationPanel: ({colorInputActive:false})
 property var wifiUsernameInput: ({activeFocus:false})
 property var wifiPasswordInput: ({activeFocus:false})
 property var wifiDomainInput: ({activeFocus:false})
 property var wifiCaInput: ({activeFocus:false})
 // RECOVERY
 // HELPERS
 Item { id: environmentMenu }
 Flickable {
  id:menuFlick; property real headerInset:0; width:340; height:240; contentHeight:menuContent.height
  function stopWheel() { cancelFlick() }
  Column {
   id:menuContent; width:340; spacing:8
   Repeater {
    id:rows; model:12
    Rectangle {
     width:340; height:56
     RadioIconButton { id:icon; x:8; y:10; iconName:"wifi" }
     BounceMouseArea { id:body; x:54; width:parent.width-x; height:parent.height; cursorShape:Qt.PointingHandCursor }
     function iconItem() {return icon}
     function bodyItem() {return body}
    }
   }
   TextInput {id:field; width:200; height:40; activeFocusOnTab:true; text:"example"}
  }
 }
 Item { id:navigation; focus:true; Keys.onPressed:event=>root.navigateGenericMenu(event) }
 TestCase {
  name:"ArrowNavigation"; when:windowShown
  function event(key) { return {key:key,accepted:false} }
  function init() {
   root.clearPendingMenuFocus();root.menuKeyboardNavigation=false
   root.menuNavigationColumn=NaN;root.pendingMenuRevealItem=null
   menuFlick.contentY=0;navigation.forceActiveFocus();wait(10)
  }
  function test_horizontal_targets_the_actual_icon_and_body() {
   root.focusMenuItem(rows.itemAt(0).iconItem())
   keyClick(Qt.Key_Right);verify(rows.itemAt(0).bodyItem().activeFocus)
   keyClick(Qt.Key_Left);verify(rows.itemAt(0).iconItem().activeFocus)
   compare(menuFlick.contentY,0)
  }
  function test_repeated_arrows_reveal_full_cards_and_stop_at_end() {
   root.focusMenuItem(rows.itemAt(0).iconItem())
   for(var i=1;i<12;i++) {
    keyClick(Qt.Key_Down)
    verify(rows.itemAt(i).iconItem().activeFocus)
    var rect=rows.itemAt(i).mapToItem(menuFlick.contentItem,0,0)
    verify(rect.y>=menuFlick.contentY-0.5)
    verify(rect.y+56<=menuFlick.contentY+menuFlick.height+0.5)
   }
   // The next editable field remains reachable; arrows inside it are native.
   keyClick(Qt.Key_Down);verify(field.activeFocus)
   for(var j=0;j<12;j++) keyClick(Qt.Key_Left)
   verify(field.activeFocus);compare(field.cursorPosition,0)
  }
  function test_lost_focus_recovers_the_same_control_without_jumping_to_start() {
   root.menuKeyboardNavigation=true
   root.focusMenuItem(rows.itemAt(7).bodyItem());wait(10)
   var position=menuFlick.contentY
   navigation.forceActiveFocus();wait(130)
   verify(rows.itemAt(7).bodyItem().activeFocus)
   compare(menuFlick.contentY,position)
  }
  function test_up_without_selection_keeps_opening_position() {
   keyClick(Qt.Key_Up);verify(navigation.activeFocus)
   compare(menuFlick.contentY,0);verify(!root.menuKeyboardNavigation)
  }
  function test_up_at_first_action_reveals_heading() {
   rows.itemAt(0).height=100
   root.focusMenuItem(rows.itemAt(0).bodyItem());root.menuKeyboardNavigation=true
   menuFlick.contentY=20
   root.pendingMenuRevealItem=rows.itemAt(9)
   keyClick(Qt.Key_Up)
   compare(menuFlick.contentY,0);compare(root.pendingMenuRevealItem,null)
   wait(30);compare(menuFlick.contentY,0)
   rows.itemAt(0).height=56
  }
  function test_up_after_wheel_can_reach_the_menu_start() {
   menuFlick.contentY=320
   keyClick(Qt.Key_Up);verify(rows.itemAt(5).iconItem().activeFocus)
   for(var i=0;i<7;i++) keyClick(Qt.Key_Up)
   compare(menuFlick.contentY,0);verify(rows.itemAt(0).iconItem().activeFocus)
  }
  function test_wheel_scrolled_viewport_does_not_jump_to_old_focus() {
   root.focusMenuItem(rows.itemAt(0).iconItem());wait(10)
   menuFlick.contentY=320
   keyClick(Qt.Key_Down);verify(rows.itemAt(5).iconItem().activeFocus)
   verify(menuFlick.contentY>=312)
  }
  function test_real_keys_keep_column_across_a_wide_action() {
   var first=rows.itemAt(0).bodyItem(), bridge=rows.itemAt(1).bodyItem()
   var last=rows.itemAt(2).bodyItem(), icon=rows.itemAt(2).iconItem()
   first.x=260;first.width=80
   bridge.x=0;bridge.width=340;rows.itemAt(1).iconItem().visible=false
   last.x=260;last.width=80;icon.x=110
   root.menuNavigationColumn=NaN;root.focusMenuItem(first)
   keyClick(Qt.Key_Down);verify(bridge.activeFocus)
   keyClick(Qt.Key_Down);verify(last.activeFocus)
   keyClick(Qt.Key_Up);verify(bridge.activeFocus)
   keyClick(Qt.Key_Up);verify(first.activeFocus)
   first.x=54;first.width=286;bridge.x=54;bridge.width=286
   last.x=54;last.width=286;icon.x=8;rows.itemAt(1).iconItem().visible=true
  }
  function test_vertical_column_is_remembered_across_full_width_row() {
   var rects=[{x:200,y:0,width:60,height:40},
     {x:0,y:60,width:340,height:40},
     {x:0,y:120,width:100,height:40},
     {x:200,y:120,width:60,height:40}]
   compare(root.spatialMenuIndex(rects,0,Qt.Key_Down,230),1)
   compare(root.spatialMenuIndex(rects,1,Qt.Key_Down,230),3)
   compare(root.spatialMenuIndex(rects,3,Qt.Key_Up,230),1)
  }
  function test_reveal_requests_only_follow_latest_selection() {
   root.menuKeyboardNavigation=true
   root.revealKeyboardMenuItem(rows.itemAt(10))
   root.revealKeyboardMenuItem(rows.itemAt(1))
   wait(10);compare(menuFlick.contentY,0)
   compare(root.pendingMenuRevealItem,null)
  }
  function test_diagonal_rows_do_not_trap_vertical_navigation() {
   var rects=[{x:0,y:0,width:36,height:36},{x:120,y:64,width:80,height:56}]
   compare(root.spatialMenuIndex(rects,0,Qt.Key_Down),1)
   compare(root.spatialMenuIndex(rects,1,Qt.Key_Up),0)
   compare(root.spatialMenuIndex(rects,0,Qt.Key_Right),0)
  }
  function test_disabled_rows_are_skipped_and_up_down_keep_column() {
   rows.itemAt(1).enabled=false
   root.focusMenuItem(rows.itemAt(0).bodyItem())
   keyClick(Qt.Key_Down);verify(rows.itemAt(2).bodyItem().activeFocus)
   keyClick(Qt.Key_Up);verify(rows.itemAt(0).bodyItem().activeFocus)
   keyClick(Qt.Key_Up);verify(rows.itemAt(0).bodyItem().activeFocus)
   rows.itemAt(1).enabled=true
  }
  function test_up_at_first_environment_reveals_title_and_clears_old_reveal() {
   root.environmentFocusIndex=0;menuFlick.contentY=180
   root.pendingMenuRevealItem=rows.itemAt(9)
   root.moveEnvironmentFocus(-1)
   compare(root.environmentFocusIndex,0)
   compare(menuFlick.contentY,0)
   compare(root.pendingMenuRevealItem,null)
  }
  function test_environment_arrows_clamp_but_tab_can_wrap_form() {
   root.environmentFocusIndex=-1;root.moveEnvironmentFocus(-1);compare(root.environmentFocusIndex,3)
   root.moveEnvironmentFocus(1);compare(root.environmentFocusIndex,3)
   root.moveEnvironmentFocus(-1);compare(root.environmentFocusIndex,2)
   root.moveEnvironmentFocus(-1);compare(root.environmentFocusIndex,0)
   root.moveEnvironmentFocus(-1);compare(root.environmentFocusIndex,0)
   root.environmentCreateFocusIndex=8
   root.moveEnvironmentCreateVertical(1);compare(root.environmentCreateFocusIndex,8)
   root.moveEnvironmentCreateFocus(1);compare(root.environmentCreateFocusIndex,0)
   root.moveEnvironmentCreateVertical(-1);compare(root.environmentCreateFocusIndex,0)
  }
 }
}
'''.replace(' // HELPERS', helpers).replace(' // RECOVERY', recovery)
try:
    shutil.copytree(ROOT/'config/environment-shell-v1/quickshell/apx', stage/'apx')
    (stage/'apx/qmldir').write_text('singleton Appearance 1.0 Appearance.qml\n')
    # Service-free appearance fixture; actual action/hover/icon components stay intact.
    (stage/'apx/Appearance.qml').write_text('pragma Singleton\nimport QtQuick\nQtObject { property int menuIconCircleSize:36; property int menuGlyphSize:16; property color surface:"#1b1d26"; property color hover:"#292d3a"; property color iconColor:"white"; property bool tintButtons:false }')
    (stage/'tst_arrows.qml').write_text(qml)
    (Path(__file__).parent/'tst_arrows.qml').write_text(qml)
    meta=home.stat()
    for p in [stage]+list(stage.rglob('*')): os.chown(p,meta.st_uid,meta.st_gid)
    result=subprocess.run(['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py'),
        'env','QT_QPA_PLATFORM=offscreen','/usr/lib/qt6/bin/qmltestrunner',
        '-input','/home/apx/.cache/'+stage.name,'-o','-,txt'],capture_output=True,text=True,timeout=20)
    (Path(__file__).parent/'results.log').write_text(result.stdout+result.stderr)
    print(result.stdout+result.stderr)
    assert result.returncode==0
finally:
    shutil.rmtree(stage)
