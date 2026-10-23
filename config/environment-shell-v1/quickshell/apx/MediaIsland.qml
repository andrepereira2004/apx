pragma ComponentBehavior: Bound
import QtQuick

Rectangle {
    id: island
    signal activated()
    property bool grouped: false
    property bool selected: false
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
    color: pointer.containsMouse || selected ? "#f2292d3a" : grouped ? "transparent" : Appearance.capsuleSurface
    border.width: selected || !grouped ? 1 : 0; border.color: selected ? Appearance.iconColor : "#304f566c"
    clip: true
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
            ControlIcon { anchors.fill: parent; source: island.transientIcon; tint: Appearance.iconColor; visible: island.showingTransient }
        }
        Text {
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
        anchors.bottom: parent.bottom; anchors.bottomMargin: 2; x: 10
        width: Math.max(0, island.width - 20); height: 2; radius: 1; color: "#455064"
        visible: !island.showingTransient && !island.compact && island.player !== null && island.player.length > 0
        Rectangle {
            width: parent.width * (island.player && island.player.length > 0 ? DesktopActivity.position(island.player) / island.player.length : 0)
            height: 2; radius: 1; color: Appearance.iconColor
        }
    }
    Accessible.role: showingTransient ? Accessible.StaticText : Accessible.Button
    Accessible.name: showingTransient ? transientTitle + " " + transientDetail : "Reprodução atual, " + (player ? player.title : "")
    BounceMouseArea { id: pointer; anchors.fill: parent; enabled: island.selected || island.currentPlayer !== null; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: island.activated() }
    Behavior on color { ColorAnimation { duration: 120 } }
}
