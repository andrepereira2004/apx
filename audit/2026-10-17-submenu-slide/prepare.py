from pathlib import Path
r=Path(__file__).resolve().parents[2];a=Path(__file__).parent
t=(r/'config/environment-shell-v1/quickshell/apx/shell.qml').read_text()
start=t.index('    onMenuRouteChanged:');end=t.index('    property rect islandOrigin:',start)
t=t[:start]+'''    property real controlPageProgress: 1
    property int controlPageDirection: 1
    property bool controlPageCapturing: false
    property bool controlPageQueued: false
    property int controlPageGeneration: 0
    property var controlPageCapture: null
    property rect outgoingPageRect: Qt.rect(0, 0, 0, 0)
    function controlDepth(state) {
        if (state.controlsAppearanceOpen || state.shortcutsOpen) return 2
        if (state.controlsWifiOpen || state.controlsBluetoothOpen) return 2
        if (state.controlsMoreOpen || state.controlsConnectivityOpen || state.controlsBrightnessOpen || state.controlsAudioOpen || state.controlsMicrophoneOpen || state.controlsActivityKind) return 1
        return 0
    }
    function cancelControlTransition() {
        controlPageGeneration++
        controlPageAnimation.stop()
        controlPageCapturing = false
        controlPageQueued = false
        controlPageCapture = null
        controlPageProgress = 1
    }
    function startControlTransition() {
        if (controlPageAnimation.running || controlPageCapturing) {
            controlPageQueued = true
            return
        }
        controlPageQueued = false
        var next = {controlsAppearanceOpen: controlsAppearanceOpen, shortcutsOpen: shortcutsOpen, controlsWifiOpen: controlsWifiOpen, controlsBluetoothOpen: controlsBluetoothOpen, controlsMoreOpen: controlsMoreOpen, controlsConnectivityOpen: controlsConnectivityOpen, controlsBrightnessOpen: controlsBrightnessOpen, controlsAudioOpen: controlsAudioOpen, controlsMicrophoneOpen: controlsMicrophoneOpen, controlsActivityKind: controlsActivityKind}
        controlPageDirection = controlDepth(next) < controlDepth(renderedControls) ? -1 : 1
        outgoingPageRect = Qt.rect(popupBackground.x, popupBackground.y, popupBackground.width, popupBackground.height)
        controlPageCapturing = true
        var generation = ++controlPageGeneration
        function reveal(capture) {
            if (generation !== root.controlPageGeneration || root.popupClosing || !popup.open) return
            root.controlPageCapture = capture
            root.controlPageCapturing = false
            root.controlPageProgress = 0
            root.syncRenderedControls()
            menuFlick.contentY = 0
            controlPageAnimation.restart()
            Qt.callLater(function() {
                var items = root.genericMenuItems()
                if (root.menuKeyboardNavigation && items.length) root.focusMenuItem(items[0])
            })
        }
        if (!popupBackground.grabToImage(function(result) { reveal(result) })) reveal(null)
    }
    onMenuRouteChanged: Qt.callLater(function() {
        if (!popup.open || root.popupClosing || root.popupAnimationPending || root.islandProgress < .99) {
            root.syncRenderedControls()
            return
        }
        if (root.popupKind !== "controls") {
            root.syncRenderedControls()
            root.islandContentOpacity = 0
            islandContentAnimation.restart()
            return
        }
        islandContentAnimation.stop()
        root.islandContentOpacity = 1
        root.startControlTransition()
    })
    NumberAnimation {
        id: controlPageAnimation
        target: root; property: "controlPageProgress"; from: 0; to: 1
        duration: 340; easing.type: Easing.OutCubic
        onFinished: {
            root.controlPageCapture = null
            if (root.controlPageQueued) Qt.callLater(function() { root.startControlTransition() })
        }
    }

'''+t[end:]
t=t.replace('        controlPageAnimation.stop()\n        popupAnimationPending', '        cancelControlTransition()\n        popupAnimationPending')
t=t.replace('    function showPopup() {\n        controlPageAnimation.stop()','    function showPopup() {\n        cancelControlTransition()')
t=t.replace('Behavior on settledHeight { enabled: !controlPageAnimation.running && root.islandProgress > .99','Behavior on settledHeight { enabled: root.islandProgress > .99')
t=t.replace('x: root.islandOrigin.x + (settledX - root.islandOrigin.x) * root.islandProgress','x: root.islandOrigin.x + (settledX - root.islandOrigin.x) * root.islandProgress + (root.popupKind === "controls" ? root.controlPageDirection * 28 * (1 - root.controlPageProgress) : 0)')
t=t.replace(' + (root.popupKind === "controls" && controlPageAnimation.running && !controlPageFadeOut.running ? 6 * (1 - root.islandContentOpacity) : 0)','')
t=t.replace('(root.popupKind === "controls" ? root.islandContentOpacity : 1)','(root.popupKind === "controls" ? root.controlPageProgress : 1)')
t=t.replace('!controlPageAnimation.running\n                contentWidth:', '!controlPageAnimation.running && !root.controlPageCapturing\n                contentWidth:')
# Snapshot sits above incoming content and never receives pointer input.
marker='        Rectangle {\n            id: popupBackground'
snapshot='''        Image {
            id: outgoingControlPage
            z: 2
            visible: root.controlPageCapture !== null && root.controlPageProgress < 1
            source: root.controlPageCapture ? root.controlPageCapture.url : ""
            x: root.outgoingPageRect.x - root.controlPageDirection * 28 * root.controlPageProgress
            y: root.outgoingPageRect.y
            width: root.outgoingPageRect.width; height: root.outgoingPageRect.height
            opacity: 1 - root.controlPageProgress
            smooth: true
        }

'''
assert marker in t;t=t.replace(marker,snapshot+marker,1)
t=t.replace('page_transition: controlPageAnimation.running,','page_transition: controlPageAnimation.running || root.controlPageCapturing, page_progress: root.controlPageProgress, outgoing_page_opacity: outgoingControlPage.opacity, outgoing_page_visible: outgoingControlPage.visible, outgoing_page_x: outgoingControlPage.x,')
(a/'shell.qml').write_text(t)
(a/'transform.py').write_text('from pathlib import Path\nRELATIVES=["quickshell/apx/shell.qml"]\ndef transform(rel,s):\n return (Path(__file__).parent/"shell.qml").read_text()\n')
(r/'scripts/physical-pilot/deploy-submenu-slide-20261017.py').write_text((r/'scripts/physical-pilot/deploy-controls-motion-20261017.py').read_text().replace('controls-motion','submenu-slide').replace('controls_motion','submenu_slide'))
(a/'validate-candidate.py').write_text((r/'audit/2026-10-17-controls-motion/validate-candidate.py').read_text().replace('controls-motion','submenu-slide').replace('motion-validation','submenu-slide-validation'))
