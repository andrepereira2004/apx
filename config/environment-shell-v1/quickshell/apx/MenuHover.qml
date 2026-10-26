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
    readonly property bool selected: keyboardFocused || parent.keyboardFocused === true || (parent.selected === true && parent.iconActionEnabled !== true) || parent.checked === true
    readonly property bool outlineVisible: enabled && (selected || hovered) && parent.outlineManaged !== true
    // Avoid drawing the old outer border underneath the common inset contour.
    Binding {
        target: feedback.parent
        property: "border.width"
        value: 0
        when: feedback.hasSurface && feedback.outlineVisible
        restoreMode: Binding.RestoreBindingOrValue
    }
    ButtonOutline {
        outlineRadius: Math.max(0, (feedback.parent.radius || 0))
        selected: feedback.selected
        hovered: feedback.hovered
        visible: feedback.outlineVisible
    }
}
