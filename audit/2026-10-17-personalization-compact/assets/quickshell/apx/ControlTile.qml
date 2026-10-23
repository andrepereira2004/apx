import QtQuick
import QtQuick.Controls

Rectangle {
    id: tile
    property string iconName: ""
    property bool playbackToggle: false
    property bool playing: false
    property bool showCaption: false
    property string caption: ""
    property bool selected: false
    property bool attention: false
    signal activated()
    implicitHeight: 36
    implicitWidth: showCaption ? captionText.implicitWidth + 48 : 48
    radius: 9
    opacity: enabled ? 1 : .42
    color: selected ? (Appearance.tintButtons ? Appearance.active : "#353a4a") : (Appearance.tintButtons ? Appearance.surface : "#1b1d26")
    border.width: selected || mouse.containsMouse ? 1 : 0
    border.color: "#9da8c2"
    // Keep both transport glyphs behind the shared pointer area.
    LucideIcon { anchors.verticalCenter: parent.verticalCenter; x: tile.showCaption ? 12 : (parent.width - width) / 2; name: tile.playbackToggle ? "play" : tile.iconName; width: 16; height: 16; visible: !tile.playbackToggle || !tile.playing }
    LucideIcon { anchors.verticalCenter: parent.verticalCenter; x: tile.showCaption ? 12 : (parent.width - width) / 2; name: tile.playbackToggle ? "pause" : ""; width: 16; height: 16; visible: tile.playbackToggle && tile.playing }
    Text {
        id: captionText
        visible: tile.showCaption
        x: 36; width: parent.width - 44; anchors.verticalCenter: parent.verticalCenter
        text: tile.caption; elide: Text.ElideRight
        color: Appearance.iconColor; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize
    }
    Rectangle { visible: tile.attention; width: 5; height: 5; radius: 3; color: Appearance.iconColor; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 6 }
    Accessible.role: Accessible.Button
    Accessible.name: caption
    BounceMouseArea { id: mouse; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: tile.activated() }
}
