import QtQuick

Rectangle {
    id: button

    property string label: ""
    property bool compactSymbol: false
    readonly property int labelPixelSize: 14
    property string alternateLabel: ""
    property bool alternateActive: false
    property bool animateActivation: false
    property bool animateDeactivation: false
    property color activeSurface
    property color hoverBorderColor: "#879196"
    property color accentColor
    property color textColor
    property int activeBorderWidth: 1
    // The popup owns pointer input while open and forwards its bar hit test.
    property var hoverOverride: null
    readonly property bool visuallyActive: (hoverOverride === null ? pointer.containsMouse : hoverOverride) || alternateActive

    signal activated()

    implicitWidth: button.compactSymbol ? 44 : Math.ceil(Math.max(buttonText.implicitWidth, alternateButtonText.implicitWidth)) + 24
    implicitHeight: 32
    scale: pointer.pressed || button.animateActivation || button.animateDeactivation ? 0.96 : 1
    radius: 7
    color: visuallyActive ? activeSurface : "transparent"
    border.width: visuallyActive ? button.activeBorderWidth : 0
    border.color: alternateActive ? accentColor : hoverBorderColor

    Behavior on scale {
        NumberAnimation { duration: 120; easing.type: Easing.OutCubic }
    }

    Text {
        id: buttonText
        visible: !button.compactSymbol
        anchors.horizontalCenter: parent.horizontalCenter
        y: (button.height - labelInk.tightBoundingRect.height) / 2 - labelInk.tightBoundingRect.y - baselineOffset
        TextMetrics {
            id: labelInk
            font: buttonText.font
            text: buttonText.text
        }
        text: button.label
        opacity: button.alternateActive ? 0 : 1
        scale: button.alternateActive ? 0.94 : 1
        color: button.visuallyActive ? button.accentColor : button.textColor
        font.family: "Selawik"
        font.pixelSize: button.labelPixelSize
        font.weight: Font.DemiBold
        font.letterSpacing: 0.3

        Behavior on opacity {
            enabled: button.animateActivation || button.animateDeactivation
            NumberAnimation { duration: 110; easing.type: Easing.OutCubic }
        }
        Behavior on scale {
            enabled: button.animateActivation || button.animateDeactivation
            NumberAnimation { duration: 130; easing.type: Easing.OutCubic }
        }
    }

    Text {
        id: alternateButtonText
        visible: !button.compactSymbol
        anchors.horizontalCenter: parent.horizontalCenter
        y: (button.height - alternateInk.tightBoundingRect.height) / 2 - alternateInk.tightBoundingRect.y - baselineOffset
        TextMetrics {
            id: alternateInk
            font: alternateButtonText.font
            text: alternateButtonText.text
        }
        text: button.alternateLabel
        opacity: button.alternateActive ? 1 : 0
        scale: button.alternateActive ? 1 : 0.94
        color: button.visuallyActive ? button.accentColor : button.textColor
        font.family: "Selawik"
        font.pixelSize: button.labelPixelSize
        font.weight: Font.DemiBold
        font.letterSpacing: 0.3

        Behavior on opacity {
            enabled: button.animateActivation || button.animateDeactivation
            NumberAnimation { duration: 110; easing.type: Easing.OutCubic }
        }
        Behavior on scale {
            enabled: button.animateActivation || button.animateDeactivation
            NumberAnimation { duration: 130; easing.type: Easing.OutCubic }
        }
    }

    // Centre the visible ink, including the pipe's descender, in equal cells.
    // Keep the owner's literal [|] / [A] labels and their existing crossfade.
    component SymbolLabel: Item {
        property string glyphs
        width: 26
        height: 20
        Repeater {
            model: 3
            delegate: Text {
                id: glyph
                required property int index
                text: parent.glyphs.charAt(index)
                font.family: "Selawik"
                font.pixelSize: button.labelPixelSize
                font.weight: Font.DemiBold
                color: button.visuallyActive ? button.accentColor : button.textColor
                x: index * 9 + (8 - ink.tightBoundingRect.width) / 2 - ink.tightBoundingRect.x
                y: (20 - ink.tightBoundingRect.height) / 2 - ink.tightBoundingRect.y - baselineOffset
                TextMetrics {
                    id: ink
                    font: glyph.font
                    text: glyph.text
                }
            }
        }
    }
    SymbolLabel {
        anchors.centerIn: parent
        visible: button.compactSymbol
        glyphs: button.label
        opacity: buttonText.opacity
        scale: buttonText.scale
    }
    SymbolLabel {
        anchors.centerIn: parent
        visible: button.compactSymbol
        glyphs: button.alternateLabel
        opacity: alternateButtonText.opacity
        scale: alternateButtonText.scale
    }

    MouseArea {
        id: pointer
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor

        // Finish the click on the permanently mapped bar before the menu
        // changes keyboard focus or layer-shell input regions.
        onClicked: button.activated()
    }
}
