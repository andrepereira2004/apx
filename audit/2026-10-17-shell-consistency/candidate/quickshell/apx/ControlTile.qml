import QtQuick
import QtQuick.Controls

Rectangle {
    id: tile
    property string iconName: ""
    property bool playbackToggle: false
    property bool playing: false
    property string caption: ""
    property bool selected: false
    property bool attention: false
    signal activated()
    implicitHeight: 36
    implicitWidth: 48
    radius: 9
    opacity: enabled ? 1 : .42
    color: selected ? (Appearance.tintButtons ? Appearance.active : "#353a4a") : (Appearance.tintButtons ? Appearance.surface : "#1b1d26")
    border.width: selected || mouse.containsMouse ? 1 : 0
    border.color: "#9da8c2"
    // Keep both transport glyphs behind the shared pointer area.
    LucideIcon { anchors.centerIn: parent; name: tile.playbackToggle ? "play" : tile.iconName; width: 16; height: 16; visible: !tile.playbackToggle || !tile.playing }
    LucideIcon { anchors.centerIn: parent; name: tile.playbackToggle ? "pause" : ""; width: 16; height: 16; visible: tile.playbackToggle && tile.playing }
    Rectangle { visible: tile.attention; width: 5; height: 5; radius: 3; color: Appearance.iconColor; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 6 }
    Accessible.role: Accessible.Button
    Accessible.name: caption
    BounceMouseArea { id: mouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: tile.activated() }
}
