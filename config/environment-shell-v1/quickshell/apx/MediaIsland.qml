pragma ComponentBehavior: Bound
import QtQuick

Rectangle {
    id: island
    signal activated()
    property bool grouped: false
    property bool selected: false
    property var hoverOverride: null
    property bool closingHoverHeld: false
    function beginHoverHandoff(hovered) { closingHoverHeld = hovered }
    function endHoverHandoff() { closingHoverHeld = false }
    onHoverOverrideChanged: {
        if (hoverOverride === null && pointer.containsMouse) endHoverHandoff()
    }
    readonly property bool visuallyHovered: !showingTransient && (closingHoverHeld || (hoverOverride === null ? pointer.containsMouse : hoverOverride))
    property bool cameraUsage: false
    property bool transientActive: false
    property string transientIcon: ""
    property string transientTitle: ""
    property string transientDetail: ""
    property int transientProgress: -1
    readonly property var currentPlayer: DesktopActivity.state.players.find(function(p) { return p.status === "Playing" && DesktopActivity.hasMedia(p) }) || DesktopActivity.state.players.find(function(p) { return DesktopActivity.hasMedia(p) }) || null
    property bool transientSnapshot: false
    readonly property bool showingTransient: transientActive || (currentPlayer === null && transientSnapshot && presence > 0)
    onTransientActiveChanged: if (transientActive) transientSnapshot = true; else if (currentPlayer) transientSnapshot = false
    property var player: null
    property real presence: currentPlayer !== null || transientActive || selected ? 1 : 0
    onCurrentPlayerChanged: if (currentPlayer) { player = currentPlayer; if (!transientActive) transientSnapshot = false }
    Component.onCompleted: if (currentPlayer) player = currentPlayer
    opacity: presence
    enabled: !showingTransient
    Behavior on presence { NumberAnimation { duration: 320; easing.type: Easing.InOutCubic } }
    height: 32; radius: 16
    color: visuallyHovered || selected ? "#f2292d3a" : grouped ? "transparent" : Appearance.capsuleSurface
    ButtonOutline {
        selected: island.selected
        hovered: island.visuallyHovered
    }
    CameraIndicator {
        anchors.fill: parent
        active: island.cameraUsage && island.transientActive
        visible: active
    }
    clip: false
    readonly property bool compact: selected && !showingTransient
    readonly property string displayTitle: {
        if (showingTransient) {
            if (transientProgress < 0) return ""
            var percentage = transientDetail.match(/\d+%/)
            return percentage ? percentage[0] : Math.max(0, Math.min(100, transientProgress)) + "%"
        }
        return compact ? "" : (player ? player.title : "")
    }
    readonly property real summaryWidth: summary.width
    readonly property real summaryX: summary.x
    Row {
        id: summary
        anchors.centerIn: parent
        spacing: island.compact || !summaryText.visible ? 0 : 5
        Item {
            width: 17; height: 17; anchors.verticalCenter: parent.verticalCenter
            LucideIcon { anchors.fill: parent; name: "audio-lines"; visible: !island.showingTransient }
            ControlIcon { anchors.fill: parent; source: island.transientIcon; tint: Appearance.iconColor; visible: island.showingTransient && !island.cameraUsage }
            LucideIcon {
                anchors.fill: parent
                name: "camera"
                visible: island.cameraUsage && island.transientActive
            }
        }
        Text { renderType: Text.CurveRendering;
            id: summaryText
            visible: !island.compact && text.length > 0
            width: island.showingTransient ? 36 : Math.min(implicitWidth, Math.max(0, island.width - 38))
            anchors.verticalCenter: parent.verticalCenter
            horizontalAlignment: island.showingTransient ? Text.AlignRight : Text.AlignLeft
            text: island.displayTitle; textFormat: Text.PlainText
            elide: Text.ElideRight; color: "#d9dcea"; font.family: Appearance.fontFamily; font.pixelSize: 13
        }
    }
    Rectangle {
        objectName: "mediaPreviewProgress"
        anchors.bottom: parent.bottom; anchors.bottomMargin: 2; x: 18
        width: Math.max(0, island.width - 36); height: 2; radius: 1; color: "#455064"
        visible: !island.showingTransient && !island.compact && island.player !== null && island.player.length > 0
        Rectangle {
            width: parent.width * (island.player && island.player.length > 0 ? DesktopActivity.position(island.player) / island.player.length : 0)
            height: 2; radius: 1; color: Appearance.iconColor
        }
    }
    Accessible.role: showingTransient ? Accessible.StaticText : Accessible.Button
    Accessible.name: showingTransient ? transientTitle + " " + transientDetail : "Reprodução atual, " + (player ? player.title : "")
    BounceMouseArea {
        id: pointer
        menuFeedbackEnabled: false; pressAnimationEnabled: false
        anchors.fill: parent
        enabled: island.selected || island.currentPlayer !== null
        hoverEnabled: true; cursorShape: Qt.PointingHandCursor
        onEntered: { if (island.hoverOverride === null) island.endHoverHandoff() }
        onExited: { if (island.hoverOverride === null) island.endHoverHandoff() }
        onClicked: island.activated()
    }
}
