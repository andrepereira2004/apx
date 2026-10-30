import QtQuick
import QtQuick.Shapes

Item {
    id: indicator
    property bool active: false
    property real phase: 0
    width: 88; height: 32
    readonly property real inset: 1.5
    readonly property real curveRadius: Math.max(0, (height - 2 * inset) / 2)
    readonly property real straight: Math.max(0, width - height)
    readonly property real perimeter: 2 * straight + 2 * Math.PI * curveRadius
    Accessible.role: Accessible.Graphic
    Accessible.name: "Câmara em utilização"
    // One native polyline follows the capsule without dash restarts at joins.
    Shape {
        id: contour
        objectName: "cameraUsageContour"
        anchors.fill: parent
        function point(distance) {
            var r = indicator.curveRadius, s = indicator.straight
            var d = ((distance % indicator.perimeter) + indicator.perimeter) % indicator.perimeter
            if (d < s) return Qt.point(indicator.inset + r + d, indicator.inset)
            d -= s
            if (d < Math.PI * r) {
                var a = -Math.PI / 2 + d / r
                return Qt.point(indicator.width - indicator.inset - r + r * Math.cos(a), indicator.height / 2 + r * Math.sin(a))
            }
            d -= Math.PI * r
            if (d < s) return Qt.point(indicator.width - indicator.inset - r - d, indicator.height - indicator.inset)
            var b = Math.PI / 2 + (d - s) / r
            return Qt.point(indicator.inset + r + r * Math.cos(b), indicator.height / 2 + r * Math.sin(b))
        }
        function trace(phase) {
            var points = []
            for (var i = 0; i <= 40; ++i)
                points.push(point(indicator.perimeter * (phase + i / 40 * 0.15)))
            return points
        }
        preferredRendererType: Shape.CurveRenderer
        ShapePath {
            strokeColor: "#ffffff"; strokeWidth: 2
            fillColor: "transparent"; capStyle: ShapePath.RoundCap
            joinStyle: ShapePath.RoundJoin
            startX: contour.point(indicator.perimeter * indicator.phase).x
            startY: contour.point(indicator.perimeter * indicator.phase).y
            PathPolyline { path: contour.trace(indicator.phase) }
        }
    }
    NumberAnimation on phase {
        objectName: "cameraContourAnimation"
        from: 0; to: 1; duration: 1800; loops: Animation.Infinite
        running: indicator.active && indicator.visible
    }
}
