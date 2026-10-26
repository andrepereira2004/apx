import QtQuick
import QtQuick.Controls
import QtQuick.Shapes
import "LucidePaths.js" as LucidePaths

Item {
    id: glyph
    property url source
    property color tint
    readonly property string lucideName: {
        const url = source.toString()
        return url.indexOf("/icons/lucide/") >= 0 ? url.substring(url.lastIndexOf("/") + 1).replace(/\.svg$/, "") : ""
    }
    readonly property string vectorPath: LucidePaths.paths[lucideName] || ""

    // Render the original 24-unit paths directly; no small QIcon raster or texture upscale.
    Shape {
        visible: glyph.vectorPath.length > 0
        width: 24; height: 24
        anchors.centerIn: parent
        preferredRendererType: Shape.CurveRenderer
        transform: Scale { origin.x: 12; origin.y: 12; xScale: Math.min(glyph.width, glyph.height) / 24; yScale: xScale }
        ShapePath {
            strokeColor: glyph.tint
            strokeWidth: 2
            fillColor: "transparent"
            capStyle: ShapePath.RoundCap
            joinStyle: ShapePath.RoundJoin
            PathSvg { path: glyph.vectorPath }
        }
    }
    // Non-Lucide sources (application and user-provided icons) retain Qt's icon loader.
    ToolButton {
        visible: !glyph.vectorPath.length
        anchors.fill: parent
        padding: 0
        focusPolicy: Qt.NoFocus
        hoverEnabled: false
        display: AbstractButton.IconOnly
        icon.source: visible ? glyph.source : ""
        icon.color: glyph.tint
        icon.width: width
        icon.height: height
        background: Item {}
    }
}
