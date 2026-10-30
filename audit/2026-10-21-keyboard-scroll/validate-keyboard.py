"""Run actual menu sizing expressions in Qt with wrapped content during reveal."""
from pathlib import Path
import json,os,re,shutil,subprocess
ROOT=Path(__file__).resolve().parents[2]
marker=Path('/run/apx/active-graphical-environment-v1.json');marker=marker if marker.exists() else Path('/run/apx/official-hub-graphical-v1.json')
state=json.loads(marker.read_text());state.setdefault('name','hub')
home=Path('/var/lib/apx/environments')/state['name']/'home/apx'
stage=home/'.cache/apx-keyboard-scroll-test-20261021'
assert not stage.exists();stage.mkdir();meta=home.stat()
source=(ROOT/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
qml="import QtQuick\nimport QtTest\nItem {\n id: root; width:340; height:400\n property bool menuKeyboardNavigation:true\n property var pendingMenuRevealItem:null; property int selected:0\n     function revealKeyboardMenuItem(item) {\n        Qt.callLater(function() {\n            if (item && item.visible && item.enabled && root.menuKeyboardNavigation)\n                root.ensureMenuItemVisible(item)\n        })\n    }\n\n    function ensureMenuItemVisible(item) {\n        if (!item || !item.visible || menuFlick.height <= 0) return\n        menuFlick.stopWheel()\n        var target = item.navigationTarget || item\n        var point = target.mapToItem(menuFlick.contentItem, 0, 0)\n        var maximum = Math.max(0, menuFlick.contentHeight - menuFlick.height)\n        var destination = menuFlick.contentY\n        if (point.y < destination) destination = point.y - 4\n        else if (point.y + target.height > destination + menuFlick.height)\n            destination = point.y + target.height - menuFlick.height + 4\n        menuFlick.contentY = Math.max(0, Math.min(maximum, destination))\n    }\n\n\n Flickable {\n  id:menuFlick; property real headerInset:0; width:340; height:400; contentHeight:1600; clip:true\n  property int stops:0\n  function stopWheel() { cancelFlick(); stops++ }\n  Column {\n   id:rows; width:340\n   Repeater {\n    id:repeater; model:24\n    Rectangle {\n     width:340; height:60\n     property bool keyboardFocused:root.selected===index\n     onKeyboardFocusedChanged: if(keyboardFocused) root.revealKeyboardMenuItem(this)\n    }\n   }\n  }\n }\n TextInput {id:field;visible:false}\n Item {\n  id:navigation;focus:true\n  Keys.onPressed: function(event) {\n   if(event.key===Qt.Key_Down) {root.selected=Math.min(23,root.selected+1);event.accepted=true}\n   if(event.key===Qt.Key_Up) {root.selected=Math.max(0,root.selected-1);event.accepted=true}\n  }\n }\n TestCase {\n  name:'KeyboardMenuScroll';when:windowShown\n  function test_arrows_reveal_selection_in_both_directions() {\n   root.selected=0;menuFlick.contentY=0;navigation.forceActiveFocus();wait(20)\n   for(var i=0;i<20;i++) keyClick(Qt.Key_Down)\n   wait(30);compare(root.selected,20);verify(menuFlick.contentY>0)\n   verify(1260<=menuFlick.contentY+menuFlick.height)\n   for(var j=0;j<20;j++) keyClick(Qt.Key_Up)\n   wait(30);compare(root.selected,0);compare(menuFlick.contentY,0)\n   verify(navigation.activeFocus)\n  }\n  function test_visible_item_does_not_move_viewport() {\n   menuFlick.contentY=100;root.ensureMenuItemVisible(repeater.itemAt(3))\n   compare(menuFlick.contentY,100)\n  }\n  function test_bottom_clamped_and_pointer_selection_does_not_scroll() {\n   root.selected=23;wait(30)\n   verify(menuFlick.contentY<=menuFlick.contentHeight-menuFlick.height)\n   root.menuKeyboardNavigation=false;menuFlick.contentY=0;root.selected=22;wait(30)\n   compare(menuFlick.contentY,0);root.menuKeyboardNavigation=true\n  }\n }\n}\n"
# Always exercise the current shell helper rather than a copied implementation.
start = source.index('    function revealKeyboardMenuItem(')
end = source.index('    // Preserve layout', start)
fixture_start = qml.index('    function revealKeyboardMenuItem(')
fixture_end = qml.index(' Flickable {', fixture_start)
guard_start = source.index('    function menuButtonFits(')
guard_end = source.index('    Component { id: menuViewportGuardFactory;', guard_start)
qml = qml[:fixture_start] + source[start:end] + source[guard_start:guard_end] + qml[fixture_end:]
qml = qml.replace('property bool menuKeyboardNavigation:true', 'property bool menuKeyboardNavigation:true; property var popup: ({open:true}); property real islandProgress:1')
qml = qml.replace('width:340; height:60', 'width:340; height:60; opacity:index===6 ? 0.42 : 1\n     MouseArea {id:rowPointer; anchors.fill:parent; acceptedButtons:Qt.LeftButton; property var guard: MenuViewportGuard {surface:rowPointer.parent; pointer:rowPointer}}')
qml = qml.replace("  function test_visible_item_does_not_move_viewport() {", """  function test_partial_cards_hide_without_changing_layout_or_keyboard_eligibility() {
   menuFlick.contentY=0;wait(20)
   var last=repeater.itemAt(6)
   compare(last.opacity,0);verify(last.visible);verify(last.enabled)
   compare(last.children[0].acceptedButtons,Qt.NoButton)
   compare(menuFlick.contentHeight,1600)
   menuFlick.contentY=20;wait(20)
   fuzzyCompare(last.opacity,0.42,0.001)
   compare(last.children[0].acceptedButtons,Qt.LeftButton)
   compare(repeater.itemAt(0).opacity,0)
   compare(repeater.itemAt(7).opacity,0)
   menuFlick.contentY=0;wait(20)
   compare(repeater.itemAt(0).opacity,1)
  }
  function test_visible_item_does_not_move_viewport() {""")
# Route real key events through the Environment menu's actual key handler.
handler_start = source.index('Keys.onPressed: function(event)', source.index('id: environmentMenu\n'))
brace = source.index('{', handler_start)
depth = 1
handler_end = brace + 1
while depth:
    if source[handler_end] == '{': depth += 1
    elif source[handler_end] == '}': depth -= 1
    handler_end += 1
fixture_start = qml.index('Keys.onPressed: function(event)')
brace = qml.index('{', fixture_start)
depth = 1
fixture_end = brace + 1
while depth:
    if qml[fixture_end] == '{': depth += 1
    elif qml[fixture_end] == '}': depth -= 1
    fixture_end += 1
qml = qml[:fixture_start] + source[handler_start:handler_end] + qml[fixture_end:]
qml = qml.replace('property var pendingMenuRevealItem:null; property int selected:0', """property var pendingMenuRevealItem:null; property int selected:0
 property bool isHub:true
 property bool environmentKeyboardFocus:true
 property bool environmentEditOpen:false
 property bool environmentCreateOpen:true
 function handleEnvironmentCreateKey(event) {
  if(event.key===Qt.Key_Down) selected=Math.min(23,selected+1)
  else if(event.key===Qt.Key_Up) selected=Math.max(0,selected-1)
  event.accepted=true
 }
""")
qml = qml.replace('root.selected=0;menuFlick.contentY=0;navigation.forceActiveFocus();wait(20)',
 'root.selected=0;menuFlick.contentY=0;root.menuKeyboardNavigation=false;navigation.forceActiveFocus();wait(20)')
try:
 (stage/'tst_keyboard.qml').write_text(qml)
 (Path(__file__).parent/'tst_keyboard.qml').write_text(qml)
 for p in [stage]+list(stage.rglob('*')):os.chown(p,meta.st_uid,meta.st_gid)
 runner=['python',str(ROOT/'audit/2026-10-16-lucide-bar/session-command.py'),'env','QT_QPA_PLATFORM=offscreen','/usr/lib/qt6/bin/qmltestrunner','-input','/home/apx/.cache/'+stage.name,'-o','-,txt']
 result=subprocess.run(runner,capture_output=True,text=True,timeout=15)
 (Path(__file__).parent/'keyboard-test.log').write_text(result.stdout+result.stderr)
 print(result.stdout+result.stderr);assert result.returncode==0
finally:shutil.rmtree(stage)
