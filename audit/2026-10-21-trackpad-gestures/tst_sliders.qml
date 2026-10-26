import QtQuick
import QtQuick.Controls
import QtTest
Item {
 id: root; width: 420; height: 220
 property bool menuKeyboardNavigation: false
 property var editingMenuSlider: null
 property color cyan: "cyan"
 property color textMain: "white"
 property color controlButtonSurface: "#222222"
 property color controlButtonOutline: "#555555"
 property int menuBodySize: 14
 property var pointerDevices: ({trackpad:{available:true,enabled:true}})
 property var trackpadGestures: ({scroll:55,workspaces:100})
 property var calls: []
 QtObject { id: appearance; property int menuLabelInset: 54; property string fontFamily: "sans-serif" }
 QtObject { id: trackpadGesturesProcess; property bool running: false }
 QtObject { id: trackpadGesturesStatusProcess; property bool running: false }
 function navigateGenericMenu(event) {}
 function setTrackpadGesture(kind,value) {
  const next = {scroll:trackpadGestures.scroll,workspaces:trackpadGestures.workspaces}
  next[kind]=Math.round(value);trackpadGestures=next;calls.push({kind:kind,value:Math.round(value)})
 }
     component MenuSlider: Slider {
        id: keyboardSlider
        activeFocusOnTab: true
        readonly property Item navigationTarget: parent
        readonly property bool keyboardSelected: activeFocus && root.menuKeyboardNavigation
        readonly property bool keyboardEditing: root.editingMenuSlider === keyboardSlider
        signal keyboardValueChanged(real nextValue)
        onActiveFocusChanged: {
            if (!activeFocus && keyboardEditing) root.editingMenuSlider = null
        }
        Keys.priority: Keys.BeforeItem
        Keys.onPressed: function(event) {
            if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter) {
                if (!event.isAutoRepeat)
                    root.editingMenuSlider = keyboardEditing ? null : keyboardSlider
                event.accepted = true
            } else if (event.key === Qt.Key_Escape && keyboardEditing) {
                root.editingMenuSlider = null
                event.accepted = true
            } else if ([Qt.Key_Left, Qt.Key_Right, Qt.Key_Up, Qt.Key_Down].indexOf(event.key) >= 0) {
                if (keyboardEditing) {
                    var direction = event.key === Qt.Key_Up || event.key === Qt.Key_Right ? 1 : -1
                    keyboardValueChanged(Math.max(from, Math.min(to, Math.round(value) + direction * 5)))
                    event.accepted = true
                } else root.navigateGenericMenu(event)
            } else if (event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab) {
                root.editingMenuSlider = null
                root.navigateGenericMenu(event)
            } else {
                // Prevent Slider's native Home/End/Page keys from bypassing Enter.
                event.accepted = true
            }
        }
        Rectangle {
            parent: keyboardSlider.parent
            anchors.fill: parent
            radius: parent.radius
            z: 100
            color: "transparent"
            border.width: keyboardSlider.keyboardEditing ? 2 : 1
            border.color: root.cyan
            visible: keyboardSlider.activeFocus && root.menuKeyboardNavigation
        }
    }
 Column { width: parent.width; spacing: 10
 Rectangle {
                        id: trackpadScrollCard
                        width: parent.width; height: 72; radius: 14; color: root.controlButtonSurface
                        Text { renderType: Text.CurveRendering; anchors.left: parent.left; anchors.leftMargin: appearance.menuLabelInset; y: 12; text: "Scroll · 2 dedos"; color: root.textMain; font.family: appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        Text { renderType: Text.CurveRendering; id: trackpadScrollPercent; width: 46; horizontalAlignment: Text.AlignRight; anchors.right: parent.right; anchors.rightMargin: 12; y: 12; text: Math.round(trackpadScrollSlider.value) + "%"; color: root.textMain; font.family: appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        MenuSlider {
                            id: trackpadScrollSlider
                            anchors.left: parent.left; anchors.leftMargin: appearance.menuLabelInset; anchors.right: trackpadScrollPercent.left; anchors.rightMargin: 8
                            y: 44; height: 16; topPadding: 0; bottomPadding: 0
                            from: 25; to: 200; stepSize: 1; activeFocusOnTab: true
                            Accessible.name: "Sensibilidade de Scroll · 2 dedos"
                            enabled: !trackpadGesturesProcess.running && !trackpadGesturesStatusProcess.running && root.pointerDevices.trackpad.available && root.pointerDevices.trackpad.enabled
                            wheelEnabled: false
                            onKeyboardValueChanged: nextValue => root.setTrackpadGesture("scroll", nextValue)
                            property real draggedValue: value
                            property bool dragStarted: false
                            onMoved: draggedValue = value
                            onPressedChanged: {
                                if (pressed) { dragStarted = true; draggedValue = value }
                                else if (dragStarted) { dragStarted = false; root.setTrackpadGesture("scroll", draggedValue) }
                            }
                            Binding { target: trackpadScrollSlider; property: "value"; value: root.trackpadGestures.scroll; when: !trackpadScrollSlider.pressed }
                            background: Rectangle {
                                x: trackpadScrollSlider.leftPadding
                                y: trackpadScrollSlider.topPadding + trackpadScrollSlider.availableHeight / 2 - height / 2
                                width: trackpadScrollSlider.availableWidth; height: 5; radius: 3
                                color: root.controlButtonOutline
                                Rectangle { width: trackpadScrollSlider.visualPosition * parent.width; height: parent.height; radius: 3; color: root.textMain }
                            }
                            handle: Item { width: 0; height: 0 }
                        }
                    }
Rectangle {
                        id: trackpadWorkspacesCard
                        width: parent.width; height: 72; radius: 14; color: root.controlButtonSurface
                        Text { renderType: Text.CurveRendering; anchors.left: parent.left; anchors.leftMargin: appearance.menuLabelInset; y: 12; text: "Workspaces · 3 dedos"; color: root.textMain; font.family: appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        Text { renderType: Text.CurveRendering; id: trackpadWorkspacesPercent; width: 46; horizontalAlignment: Text.AlignRight; anchors.right: parent.right; anchors.rightMargin: 12; y: 12; text: Math.round(trackpadWorkspacesSlider.value) + "%"; color: root.textMain; font.family: appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        MenuSlider {
                            id: trackpadWorkspacesSlider
                            anchors.left: parent.left; anchors.leftMargin: appearance.menuLabelInset; anchors.right: trackpadWorkspacesPercent.left; anchors.rightMargin: 8
                            y: 44; height: 16; topPadding: 0; bottomPadding: 0
                            from: 25; to: 200; stepSize: 1; activeFocusOnTab: true
                            Accessible.name: "Sensibilidade de Workspaces · 3 dedos"
                            enabled: !trackpadGesturesProcess.running && !trackpadGesturesStatusProcess.running && root.pointerDevices.trackpad.available && root.pointerDevices.trackpad.enabled
                            wheelEnabled: false
                            onKeyboardValueChanged: nextValue => root.setTrackpadGesture("workspaces", nextValue)
                            property real draggedValue: value
                            property bool dragStarted: false
                            onMoved: draggedValue = value
                            onPressedChanged: {
                                if (pressed) { dragStarted = true; draggedValue = value }
                                else if (dragStarted) { dragStarted = false; root.setTrackpadGesture("workspaces", draggedValue) }
                            }
                            Binding { target: trackpadWorkspacesSlider; property: "value"; value: root.trackpadGestures.workspaces; when: !trackpadWorkspacesSlider.pressed }
                            background: Rectangle {
                                x: trackpadWorkspacesSlider.leftPadding
                                y: trackpadWorkspacesSlider.topPadding + trackpadWorkspacesSlider.availableHeight / 2 - height / 2
                                width: trackpadWorkspacesSlider.availableWidth; height: 5; radius: 3
                                color: root.controlButtonOutline
                                Rectangle { width: trackpadWorkspacesSlider.visualPosition * parent.width; height: parent.height; radius: 3; color: root.textMain }
                            }
                            handle: Item { width: 0; height: 0 }
                        }
                    }
 }
 TestCase {
  name: "IndependentGestureSliders"; when: windowShown
  function init() { root.calls=[];root.trackpadGestures={scroll:55,workspaces:100};wait(10) }
  function test_scroll_drag_keeps_released_value() {
   mousePress(trackpadScrollSlider,60,8);mouseMove(trackpadScrollSlider,240,8,40);mouseRelease(trackpadScrollSlider,240,8)
   compare(root.calls.length,1);compare(root.calls[0].kind,"scroll")
   verify(root.trackpadGestures.scroll>100);compare(root.trackpadGestures.workspaces,100)
   compare(Math.round(trackpadScrollSlider.value),root.trackpadGestures.scroll)
  }
  function test_workspace_drag_does_not_change_scroll() {
   mousePress(trackpadWorkspacesSlider,100,8);mouseMove(trackpadWorkspacesSlider,250,8,40);mouseRelease(trackpadWorkspacesSlider,250,8)
   compare(root.calls.length,1);compare(root.calls[0].kind,"workspaces")
   verify(root.trackpadGestures.workspaces>100);compare(root.trackpadGestures.scroll,55)
  }
  function test_keyboard_controls_remain_independent() {
   trackpadScrollSlider.keyboardValueChanged(75)
   compare(root.trackpadGestures.scroll,75);compare(root.trackpadGestures.workspaces,100)
   trackpadWorkspacesSlider.keyboardValueChanged(120)
   compare(root.trackpadGestures.scroll,75);compare(root.trackpadGestures.workspaces,120)
  }
 }
}
