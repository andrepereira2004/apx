pragma ComponentBehavior: Bound
import QtQuick

Rectangle {
    id: island
    signal activated()
    readonly property var player: DesktopActivity.state.players.length ? DesktopActivity.state.players[0] : null
    height: 30; radius: 15
    color: pointer.containsMouse ? "#ed343a4d" : (Appearance.tintButtons ? Appearance.barSurface : "#dc202330")
    border.width: 1; border.color: "#304f566c"
    clip: true
    Row {
        anchors.fill: parent; anchors.leftMargin: 10; anchors.rightMargin: 10; spacing: 7
        LucideIcon { name: island.player ? island.player.kind : "music"; width: 17; height: 17; anchors.verticalCenter: parent.verticalCenter }
        Text {
            width: Math.max(0, parent.width - 24); anchors.verticalCenter: parent.verticalCenter
            text: island.player ? island.player.title : ""; textFormat: Text.PlainText
            elide: Text.ElideRight; color: "#d9dcea"; font.family: "JetBrains Mono"; font.pixelSize: 10
        }
    }
    Rectangle {
        anchors.bottom: parent.bottom; anchors.bottomMargin: 2; x: 10
        width: Math.max(0, island.width - 20); height: 2; radius: 1; color: "#455064"
        visible: island.player !== null && island.player.length > 0
        Rectangle { width: parent.width * (island.player && island.player.length > 0 ? DesktopActivity.position(island.player) / island.player.length : 0); height: 2; radius: 1; color: Appearance.iconColor }
    }
    Accessible.role: Accessible.Button
    Accessible.name: "Reprodução atual, " + (player ? player.title : "")
    BounceMouseArea { id: pointer; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: island.activated() }
    Behavior on color { ColorAnimation { duration: 120 } }
}
