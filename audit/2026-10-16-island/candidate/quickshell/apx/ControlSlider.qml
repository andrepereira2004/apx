import QtQuick
import QtQuick.Controls

Slider {
    id: slider
    background: Rectangle {
        x: slider.leftPadding; y: (slider.height - height) / 2
        width: slider.availableWidth; height: 4; radius: 2
        color: "#455064"
        Rectangle { width: parent.width * slider.visualPosition; height: parent.height; radius: 2; color: Appearance.iconColor }
    }
    handle: Rectangle {
        x: slider.leftPadding + slider.visualPosition * (slider.availableWidth - width)
        y: (slider.height - height) / 2
        width: slider.pressed ? 12 : 9; height: width; radius: width / 2
        color: Appearance.iconColor
        Behavior on width { NumberAnimation { duration: 100 } }
    }
}
