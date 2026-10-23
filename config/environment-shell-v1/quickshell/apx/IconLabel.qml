import QtQuick

Item {
    id: label
    property string text: ""
    property string iconName: ""
    property color color: "#d5d8e5"
    property int pixelSize: Appearance.bodySize
    property int iconSize: 17
    property bool stacked: false
    readonly property int gap: text.length && iconName.length ? (stacked ? 4 : 7) : 0
    readonly property int imageWidth: iconName.length ? iconSize : 0
    implicitWidth: stacked ? Math.max(imageWidth, caption.implicitWidth) : imageWidth + gap + caption.implicitWidth
    implicitHeight: stacked ? imageWidth + gap + caption.implicitHeight : Math.max(imageWidth, caption.implicitHeight)
    LucideIcon {
        visible: label.iconName.length > 0
        name: label.iconName
        tint: Appearance.iconColor
        width: label.iconSize; height: width
        x: label.stacked ? (label.width - width) / 2 : 0
        y: label.stacked ? 0 : (label.height - height) / 2
    }
    Text {
        id: caption
        text: label.text
        color: label.color
        font.family: Appearance.fontFamily
        font.pixelSize: label.pixelSize
        font.weight: Font.Normal
        x: label.stacked ? (label.width - width) / 2 : label.imageWidth + label.gap
        y: label.stacked ? label.imageWidth + label.gap : (label.height - height) / 2
    }
}
