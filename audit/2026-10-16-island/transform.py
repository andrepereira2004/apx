def shell(text):
    text=text.replace('                    z: -1; anchors.fill: parent; anchors.margins: -3\n                    radius: height / 2','                    parent: rightActions.parent\n                    x: rightActions.x - 3; y: rightActions.y - 3\n                    width: rightActions.width + 6; height: rightActions.height + 6\n                    z: -1; radius: height / 2')
    text=text.replace('animation_pending: root.popupAnimationPending,', 'island_progress: root.islandProgress, island_closing: root.popupClosing, animation_pending: root.popupAnimationPending,') if 'island_progress: root.islandProgress' not in text else text
    if 'property real islandProgress:' in text:return text
    text=text.replace('    property bool popupAnimationPending: false','''    property real islandProgress: 0
    property bool popupClosing: false
    property real islandContentOpacity: 1
    property rect islandOrigin: Qt.rect(0, 8, 40, 30)
    property bool popupAnimationPending: false''',1)
    text=text.replace('    function closePopup() {','''    function closePopup() {
        if (!popup.open || popupClosing) return
        popupClosing = true
        popupAnimationPending = false
        popupKeyboardRequested = false
        popupOpenAnimation.stop()
        popupCloseAnimation.restart()
    }

    function finishClosePopup() {''',1)
    text=text.replace('        popup.open = false\n        popupAnimationPending = false','        popup.open = false\n        popupClosing = false\n        popupAnimationPending = false',1)
    text=text.replace('''        popupBackground.opacity = 0.001
        popupBackground.scale = (popupKind === "controls" ? controlCenterScale : 1) * 0.96
''','''        popupCloseAnimation.stop()
        popupClosing = false
        if (!popup.open) {
            islandProgress = 0
            if (popupTarget && bar) {
                var point = popupTarget.mapToItem(bar.contentItem, 0, 0)
                islandOrigin = Qt.rect(point.x + bar.margins.left, point.y + bar.margins.top,
                                       popupTarget.width, popupTarget.height)
            }
        }
        islandContentOpacity = 0
        islandContentAnimation.restart()
''',1)
    old='''            popup.open = false
            popupKind = ""
            if (kind === "environments") environmentKeyboardFocus = false
            if (kind === "calendar") calendarFocusAction = ({ kind: "", key: "" })
            return'''
    assert old in text;text=text.replace(old,'            root.closePopup()\n            return',1)
    # Shared surface morphs from the trigger into a fully laid out panel.
    start=text.index('            x: root.popupLeftMargin',text.index('id: popupBackground'))
    end=text.index('\n\n            // Blank space',start)
    text=text[:start]+'''            readonly property real targetWidth: Math.min(popup.menuWidth, popup.width - 16)
            readonly property real targetHeight: Math.min(popup.menuHeight, popup.height - 73,
                root.popupKind === "calendar" || root.popupKind === "environments"
                ? popup.menuHeight : menuContent.implicitHeight + 20)
            property real settledHeight: targetHeight
            Behavior on settledHeight { enabled: root.islandProgress > .99 && !root.popupClosing; NumberAnimation { duration: 200; easing.type: Easing.OutQuint } }
            x: root.islandOrigin.x + (Math.max(8, Math.min(root.popupLeftMargin, popup.width - targetWidth - 8)) - root.islandOrigin.x) * root.islandProgress
            y: root.islandOrigin.y + (65 - root.islandOrigin.y) * root.islandProgress
            width: root.islandOrigin.width + (targetWidth - root.islandOrigin.width) * root.islandProgress
            height: root.islandOrigin.height + (settledHeight - root.islandOrigin.height) * root.islandProgress
            Keys.onPressed: function(event) { root.navigateGenericMenu(event) }
            scale: 1
            opacity: Math.min(1, root.islandProgress * 5)
            transformOrigin: Item.TopLeft
            clip: true
            radius: 15 + (20 - 15) * root.islandProgress
            color: root.popupPanel
            border.width: 1
            border.color: root.shellBorder

            NumberAnimation {
                id: popupOpenAnimation
                target: root; property: "islandProgress"; to: 1
                duration: 240; easing.type: Easing.OutQuint
                onFinished: root.flushEnvironmentCatalog()
            }
            NumberAnimation {
                id: popupCloseAnimation
                target: root; property: "islandProgress"; to: 0
                duration: 180; easing.type: Easing.InOutCubic
                onFinished: if (root.popupClosing) root.finishClosePopup()
            }
            NumberAnimation {
                id: islandContentAnimation
                target: root; property: "islandContentOpacity"; to: 1
                duration: 200; easing.type: Easing.OutCubic
            }'''+text[end:]
    text=text.replace('''                id: menuFlick
                anchors.fill: parent
                anchors.margins: 10''','''                id: menuFlick
                x: 10; y: 10
                width: popupBackground.targetWidth - 20
                height: popupBackground.settledHeight - 20
                opacity: Math.max(0, (root.islandProgress - .3) / .7) * root.islandContentOpacity
                enabled: !root.popupClosing && root.islandProgress > .8''',1)
    text=text.replace('    property string ghostMessage:', '    Binding { target: DesktopActivity; property: "detailsVisible"; value: popup.open && root.popupKind === "controls" && root.controlsActivityKind === "media" }\n    property string ghostMessage:',1)
    # Right actions share one pill; every existing action keeps its own hit area.
    anchor='''            Row {
                anchors.right: parent.right'''
    assert text.count(anchor)==1
    text=text.replace(anchor,'''            Row {
                id: rightActions
                Rectangle {
                    parent: rightActions.parent
                    x: rightActions.x - 3; y: rightActions.y - 3
                    width: rightActions.width + 6; height: rightActions.height + 6
                    z: -1; radius: height / 2
                    color: Appearance.tintButtons ? Appearance.barSurface : "#dc202330"
                    border.width: 1; border.color: "#304f566c"
                }
                anchors.right: parent.right''',1)
    text=text.replace('''                    id: modelStoreButton''','''                    grouped: true
                    id: modelStoreButton''',1)
    for name in ['appsButton','filesButton','batteryButton','controlCenterButton']:
        text=text.replace('                    id: '+name,'                    grouped: true\n                    id: '+name,1)
    # Media pill occupies only spare space left of the central Environment capsule.
    anchor='''            BarButton {
                id: environmentButton'''
    assert text.count(anchor)==1
    text=text.replace(anchor,'''            MediaIsland {
                id: mediaIsland
                anchors.right: environmentButton.left
                anchors.rightMargin: 12
                anchors.verticalCenter: parent.verticalCenter
                width: Math.min(220, Math.max(0, environmentButton.x - leftActions.width - 36))
                visible: !root.isHub && DesktopActivity.state.players.length > 0 && width >= 110
                onActivated: {
                    root.popupKind = "controls"
                    root.popupTarget = mediaIsland
                    root.popupKeyboardRequested = true
                    root.showPopup()
                    root.openActivitySection("media")
                }
            }

'''+anchor,1)
    text=text.replace('''            Row {
                anchors.left: parent.left''','''            Row {
                id: leftActions
                anchors.left: parent.left''',1)
    return text
