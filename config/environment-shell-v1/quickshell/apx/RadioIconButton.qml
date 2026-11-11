import QtQuick
import QtQuick.Controls

Rectangle {
    id: button
    property string iconName: "wifi"
    property string actionLabel: ""
    property bool powered: false
    property bool busy: false
    property bool cardHoverEnabled: true
    property bool cardOutlineEnabled: true
    property bool showOutline: true
    property var navigationHandler: null
    property Item keyboardRightTarget: null
    property Item keyboardDownTarget: null
    signal activated()
    width: Appearance.menuIconCircleSize; height: width; radius: width / 2
    antialiasing: true
    readonly property Item navigationTarget: parent
    activeFocusOnTab: true
    enabled: !busy
    readonly property color surroundingColor: parent && parent.color !== undefined ? parent.color : (parent && parent.parent && parent.parent.color !== undefined ? parent.parent.color : Appearance.surface)
    color: activeFocus ? "#454d64" : Qt.lighter(surroundingColor, iconHover.hovered && enabled ? 1.95 : 1.6)
    border.width: 0
    ButtonOutline {
        outlineTarget: button
        shown: button.showOutline
        selected: button.activeFocus || button.powered
        hovered: iconHover.hovered && button.enabled
    }
    MenuHover {
        parent: button.parent; z: 100
        enabled: button.cardHoverEnabled && button.enabled && !button.parent.children.some(child => child.keyboardActivationPending !== undefined)
        outlineEnabled: button.cardOutlineEnabled && button.showOutline
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
    Keys.priority: Keys.BeforeItem
    Keys.onPressed: event => {
        if ([Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space].indexOf(event.key) >= 0) {
            if (!event.isAutoRepeat) button.activated()
            event.accepted = true
        } else if (event.key === Qt.Key_Right && button.keyboardRightTarget && button.keyboardRightTarget.enabled) {
            button.keyboardRightTarget.forceActiveFocus(Qt.TabFocusReason)
            event.accepted = true
        } else if (event.key === Qt.Key_Down && button.keyboardDownTarget && button.keyboardDownTarget.enabled) {
            button.keyboardDownTarget.forceActiveFocus(Qt.TabFocusReason)
            event.accepted = true
        } else if (button.navigationHandler && [Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_Up, Qt.Key_Down, Qt.Key_Left, Qt.Key_Right].indexOf(event.key) >= 0)
            button.navigationHandler(event)
    }
    MouseArea {
        id: mouse; anchors.fill: parent; hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: { button.focus = false; button.activated() }
    }
}
