pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls

Column {
    id: timeline
    required property var player
    spacing: 4
    Slider {
        id: seek
        width: parent.width; height: 24
        from: 0; to: Math.max(1, Number(timeline.player.length) || 0)
        enabled: timeline.player.can_seek && timeline.player.length > 0
        Accessible.name: "Posição da reprodução"
        Binding { target: seek; property: "value"; value: DesktopActivity.position(timeline.player); when: !seek.pressed }
        onMoved: if (!pressed) DesktopActivity.seek(timeline.player, value)
        onPressedChanged: if (!pressed && enabled) DesktopActivity.seek(timeline.player, value)
        background: Rectangle {
            x: seek.leftPadding; y: (seek.height - height) / 2
            width: seek.availableWidth; height: 4; radius: 2; color: "#455064"
            Rectangle { width: parent.width * seek.visualPosition; height: parent.height; radius: 2; color: Appearance.iconColor }
        }
        handle: Item { width: 0; height: 0 }
    }
    Row {
        width: parent.width
        Text { width: parent.width / 2; text: DesktopActivity.timeLabel(seek.pressed ? seek.value : DesktopActivity.position(timeline.player)); color: "#b5bdd0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize }
        Text { width: parent.width / 2; horizontalAlignment: Text.AlignRight; text: timeline.player.length > 0 ? DesktopActivity.timeLabel(timeline.player.length) : "Em direto"; color: "#b5bdd0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize }
    }
}
