import QtQuick
import QtQuick.Controls
import QtTest
Item {
 id: root; width: 420; height: 300
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
 property real pendingMouseSensitivity: NaN
 property int mouseSensitivity: 0
 property string mouseSensitivityError: ""
 property int microphonePending: -1
 property int microphoneVolume: 50
 property bool microphoneMuted: false
 property string microphoneText: "50%"
 function showHotkeyOsd(icon,title,detail,progress) {}
 QtObject { id: mouseSensitivityProcess; property bool running: false; property var command: [] }
 QtObject { id: mouseSensitivityStatusProcess; property bool running: false; property var command: [] }
 QtObject { id: microphoneSetProcess; property bool running: false; property var command: [] }
 property int testVolume: 50
 property int testBrightness: 50
 MenuSlider { id: sound; x:0; y:170; width:300; height:24; from:0; to:100; value:root.testVolume; onKeyboardValueChanged: n => root.testVolume=n }
 MenuSlider { id: brightness; x:0; y:200; width:300; height:24; from:5; to:100; value:root.testBrightness; onKeyboardValueChanged: n => root.testBrightness=n }
 MenuSlider { id: mouse; x:0; y:230; width:300; height:24; from:-100; to:100; value:root.mouseSensitivity; onKeyboardValueChanged: n => root.setMouseSensitivity(n) }
 ControlSlider { id: opacityControl; x:0; y:260; width:300; height:24; from:0; to:100; value:50; property int moves:0; onMoved: moves++ }

 property var pendingTrackpadGestures: ({})
 property string trackpadGesturesError: ""
 QtObject { id: appearance; property int menuLabelInset: 54; property string fontFamily: "sans-serif" }
 QtObject { id: trackpadGesturesProcess; property bool running: false; property var command: [] }
 QtObject { id: trackpadGesturesStatusProcess; property bool running: false; property var command: [] }
 function navigateGenericMenu(event) {}
     function setTrackpadGesture(kind, value) {
        const raw = Math.max(25, Math.min(200, Math.round(25 + value * 1.75)))
        const next = Object.assign({}, trackpadGestures)
        next[kind] = raw
        trackpadGestures = next
        const pending = Object.assign({}, pendingTrackpadGestures)
        pending[kind] = raw
        pendingTrackpadGestures = pending
        trackpadGesturesError = ""
        flushTrackpadGestures()
    }
    function flushTrackpadGestures() {
        if (trackpadGesturesProcess.running || trackpadGesturesStatusProcess.running) return
        const kinds = Object.keys(pendingTrackpadGestures)
        if (!kinds.length) return
        const kind = kinds[0], raw = pendingTrackpadGestures[kind]
        const remaining = Object.assign({}, pendingTrackpadGestures)
        delete remaining[kind]
        pendingTrackpadGestures = remaining
        trackpadGesturesProcess.command = ["/home/apx/.local/bin/apx-trackpad-gestures-v1", "set", kind, String(raw)]
        trackpadGesturesProcess.running = true
    }
    function readTrackpadGestures(text) {
        try {
            const value = JSON.parse(text)
            if (Number.isFinite(value.scroll) && Number.isFinite(value.workspaces)) {
                for (const kind of Object.keys(pendingTrackpadGestures)) value[kind] = pendingTrackpadGestures[kind]
                trackpadGestures = value
            }
        } catch (error) {}
    }
    function setMouseSensitivity(value) {
        mouseSensitivity = Math.max(-100, Math.min(100, Math.round(value)))
        pendingMouseSensitivity = mouseSensitivity
        mouseSensitivityError = ""
        flushMouseSensitivity()
    }
    function flushMouseSensitivity() {
        if (!Number.isFinite(pendingMouseSensitivity) || mouseSensitivityProcess.running || mouseSensitivityStatusProcess.running) return
        const next = pendingMouseSensitivity
        pendingMouseSensitivity = NaN
        mouseSensitivityProcess.command = ["/home/apx/.local/bin/apx-mouse-sensitivity-v1", "set", String(next)]
        mouseSensitivityProcess.running = true
    }
    function readMouseSensitivity(text) {
        if (!Number.isFinite(pendingMouseSensitivity) && text.trim().length && Number.isFinite(Number(text.trim()))) mouseSensitivity = Number(text.trim())
    }
    function commitMicrophoneVolume(value) {
        var nextVolume = Math.round(value)
        microphoneVolume = nextVolume
        if (!microphoneMuted)
            microphoneText = nextVolume + "%"
        showHotkeyOsd(
            microphoneMuted
                ? Qt.resolvedUrl("icons/lucide/mic-off.svg")
                : Qt.resolvedUrl("icons/lucide/mic.svg"),
            "Microfone", microphoneMuted ? "Silenciado" : nextVolume + "%", nextVolume)
        microphonePending = nextVolume
        dispatchMicrophoneVolume()
    }
    function dispatchMicrophoneVolume() {
        if (microphoneSetProcess.running || microphonePending < 0) return
        const next = microphonePending
        microphonePending = -1
        microphoneSetProcess.command = ["/usr/bin/wpctl", "set-volume", "-l", "1", "@DEFAULT_AUDIO_SOURCE@", next + "%"]
        microphoneSetProcess.running = true
    }
     component MenuSlider: Slider {
        id: keyboardSlider
        activeFocusOnTab: true
        readonly property Item navigationTarget: parent
        readonly property bool keyboardSelected: activeFocus && root.menuKeyboardNavigation
        readonly property bool keyboardEditing: root.editingMenuSlider === keyboardSlider
        property bool directArrowAdjustment: true
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
                if (keyboardEditing || (directArrowAdjustment && (event.key === Qt.Key_Left || event.key === Qt.Key_Right))) {
                    var direction = event.key === Qt.Key_Up || event.key === Qt.Key_Right ? 1 : -1
                    keyboardValueChanged(Math.max(from, Math.min(to, Math.round(value) + direction * (directArrowAdjustment ? (event.modifiers & Qt.ShiftModifier ? 5 : 1) : 5))))
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
                            from: 0; to: 100; directArrowAdjustment: true; stepSize: 1; activeFocusOnTab: true
                            Accessible.name: "Sensibilidade de Scroll · 2 dedos"
                            enabled: root.pointerDevices.trackpad.available && root.pointerDevices.trackpad.enabled
                            wheelEnabled: false
                            onKeyboardValueChanged: nextValue => root.setTrackpadGesture("scroll", nextValue)
                            property real draggedValue: value
                            property bool dragStarted: false
                            onMoved: draggedValue = value
                            onPressedChanged: {
                                if (pressed) { dragStarted = true; draggedValue = value }
                                else if (dragStarted) { dragStarted = false; root.setTrackpadGesture("scroll", draggedValue) }
                            }
                            Binding { target: trackpadScrollSlider; property: "value"; value: (root.trackpadGestures.scroll - 25) / 1.75; when: !trackpadScrollSlider.pressed }
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
                            from: 0; to: 100; directArrowAdjustment: true; stepSize: 1; activeFocusOnTab: true
                            Accessible.name: "Sensibilidade de Workspaces · 3 dedos"
                            enabled: root.pointerDevices.trackpad.available && root.pointerDevices.trackpad.enabled
                            wheelEnabled: false
                            onKeyboardValueChanged: nextValue => root.setTrackpadGesture("workspaces", nextValue)
                            property real draggedValue: value
                            property bool dragStarted: false
                            onMoved: draggedValue = value
                            onPressedChanged: {
                                if (pressed) { dragStarted = true; draggedValue = value }
                                else if (dragStarted) { dragStarted = false; root.setTrackpadGesture("workspaces", draggedValue) }
                            }
                            Binding { target: trackpadWorkspacesSlider; property: "value"; value: (root.trackpadGestures.workspaces - 25) / 1.75; when: !trackpadWorkspacesSlider.pressed }
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
  function init() {
   trackpadGesturesProcess.running=false;trackpadGesturesStatusProcess.running=false
   trackpadGesturesProcess.command=[];root.pendingTrackpadGestures={};root.trackpadGestures={scroll:55,workspaces:100};wait(10)
  }
  function test_scroll_drag_keeps_released_value() {
   mousePress(trackpadScrollSlider,60,8);mouseMove(trackpadScrollSlider,240,8,40);mouseRelease(trackpadScrollSlider,240,8)
   verify(root.trackpadGestures.scroll>100);compare(root.trackpadGestures.workspaces,100)
   compare(trackpadGesturesProcess.command[2],"scroll")
   compare(Number(trackpadGesturesProcess.command[3]),root.trackpadGestures.scroll)
  }
  function test_workspace_drag_does_not_change_scroll() {
   mousePress(trackpadWorkspacesSlider,100,8);mouseMove(trackpadWorkspacesSlider,250,8,40);mouseRelease(trackpadWorkspacesSlider,250,8)
   verify(root.trackpadGestures.workspaces>100);compare(root.trackpadGestures.scroll,55)
   compare(trackpadGesturesProcess.command[2],"workspaces")
  }
  function test_direct_arrows_and_shift() {
   trackpadScrollSlider.forceActiveFocus()
   const initial=Math.round(trackpadScrollSlider.value)
   keyClick(Qt.Key_Right)
   compare(Math.round(trackpadScrollSlider.value),initial+1)
   keyClick(Qt.Key_Right,Qt.ShiftModifier)
   compare(Math.round(trackpadScrollSlider.value),initial+6)
   compare(root.trackpadGestures.workspaces,100)
  }
  function test_pending_keys_preserve_latest_value() {
   trackpadScrollSlider.forceActiveFocus()
   for(let i=0;i<12;i++) keyClick(Qt.Key_Right)
   const desired=root.trackpadGestures.scroll
   verify(root.pendingTrackpadGestures.scroll!==undefined)
   root.readTrackpadGestures(JSON.stringify({scroll:57,workspaces:100}))
   compare(root.trackpadGestures.scroll,desired)
   trackpadGesturesProcess.running=false;root.flushTrackpadGestures()
   compare(Number(trackpadGesturesProcess.command[3]),desired)
  }
  function test_sound_and_brightness_arrows() {
   root.testVolume=50;root.testBrightness=50
   sound.forceActiveFocus();keyClick(Qt.Key_Right);compare(root.testVolume,51)
   keyClick(Qt.Key_Left,Qt.ShiftModifier);compare(root.testVolume,46)
   brightness.forceActiveFocus();keyClick(Qt.Key_Right);compare(root.testBrightness,51)
   root.testBrightness=5;keyClick(Qt.Key_Left);compare(root.testBrightness,5)
   root.testVolume=100;sound.forceActiveFocus();keyClick(Qt.Key_Right);compare(root.testVolume,100)
  }
  function test_mouse_held_keys_queue_last_value() {
   root.mouseSensitivity=0;root.pendingMouseSensitivity=NaN
   mouseSensitivityProcess.running=false;mouseSensitivityStatusProcess.running=false
   mouse.forceActiveFocus()
   for(let i=0;i<12;i++) keyClick(Qt.Key_Right)
   compare(root.mouseSensitivity,12);compare(root.pendingMouseSensitivity,12)
   root.readMouseSensitivity("1");compare(root.mouseSensitivity,12)
   mouseSensitivityProcess.running=false;root.flushMouseSensitivity()
   compare(mouseSensitivityProcess.command[2],"12")
  }
  function test_microphone_latest_write_survives_busy_process() {
   microphoneSetProcess.running=false;root.microphonePending=-1
   root.commitMicrophoneVolume(51);root.commitMicrophoneVolume(52);root.commitMicrophoneVolume(53)
   compare(root.microphonePending,53);compare(root.microphoneVolume,53)
   microphoneSetProcess.running=false;root.dispatchMicrophoneVolume()
   compare(microphoneSetProcess.command[5],"53%")
  }
  function test_opacity_keys_emit_updates() {
   opacityControl.value=50;opacityControl.moves=0
   opacityControl.forceActiveFocus();keyClick(Qt.Key_Right);compare(opacityControl.value,51)
   keyClick(Qt.Key_Left,Qt.ShiftModifier);compare(opacityControl.value,46)
   compare(opacityControl.moves,2)
  }
  function test_ranges_and_normalization() {
   compare(trackpadScrollSlider.from,0);compare(trackpadScrollSlider.to,100)
   compare(trackpadWorkspacesSlider.from,0);compare(trackpadWorkspacesSlider.to,100)
   root.setTrackpadGesture("scroll",0);compare(root.trackpadGestures.scroll,25)
   root.setTrackpadGesture("scroll",100);compare(root.trackpadGestures.scroll,200)
   root.setTrackpadGesture("workspaces",100);compare(root.trackpadGestures.workspaces,200)
  }
 }
}
