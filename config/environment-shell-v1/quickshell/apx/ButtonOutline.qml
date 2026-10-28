import QtQuick

// Contour follows the outer edge of each button.
Rectangle {
    property bool selected: false
    property bool hovered: false
    property int idleWidth: 0
    property real outlineRadius: Math.max(0, (parent.radius || 0))
    anchors.fill: parent
    anchors.margins: 0
    radius: outlineRadius
    color: "transparent"
    antialiasing: true
    border.width: selected || hovered ? 1 : idleWidth
    border.pixelAligned: true
    border.color: selected ? Appearance.buttonSelectedBorder : hovered ? Appearance.buttonHoverBorder : Appearance.buttonIdleBorder
    visible: border.width > 0
}
