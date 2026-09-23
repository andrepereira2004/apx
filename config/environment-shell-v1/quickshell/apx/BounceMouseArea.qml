import QtQuick

MouseArea {
    id: bounceMouse
    property bool keyboardActivationPending: false
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
    Rectangle {
        anchors.fill: parent
        radius: bounceMouse.parent.radius === undefined ? 0 : bounceMouse.parent.radius
        color: "transparent"
        border.width: 1
        border.color: "#55e6ff"
        visible: bounceMouse.activeFocus || bounceMouse.keyboardActivationPending
        z: 100
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
