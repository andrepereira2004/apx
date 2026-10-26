import QtQuick
import QtQuick.Controls

Rectangle {
    id: button
    property string iconName: "wifi"
    property string actionLabel: ""
    property bool powered: false
    property bool busy: false
    property bool cardHoverEnabled: true
    signal activated()
    width: Appearance.menuIconCircleSize; height: width; radius: width / 2
    antialiasing: true
    readonly property Item navigationTarget: parent
    activeFocusOnTab: true
    enabled: !busy
    readonly property color surroundingColor: parent && parent.color !== undefined ? parent.color : (parent && parent.parent && parent.parent.color !== undefined ? parent.parent.color : Appearance.surface)
    color: Qt.lighter(surroundingColor, iconHover.hovered && enabled ? 1.95 : 1.6)
    border.width: activeFocus || (iconHover.hovered && enabled) ? 2 : 0
    border.color: activeFocus ? Appearance.iconColor : "#69728a"
    MenuHover {
        parent: button.parent; z: 100
        enabled: button.cardHoverEnabled && button.enabled && !button.parent.children.some(child => child.keyboardActivationPending !== undefined)
    }
    HoverHandler { id: iconHover; blocking: false }
    scale: mouse.pressed ? .94 : 1
    Behavior on color { ColorAnimation { duration: 90 } }
    Behavior on scale { NumberAnimation { duration: 90; easing.type: Easing.OutCubic } }
    Accessible.role: Accessible.CheckBox
    Accessible.name: actionLabel
    Accessible.checkable: true
    Accessible.checked: powered
    LucideIcon {
        anchors.centerIn: parent; width: Appearance.menuGlyphSize; height: width
        name: button.iconName
        opacity: button.powered ? 1 : .55
        Behavior on opacity { NumberAnimation { duration: 90 } }
    }
    Keys.onPressed: event => {
        if ([Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space].indexOf(event.key) >= 0) {
            if (!event.isAutoRepeat) button.activated()
            event.accepted = true
        }
    }
    MouseArea {
        id: mouse; anchors.fill: parent; hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: { button.focus = false; button.activated() }
    }
}
