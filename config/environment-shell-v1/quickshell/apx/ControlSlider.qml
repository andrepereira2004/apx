import QtQuick
import QtQuick.Controls

Slider {
    id: slider
    activeFocusOnTab: true
    Keys.priority: Keys.BeforeItem
    Keys.onPressed: function(event) {
        if (event.key !== Qt.Key_Left && event.key !== Qt.Key_Right) return
        const direction = event.key === Qt.Key_Right ? 1 : -1
        value = Math.max(from, Math.min(to, Math.round(value) + direction * (event.modifiers & Qt.ShiftModifier ? 5 : 1)))
        moved()
        event.accepted = true
    }
    background: Rectangle {
        x: slider.leftPadding; y: (slider.height - height) / 2
        width: slider.availableWidth; height: 6; radius: 3
        color: "#455064"
        Rectangle { width: parent.width * slider.visualPosition; height: parent.height; radius: 3; color: Appearance.iconColor }
    }
    handle: Item { width: 0; height: 0 }
}
