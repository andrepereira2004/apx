import QtQuick

MouseArea {
    id: bounceMouse
    property var menuViewportGuard: null
    property bool keyboardActivationPending: false
    property bool menuFeedbackEnabled: true
    property bool outlineEnabled: true
    property bool pressAnimationEnabled: true
    property var navigationHandler: null
    property var keyboardLeftHandler: null
    property var keyboardEnterHandler: null
    property var keyboardDownHandler: null
    // Shared pointer feedback for every menu action; keyboard focus stays cyan.
    hoverEnabled: true
    onVisibleChanged: if (!visible) keyboardActivationPending = false
    // The same action is shared by pointer and keyboard activation.
    activeFocusOnTab: activeFocus || cursorShape === Qt.PointingHandCursor
    Keys.priority: Keys.BeforeItem
    Keys.onPressed: function(event) {
        if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
            if (!event.isAutoRepeat) {
                if (event.key !== Qt.Key_Space && keyboardEnterHandler)
                    keyboardEnterHandler()
                else {
                    keyboardActivationPending = true
                    bounceMouse.clicked(null)
                }
            }
            event.accepted = true
        } else if (event.key === Qt.Key_Down && keyboardDownHandler)
            keyboardDownHandler(event)
        else if (event.key === Qt.Key_Left && keyboardLeftHandler)
            keyboardLeftHandler(event)
        else if (navigationHandler && [Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right].indexOf(event.key) >= 0)
            navigationHandler(event)
    }
    Timer {
        interval: 50
        repeat: true
        running: bounceMouse.keyboardActivationPending
        onTriggered: {
            if (!bounceMouse.visible) bounceMouse.keyboardActivationPending = false
            else if (bounceMouse.enabled) {
                bounceMouse.forceActiveFocus(Qt.TabFocusReason)
                bounceMouse.keyboardActivationPending = false
            }
        }
    }
    MenuHover {
        parent: bounceMouse.parent
        z: 100
        enabled: bounceMouse.enabled && bounceMouse.menuFeedbackEnabled
        keyboardFocused: bounceMouse.activeFocus || bounceMouse.keyboardActivationPending
        outlineEnabled: bounceMouse.outlineEnabled
    }

    NumberAnimation {
        id: bounceDown
        target: bounceMouse.parent
        property: "scale"
        to: 0.96
        duration: 40
        easing.type: Easing.OutCubic
    }

    NumberAnimation {
        id: bounceUp
        target: bounceMouse.parent
        property: "scale"
        to: 1
        duration: 70
        easing.type: Easing.OutCubic
    }

    onPressed: if (pressAnimationEnabled) bounceDown.restart()
    onReleased: if (pressAnimationEnabled) bounceUp.restart()
    onCanceled: if (pressAnimationEnabled) bounceUp.restart()
}
