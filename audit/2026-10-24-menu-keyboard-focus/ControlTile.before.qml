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
    property bool quiet: false
    property bool attention: false
    property bool iconActionEnabled: false
    property bool iconActionAvailable: true
    property string iconActionLabel: ""
    signal iconActivated()
    signal activated()
    implicitHeight: Appearance.menuActionHeight
    implicitWidth: showCaption ? captionText.implicitWidth + 48 : 48
    radius: Appearance.menuActionRadius
    opacity: enabled ? 1 : .42
    color: quiet ? "#1b1d26" : selected ? (Appearance.tintButtons ? Appearance.active : "#353a4a") : (Appearance.tintButtons ? Appearance.surface : "#1b1d26")
    border.width: 0
    Rectangle {
        visible: tile.showCaption && !tile.iconActionEnabled
        objectName: "controlIconCircle"
        x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter
        width: Appearance.menuIconCircleSize; height: width; radius: width / 2
        color: Qt.lighter(tile.color, 1.6)
    }
    // Keep both transport glyphs behind the shared pointer area.
    LucideIcon { anchors.verticalCenter: parent.verticalCenter; x: tile.showCaption ? Appearance.menuIconInset + (Appearance.menuIconCircleSize - Appearance.menuGlyphSize) / 2 : (parent.width - width) / 2; name: tile.playbackToggle ? "play" : tile.iconName; width: Appearance.menuGlyphSize; height: width; visible: !tile.iconActionEnabled && (!tile.playbackToggle || !tile.playing) }
    LucideIcon { anchors.verticalCenter: parent.verticalCenter; x: tile.showCaption ? Appearance.menuIconInset + (Appearance.menuIconCircleSize - Appearance.menuGlyphSize) / 2 : (parent.width - width) / 2; name: tile.playbackToggle ? "pause" : ""; width: Appearance.menuGlyphSize; height: width; visible: tile.playbackToggle && tile.playing }
    Text { renderType: Text.CurveRendering;
        id: captionText
        visible: tile.showCaption
        x: Appearance.menuLabelInset; width: parent.width - x - 8; anchors.verticalCenter: parent.verticalCenter
        text: tile.caption; elide: Text.ElideRight
        color: Appearance.iconColor; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize
    }
    Rectangle { visible: tile.attention; width: 5; height: 5; radius: 3; color: Appearance.iconColor; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 6 }
    Accessible.role: Accessible.Button
    Accessible.name: caption
    BounceMouseArea { id: mouse; anchors.fill: parent; anchors.leftMargin: tile.iconActionEnabled ? Appearance.menuIconInset + Appearance.menuIconCircleSize : 0; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: tile.activated() }
    RadioIconButton {
        visible: tile.iconActionEnabled
        x: Appearance.menuIconInset; anchors.verticalCenter: parent.verticalCenter
        iconName: tile.iconName
        powered: tile.selected
        busy: !tile.iconActionAvailable
        actionLabel: tile.iconActionLabel
        onActivated: tile.iconActivated()
    }
}
