import QtQuick
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
    Timer {
        interval: 100
        repeat: true
        running: popup.open && root.menuKeyboardNavigation && root.popupKind !== "calendar" && (root.popupKind !== "environments" || !root.isHub)
        onTriggered: {
            if (controlPageAnimation.running || controlPageCapturing) return
            // The action temporarily disables its button; let it regain focus.
            if (root.focusedMenuItem && root.focusedMenuItem.visible && root.focusedMenuItem.keyboardActivationPending === true) return
            var items = root.genericMenuItems()
            for (var i = 0; i < items.length; ++i) if (items[i].activeFocus) return
            if (items.length) {
                var previous = items.indexOf(root.focusedMenuItem)
                root.focusMenuItem(items[previous >= 0 ? previous : 0])
            }
        }
    }

    function genericMenuItems() {
        var result = []
        function visit(item) {
            if (!item.visible || !item.enabled) return
            if (item.activeFocusOnTab && item.width > 0 && item.height > 0) {
                result.push(item)
                return
            }
            for (var i = 0; i < item.children.length; ++i) visit(item.children[i])
        }
        visit(menuContent)
        return result
    }
    function clearPendingMenuFocus() {
        if (focusedMenuItem && focusedMenuItem.keyboardActivationPending !== undefined)
            focusedMenuItem.keyboardActivationPending = false
        focusedMenuItem = null
    }
    function focusMenuItem(item) {
        menuFlick.stopWheel()
        if (focusedMenuItem !== item) clearPendingMenuFocus()
        focusedMenuItem = item
        item.forceActiveFocus(Qt.TabFocusReason)
        ensureMenuItemVisible(item)
        revealKeyboardMenuItem(item)
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
    function menuNavigationRect(item) {
        // Direction follows the actual control; scrolling reveals its whole card.
        var point = item.mapToItem(menuFlick.contentItem, 0, 0)
        return { x: point.x, y: point.y, width: item.width, height: item.height }
    }
    function menuEntryIndex(items, backwards) {
        var best = -1
        var bestY = backwards ? -Infinity : Infinity
        var bestX = backwards ? -Infinity : Infinity
        for (var i = 0; i < items.length; ++i) {
            var item = items[i]
            var target = item.navigationTarget || (item.menuViewportGuard !== undefined ? item.parent : item)
            var point = target.mapToItem(menuFlick.contentItem, 0, 0)
            if (point.y < menuFlick.contentY + (menuFlick.headerInset || 0) - 0.5
                    || point.y + target.height > menuFlick.contentY + menuFlick.height + 0.5) continue
            var rect = menuNavigationRect(item)
            var y = rect.y + rect.height / 2
            var x = rect.x + rect.width / 2
            if (best < 0 || (backwards ? y > bestY + 8 : y < bestY - 8)
                    || (Math.abs(y - bestY) <= 8 && (backwards ? x > bestX : x < bestX))) {
                best = i; bestY = y; bestX = x
            }
        }
        return best >= 0 ? best : (backwards ? items.length - 1 : 0)
    }
    function menuItemIntersectsViewport(item) {
        var rect = menuNavigationRect(item)
        return rect.y + rect.height > menuFlick.contentY + (menuFlick.headerInset || 0)
            && rect.y < menuFlick.contentY + menuFlick.height
    }
    function spatialMenuIndex(rects, current, key, preferredX) {
        var origin = rects[current]
        var horizontal = key === Qt.Key_Left || key === Qt.Key_Right
        var direction = key === Qt.Key_Left || key === Qt.Key_Up ? -1 : 1
        var column = !horizontal && isFinite(preferredX) ? preferredX : origin.x + origin.width / 2
        var best = current
        var bestDistance = Infinity
        var bestOffset = Infinity
        for (var i = 0; i < rects.length; ++i) {
            if (i === current) continue
            var candidate = rects[i]
            var along = horizontal
                ? candidate.x + candidate.width / 2 - origin.x - origin.width / 2
                : candidate.y + candidate.height / 2 - origin.y - origin.height / 2
            var sameRowTolerance = horizontal ? 1 : Math.min(origin.height, candidate.height) * 0.45
            if (along * direction <= sameRowTolerance) continue
            var overlap = horizontal
                ? Math.min(origin.y + origin.height, candidate.y + candidate.height) - Math.max(origin.y, candidate.y)
                : Math.min(origin.x + origin.width, candidate.x + candidate.width) - Math.max(origin.x, candidate.x)
            // Left/right stay in the current row. Up/down can reach an inset row.
            if (horizontal && overlap <= 1) continue
            var distance = Math.abs(along)
            var offset = horizontal
                ? Math.abs(candidate.y + candidate.height / 2 - origin.y - origin.height / 2)
                : Math.abs(candidate.x + candidate.width / 2 - column)
            if (distance < bestDistance - 8 || (Math.abs(distance - bestDistance) <= 8 && offset < bestOffset)) {
                best = i
                bestDistance = distance
                bestOffset = offset
            }
        }
        return best
    }
    function navigateGenericMenu(event) {
        if (controlPageAnimation.running || controlPageCapturing) { event.accepted = true; return }
        if (popupKind === "calendar" || (popupKind === "environments" && isHub)) return
        var tab = event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab
        var arrow = [Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right].indexOf(event.key) >= 0
        if (!tab && !arrow) return
        if (arrow && root.controlsAppearanceOpen && personalizationPanel.colorInputActive) return
        // Text fields own cursor movement; only Tab navigates the menu.
        if (arrow && root.wifiPasswordVisible &&
                (wifiUsernameInput.activeFocus || wifiPasswordInput.activeFocus ||
                 wifiDomainInput.activeFocus || wifiCaInput.activeFocus)) return
        var items = genericMenuItems()
        if (!items.length) return
        var current = -1
        for (var i = 0; i < items.length; ++i) if (items[i].activeFocus) current = i
        if (arrow && current >= 0 && items[current].cursorPosition !== undefined
                && items[current].text !== undefined) return
        var backwards = event.key === Qt.Key_Backtab || event.key === Qt.Key_Up || event.key === Qt.Key_Left
        // Wheel scrolling can leave Qt focus on an option outside the viewport.
        if (current >= 0 && !menuItemIntersectsViewport(items[current])) current = -1
        // An opening menu has no previous row: Up must not select the last item.
        if (current < 0 && event.key === Qt.Key_Up) {
            if (menuFlick.contentY > 0) {
                menuKeyboardNavigation = true
                focusMenuItem(items[menuEntryIndex(items, false)])
            }
            event.accepted = true
            return
        }
        menuKeyboardNavigation = true
        var vertical = event.key === Qt.Key_Up || event.key === Qt.Key_Down
        if (!vertical || current < 0 || root.focusedMenuItem !== items[current]) menuNavigationColumn = NaN
        var next = menuEntryIndex(items, backwards)
        if (current >= 0) {
            if (vertical && !isFinite(menuNavigationColumn)) {
                var rect = menuNavigationRect(items[current])
                menuNavigationColumn = rect.x + rect.width / 2
            }
            next = tab ? (current + (event.key === Qt.Key_Backtab ? -1 : 1) + items.length) % items.length
                       : spatialMenuIndex(items.map(menuNavigationRect), current, event.key, menuNavigationColumn)
        }
        if (event.key === Qt.Key_Up && current >= 0 && next === current) {
            // The first action can sit below a heading: reveal the whole menu start.
            pendingMenuRevealItem = null
            menuFlick.stopWheel()
            menuFlick.contentY = 0
            event.accepted = true
            return
        }
        focusMenuItem(items[next])
        event.accepted = true
    }
    function environmentIsOpenable(item) {
        return !!item && (item.state === "stopped" || item.state === "ready")
    }
    function moveEnvironmentFocus(direction) {
        if (environmentManagementBusy || environmentMetadataBusy) return
        var rows = environmentCatalog.length
        // The current Environment card is informational only.
        var indices = []
        for (var index = 0; index < rows; ++index)
            if (environmentIsOpenable(environmentCatalog[index])) indices.push(index)
        indices.push(rows)
        if (selectedEnvironmentName.length) {
            indices.push(rows + 1)
            indices.push(rows + 2)
        }
        var position = indices.indexOf(environmentFocusIndex)
        if (position < 0) environmentFocusIndex = indices[direction < 0 ? indices.length - 1 : 0]
        else environmentFocusIndex = indices[Math.max(0, Math.min(indices.length - 1, position + direction))]
        if (position === 0 && direction < 0) {
            // The title/current Environment are above the first actionable row.
            menuFlick.stopWheel()
            pendingMenuRevealItem = null
            menuFlick.contentY = 0
        }
        environmentDeleteConfirm = false
        environmentEditOpen = false
    }
    function moveEnvironmentCreateFocus(direction, wrap) {
        var indices = environmentCreateVisibleFocusIndices()
        var position = indices.indexOf(environmentCreateFocusIndex)
        if (position < 0) environmentCreateFocusIndex = direction > 0 ? indices[0] : indices[indices.length - 1]
        else environmentCreateFocusIndex = indices[wrap === false
            ? Math.max(0, Math.min(indices.length - 1, position + direction))
            : (position + direction + indices.length) % indices.length]
        environmentMenu.forceActiveFocus()
    }
    function moveEnvironmentCreateVertical(direction) {
        moveEnvironmentCreateFocus(direction, false)
    }
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
