import QtQuick

Rectangle {
    id: button
    property bool grouped: false
    property string label: ""
    property string iconName: ""
    property int iconSize: 17
    property string alternateIconName: iconName
    property bool compactSymbol: false
    readonly property int labelPixelSize: 13
    property string alternateLabel: label
    property string accessibleLabel: label
    property bool alternateActive: false
    property bool animateActivation: false
    property bool animateDeactivation: false
    property color activeSurface: "#da3a4055"
    property color accentColor: "#f0f0fa"
    property color textColor: "#c8ccdc"
    property int inactiveBorderWidth: 0
    property var hoverOverride: null
    readonly property bool visuallyActive: (hoverOverride === null ? pointer.containsMouse : hoverOverride) || alternateActive
    signal activated()

    implicitWidth: Math.max(36, Math.ceil(Math.max(normalContent.implicitWidth, activeContent.implicitWidth)) + 24)
    implicitHeight: Math.max(32, iconSize + 6)
    scale: pointer.pressed || animateActivation || animateDeactivation ? 0.96 : 1
    radius: 16
    color: visuallyActive ? activeSurface : (grouped ? "transparent" : Appearance.capsuleSurface)
    ButtonOutline {
        selected: button.alternateActive
        hovered: button.visuallyActive
        idleWidth: button.inactiveBorderWidth
    }
    Accessible.role: Accessible.Button
    Accessible.name: accessibleLabel
    Behavior on scale { NumberAnimation { duration: 120; easing.type: Easing.OutCubic } }
    Behavior on color { ColorAnimation { duration: 120 } }

    IconLabel {
        id: normalContent
        anchors.centerIn: parent
        text: button.label
        iconName: button.iconName
        color: button.visuallyActive ? button.accentColor : button.textColor
        pixelSize: button.labelPixelSize
        iconSize: button.iconSize
        opacity: button.alternateActive ? 0 : 1
        Behavior on opacity { NumberAnimation { duration: 110 } }
    }
    IconLabel {
        id: activeContent
        anchors.centerIn: parent
        text: button.alternateLabel
        iconName: button.alternateIconName
        color: button.accentColor
        pixelSize: button.labelPixelSize
        iconSize: button.iconSize
        opacity: button.alternateActive ? 1 : 0
        Behavior on opacity { NumberAnimation { duration: 110 } }
    }
    MouseArea {
        id: pointer
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton
        hoverEnabled: true
        cursorShape: Qt.PointingHandCursor
        onClicked: button.activated()
    }
}
