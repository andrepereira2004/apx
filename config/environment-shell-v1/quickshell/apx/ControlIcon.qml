import QtQuick
import QtQuick.Controls
import QtQuick.Controls.impl as ControlsImpl

Item {
    id: glyph
    property url source
    property color tint
    readonly property bool originalLucide: source.toString().indexOf("/icons/lucide/") >= 0

    // Load the original SVG at the menu's 2x render resolution, keeping its
    // logical size, 24-unit viewBox and original stroke unchanged.
    // IconImage is Qt Controls' existing tinted image primitive; bypass only
    // ToolButton's implicit QIcon sizing, not the original SVG artwork.
    // Instantiate only the selected renderer, including in closed menus.
    Loader {
        anchors.fill: parent
        sourceComponent: glyph.originalLucide ? lucideIcon : fallbackIcon
    }
    Component {
        id: lucideIcon
        ControlsImpl.IconImage {
            source: glyph.source
            color: glyph.tint
            sourceSize: Qt.size(Math.ceil(width * 2), Math.ceil(height * 2))
            fillMode: Image.PreserveAspectFit
            smooth: true
            mipmap: false
        }
    }
    Component {
        id: fallbackIcon
        ToolButton {
            padding: 0
            focusPolicy: Qt.NoFocus
            hoverEnabled: false
            display: AbstractButton.IconOnly
            icon.source: glyph.source
            icon.color: glyph.tint
            icon.width: width
            icon.height: height
            background: Item {}
        }
    }
}
