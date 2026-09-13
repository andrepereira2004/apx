import QtQuick

MouseArea {
    id: bounceMouse
    // The same action is shared by pointer and keyboard activation.
    activeFocusOnTab: activeFocus || cursorShape === Qt.PointingHandCursor
    Keys.onPressed: function(event) {
        if (event.key === Qt.Key_Return || event.key === Qt.Key_Enter || event.key === Qt.Key_Space) {
            if (!event.isAutoRepeat) bounceMouse.clicked(null)
            event.accepted = true
        }
    }
    Rectangle {
        anchors.fill: parent
        anchors.margins: 2
        radius: 7
        color: "transparent"
        border.width: 1
        border.color: "#55e6ff"
        visible: bounceMouse.activeFocus
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
