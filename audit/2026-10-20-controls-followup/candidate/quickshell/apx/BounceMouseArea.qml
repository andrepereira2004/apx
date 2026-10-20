import QtQuick

MouseArea {
    id: bounceMouse
    property bool keyboardActivationPending: false
    // Shared pointer feedback for every menu action; keyboard focus stays cyan.
    hoverEnabled: true
    onVisibleChanged: if (!visible) keyboardActivationPending = false
    // The same action is shared by pointer and keyboard activation.
    activeFocusOnTab: activeFocus || cursorShape === Qt.PointingHandCursor
    Keys.onPressed: function(event) {
        if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
            if (!event.isAutoRepeat) {
                keyboardActivationPending = true
                bounceMouse.clicked(null)
            }
            event.accepted = true
        }
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
        enabled: bounceMouse.enabled
        keyboardFocused: bounceMouse.activeFocus || bounceMouse.keyboardActivationPending
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

    onPressed: bounceDown.restart()
    onReleased: bounceUp.restart()
    onCanceled: bounceUp.restart()
}
