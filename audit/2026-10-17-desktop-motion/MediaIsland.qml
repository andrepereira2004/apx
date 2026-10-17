pragma ComponentBehavior: Bound
import QtQuick

Rectangle {
    id: island
    signal activated()
    property bool transientActive: false
    property string transientIcon: ""
    property string transientTitle: ""
    property string transientDetail: ""
    property int transientProgress: -1
    property real expandedAmount: 0
    readonly property var currentPlayer: DesktopActivity.state.players.find(function(p) { return p.status === "Playing" && DesktopActivity.hasMedia(p) }) || DesktopActivity.state.players.find(function(p) { return DesktopActivity.hasMedia(p) }) || null
    property bool transientSnapshot: false
    readonly property bool showingTransient: transientActive || (currentPlayer === null && transientSnapshot && presence > 0)
    onTransientActiveChanged: if (transientActive) transientSnapshot = true; else if (currentPlayer) transientSnapshot = false
    property var player: null
    property real presence: currentPlayer !== null || transientActive ? 1 : 0
    onCurrentPlayerChanged: if (currentPlayer) { player = currentPlayer; if (!transientActive) transientSnapshot = false }
    Component.onCompleted: if (currentPlayer) player = currentPlayer
    opacity: presence * (1 - expandedAmount)
    Behavior on presence { NumberAnimation { duration: 320; easing.type: Easing.InOutCubic } }
    height: 32; radius: 16
    color: pointer.containsMouse ? "#ed343a4d" : (Appearance.tintButtons ? Appearance.barSurface : "#dc202330")
    border.width: 1; border.color: "#304f566c"
    clip: true
    readonly property bool hasArtwork: !showingTransient && artwork.status === Image.Ready
    readonly property string displayTitle: showingTransient ? transientTitle + (transientDetail.length ? " · " + transientDetail : "") : (player ? player.title : "")
    Row {
        anchors.fill: parent; anchors.leftMargin: 10; anchors.rightMargin: 10; spacing: 7
        Item {
            width: 18; height: 18; anchors.verticalCenter: parent.verticalCenter
            Image {
                id: artwork
                anchors.fill: parent
                source: island.player ? (island.player.art_url || "") : ""
                sourceSize.width: 36; sourceSize.height: 36
                fillMode: Image.PreserveAspectCrop; asynchronous: true
                visible: island.hasArtwork
            }
            LucideIcon { anchors.centerIn: parent; name: island.player ? island.player.kind : "music"; width: 17; height: 17; visible: !island.showingTransient && !island.hasArtwork }
            ControlIcon { anchors.fill: parent; source: island.transientIcon; tint: Appearance.iconColor; visible: island.showingTransient }
        }
        Text {
            width: Math.max(0, parent.width - 42); anchors.verticalCenter: parent.verticalCenter
            text: island.displayTitle; textFormat: Text.PlainText
            elide: Text.ElideRight; color: "#d9dcea"; font.family: "JetBrains Mono"; font.pixelSize: 13
        }
        Rectangle {
            width: 4; height: island.player && island.player.status === "Playing" ? 10 : 4
            anchors.verticalCenter: parent.verticalCenter; radius: 2
            visible: !island.showingTransient && island.currentPlayer !== null
            color: Appearance.iconColor
            opacity: island.player && island.player.status === "Playing" ? 1 : 0.45
            Behavior on height { NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }
            Behavior on opacity { NumberAnimation { duration: 180 } }
        }
    }
    Rectangle {
        anchors.bottom: parent.bottom; anchors.bottomMargin: 2; x: 10
        width: Math.max(0, island.width - 20); height: 2; radius: 1; color: "#455064"
        visible: island.showingTransient ? island.transientProgress >= 0 : island.player !== null && island.player.length > 0
        Rectangle {
            width: parent.width * (island.showingTransient ? Math.max(0, Math.min(100, island.transientProgress)) / 100 : (island.player && island.player.length > 0 ? DesktopActivity.position(island.player) / island.player.length : 0))
            height: 2; radius: 1; color: Appearance.iconColor
            Behavior on width { enabled: island.transientActive; NumberAnimation { duration: 90; easing.type: Easing.OutCubic } }
        }
    }
    Accessible.role: transientActive ? Accessible.StaticText : Accessible.Button
    Accessible.name: transientActive ? displayTitle : "Reprodução atual, " + (player ? player.title : "")
    BounceMouseArea { id: pointer; anchors.fill: parent; enabled: !island.showingTransient && island.currentPlayer !== null; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: island.activated() }
    Behavior on color { ColorAnimation { duration: 120 } }
}
