import QtQuick
import QtTest
Item {
 id: root; width:340; height:400
 property bool menuKeyboardNavigation:true; property var popup: ({open:true}); property real islandProgress:1
 property var pendingMenuRevealItem:null; property int selected:0
 property bool isHub:true
 property bool environmentKeyboardFocus:true
 property bool environmentEditOpen:false
 property bool environmentCreateOpen:true
 function handleEnvironmentCreateKey(event) {
  if(event.key===Qt.Key_Down) selected=Math.min(23,selected+1)
  else if(event.key===Qt.Key_Up) selected=Math.max(0,selected-1)
  event.accepted=true
 }

     function revealKeyboardMenuItem(item) {
        pendingMenuRevealItem = item
        Qt.callLater(root.flushMenuReveal)
    }

    function flushMenuReveal() {
        var item = pendingMenuRevealItem
        pendingMenuRevealItem = null
        if (item && item.visible && item.enabled && popup.open && root.menuKeyboardNavigation)
            root.ensureMenuItemVisible(item)
    }

    function ensureMenuItemVisible(item) {
        if (!item || !item.visible || menuFlick.height <= 0) return
        menuFlick.stopWheel()
        var target = item.navigationTarget || (item.menuViewportGuard !== undefined ? item.parent : item)
        var point = target.mapToItem(menuFlick.contentItem, 0, 0)
        var maximum = Math.max(0, menuFlick.contentHeight - menuFlick.height)
        var destination = menuFlick.contentY
        var topInset = menuFlick.headerInset || 0
        var availableHeight = menuFlick.height - topInset
        var margin = Math.min(8, Math.max(0, (availableHeight - target.height) / 2))
        // A tall section should reveal its beginning instead of jumping to its end.
        if (target.height > availableHeight)
            destination = point.y - topInset
        else if (point.y < destination + topInset + margin) destination = point.y - topInset - margin
        else if (point.y + target.height > destination + menuFlick.height - margin)
            destination = point.y + target.height - menuFlick.height + margin
        menuFlick.contentY = Math.max(0, Math.min(maximum, destination))
    }

    function menuButtonFits(surface) {
        var topInset = menuFlick.headerInset || 0
        var scroll = menuFlick.contentY + topInset
        var viewport = menuFlick.height - topInset
        var layoutHeight = menuFlick.contentHeight
        var localY = surface.y
        if (!popup.open || root.islandProgress < 1 || !surface.visible
                || surface.height > viewport) return true
        var point = surface.mapToItem(menuFlick.contentItem, 0, 0)
        return point.y >= scroll - 0.5 && point.y + surface.height <= scroll + viewport + 0.5
    }

    component MenuViewportGuard: QtObject {
        required property var surface
        required property var pointer
        readonly property bool fullyVisible: root.menuButtonFits(surface)
        property Binding opacityBinding: Binding {
            target: surface; property: "opacity"; value: 0
            when: !fullyVisible
            restoreMode: Binding.RestoreBindingOrValue
        }
        property Binding pointerBinding: Binding {
            target: pointer; property: "acceptedButtons"; value: Qt.NoButton
            when: !fullyVisible
            restoreMode: Binding.RestoreBindingOrValue
        }
    }
 Flickable {
  id:menuFlick; property real headerInset:0; width:340; height:400; contentHeight:1600; clip:true
  property int stops:0
  function stopWheel() { cancelFlick(); stops++ }
  Column {
   id:rows; width:340
   Repeater {
    id:repeater; model:24
    Rectangle {
     width:340; height:60; opacity:index===6 ? 0.42 : 1
     MouseArea {id:rowPointer; anchors.fill:parent; acceptedButtons:Qt.LeftButton; property var guard: MenuViewportGuard {surface:rowPointer.parent; pointer:rowPointer}}
     property bool keyboardFocused:root.selected===index
     onKeyboardFocusedChanged: if(keyboardFocused) root.revealKeyboardMenuItem(this)
    }
   }
  }
 }
 TextInput {id:field;visible:false}
 Item {
  id:navigation;focus:true
  Keys.onPressed: function(event) {
                        if (!root.isHub) { root.navigateGenericMenu(event); return }
                        if ([Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down].indexOf(event.key) >= 0)
                            root.menuKeyboardNavigation = true
                        if (!root.environmentKeyboardFocus && [Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down, Qt.Key_Return, Qt.Key_Enter].indexOf(event.key) >= 0) {
                            root.environmentKeyboardFocus = true
                            root.menuKeyboardNavigation = true
                            if (!root.environmentEditOpen && !root.environmentCreateOpen && !root.environmentDeleteConfirm) {
                                root.environmentFocusIndex = -1
                                root.moveEnvironmentFocus(event.key === Qt.Key_Up || event.key === Qt.Key_Backtab ? -1 : 1)
                            }
                            event.accepted = true
                            return
                        }
                        if (root.environmentEditOpen) {
                            root.handleEnvironmentEditKey(event)
                            return
                        }
                        if (root.environmentCreateOpen) {
                            root.handleEnvironmentCreateKey(event)
                            return
                        }
                        if (!root.isHub) return
                        if (root.environmentDeleteConfirm) {
                            if (event.key === Qt.Key_Left) {
                                root.environmentDeleteFocusIndex = 0
                            } else if (event.key === Qt.Key_Right) {
                                root.environmentDeleteFocusIndex = 1
                            } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                                if (root.environmentDeleteFocusIndex === 0) root.cancelEnvironmentDelete()
                                else root.destroySelectedEnvironment()
                            } else if (event.key === Qt.Key_Escape) {
                                root.cancelEnvironmentDelete()
                            } else {
                                return
                            }
                            event.accepted = true
                            return
                        }
                        if (event.key === Qt.Key_Up) {
                            root.moveEnvironmentFocus(-1)
                            event.accepted = true
                        } else if (event.key === Qt.Key_Down) {
                            root.moveEnvironmentFocus(1)
                            event.accepted = true
                        } else if (event.key === Qt.Key_Left) {
                            root.moveEnvironmentActionFocus(-1)
                            event.accepted = true
                        } else if (event.key === Qt.Key_Right) {
                            root.moveEnvironmentActionFocus(1)
                            event.accepted = true
                        } else if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                            root.activateEnvironmentFocus()
                            event.accepted = true
                        } else if (event.key === Qt.Key_Delete) {
                            root.deleteFocusedEnvironment()
                            event.accepted = true
                        } else if (event.key === Qt.Key_F2) {
                            root.beginEnvironmentEdit()
                            event.accepted = true
                        } else if (event.key === Qt.Key_Escape) {
                            root.closePopup()
                            event.accepted = true
                        }
                    }
 }
 TestCase {
  name:'KeyboardMenuScroll';when:windowShown
  function test_arrows_reveal_selection_in_both_directions() {
   root.selected=0;menuFlick.contentY=0;root.menuKeyboardNavigation=false;navigation.forceActiveFocus();wait(20)
   for(var i=0;i<20;i++) keyClick(Qt.Key_Down)
   wait(30);compare(root.selected,20);verify(menuFlick.contentY>0)
   verify(1260<=menuFlick.contentY+menuFlick.height)
   for(var j=0;j<20;j++) keyClick(Qt.Key_Up)
   wait(30);compare(root.selected,0);compare(menuFlick.contentY,0)
   verify(navigation.activeFocus)
  }
  function test_partial_cards_hide_without_changing_layout_or_keyboard_eligibility() {
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
  function test_visible_item_does_not_move_viewport() {
   menuFlick.contentY=100;root.ensureMenuItemVisible(repeater.itemAt(3))
   compare(menuFlick.contentY,100)
  }
  function test_bottom_clamped_and_pointer_selection_does_not_scroll() {
   root.selected=23;wait(30)
   verify(menuFlick.contentY<=menuFlick.contentHeight-menuFlick.height)
   root.menuKeyboardNavigation=false;menuFlick.contentY=0;root.selected=22;wait(30)
   compare(menuFlick.contentY,0);root.menuKeyboardNavigation=true
  }
 }
}
