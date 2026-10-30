import QtQuick

// Contour follows the outer edge of each button.
Rectangle {
    required property Item outlineTarget
    property Item outlineHost: null
    property bool selected: false
    property bool hovered: false
    property bool shown: true
    property int idleWidth: 0
    property real outlineRadius: Math.max(0, outlineTarget.radius || 0)
    readonly property rect mappedBounds: {
        if (!outlineHost) return Qt.rect(0, 0, outlineTarget.width, outlineTarget.height)
        // Reading the whole parent chain keeps the mapped position reactive
        // when a Row or a bar island moves without resizing the button.
        for (var item = outlineTarget; item && item !== outlineHost; item = item.parent) {
            item.x; item.y; item.width; item.height; item.scale; item.rotation
        }
        var topLeft = outlineTarget.mapToItem(outlineHost, 0, 0)
        var bottomRight = outlineTarget.mapToItem(outlineHost, outlineTarget.width, outlineTarget.height)
        return Qt.rect(topLeft.x, topLeft.y, bottomRight.x - topLeft.x, bottomRight.y - topLeft.y)
    }
    parent: outlineHost || outlineTarget
    x: mappedBounds.x
    y: mappedBounds.y
    width: mappedBounds.width
    height: mappedBounds.height
    z: outlineHost ? 100 : 0
    radius: outlineRadius * (outlineTarget.width > 0 ? width / outlineTarget.width : 1)
    color: "transparent"
    antialiasing: true
    border.width: selected || hovered ? 1 : idleWidth
    border.pixelAligned: false
    border.color: selected ? Appearance.buttonSelectedBorder : hovered ? Appearance.buttonHoverBorder : Appearance.buttonIdleBorder
    visible: shown && border.width > 0 && outlineTarget.visible
}
