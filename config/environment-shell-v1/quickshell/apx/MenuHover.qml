import QtQuick

// Highlight the complete card, even when its icon and body have separate actions.
Item {
    id: feedback
    anchors.fill: parent
    property bool keyboardFocused: false
    property bool hasSurface: false
    Component.onCompleted: hasSurface = parent && parent.color !== undefined
    readonly property bool hovered: pointer.hovered && enabled
    HoverHandler { parent: feedback.parent; id: pointer; blocking: false; enabled: feedback.enabled }
    Binding {
        target: feedback.parent
        property: "color"
        value: Qt.lighter(Appearance.tintButtons ? Appearance.hover : "#292d3a", feedback.parent.brightActionHover === true ? 1.95 : 1)
        when: feedback.hovered && feedback.hasSurface
        restoreMode: Binding.RestoreBindingOrValue
    }
    Rectangle {
        anchors.fill: parent
        anchors.margins: 1
        radius: Math.max(0, (feedback.parent.radius || 0) - 1)
        color: "transparent"
        border.width: 1
        border.color: feedback.keyboardFocused ? "#55e6ff" : "#69728a"
        visible: (feedback.hovered || feedback.keyboardFocused) && feedback.parent.brightActionHover !== true
        antialiasing: true
    }
}
