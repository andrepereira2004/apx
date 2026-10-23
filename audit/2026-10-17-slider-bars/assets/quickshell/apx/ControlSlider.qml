import QtQuick
import QtQuick.Controls

Slider {
    id: slider
    background: Rectangle {
        x: slider.leftPadding; y: (slider.height - height) / 2
        width: slider.availableWidth; height: 6; radius: 3
        color: "#455064"
        Rectangle { width: parent.width * slider.visualPosition; height: parent.height; radius: 3; color: Appearance.iconColor }
    }
    handle: Item { width: 0; height: 0 }
}
