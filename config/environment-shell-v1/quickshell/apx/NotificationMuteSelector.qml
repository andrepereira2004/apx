import QtQuick
import QtQuick.Controls

ComboBox {
    id: choice
    height: 30
    leftPadding: 9; rightPadding: 24
    background: Rectangle {
        radius: 7; color: choice.pressed ? "#385065" : "#303b4d"
        border.width: choice.activeFocus ? 1 : 0
        border.color: "#8fa3b6"
    }
    contentItem: Text {
        text: choice.displayText; textFormat: Text.PlainText; elide: Text.ElideRight
        verticalAlignment: Text.AlignVCenter; color: "#e9eff7"
        font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize
    }
    indicator: LucideIcon {
        name: "chevron-right"; rotation: 90; width: 14; height: 14
        x: choice.width - width - 7; y: (choice.height - height) / 2
    }
    delegate: ItemDelegate {
        id: option
        required property string modelData
        width: choice.width; height: 30; text: modelData
        font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize
        palette.buttonText: "#e9eff7"
        background: Rectangle { color: option.highlighted ? "#385065" : "#20232d" }
    }
    popup: Popup {
        y: choice.height + 2; width: choice.width
        implicitHeight: Math.min(180, list.contentHeight + 8)
        padding: 4
        contentItem: ListView {
            id: list; clip: true
            model: choice.delegateModel
            currentIndex: choice.highlightedIndex
            ScrollIndicator.vertical: ScrollIndicator { }
        }
        background: Rectangle { radius: 8; color: "#20232d"; border.width: 1; border.color: "#4a5b70" }
    }
}
