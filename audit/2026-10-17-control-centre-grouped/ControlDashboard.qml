pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls

Column {
    id: dashboard
    required property var controller
    readonly property bool brightnessPressed: brightness.pressed
    spacing: 10
    Rectangle {
        width: dashboard.width; height: controls.implicitHeight + 20; radius: 18
        color: dashboard.controller.popupPanel
        border.width: 1; border.color: dashboard.controller.shellBorder
        Column {
            id: controls
            x: 10; y: 10; width: parent.width - 20; spacing: 6
    Item {
        id: dashboardHeader
        width: parent.width; height: 30
        Text { width: parent.width; height: 24; verticalAlignment: Text.AlignVCenter; text: "Central de Controlo"; color: "#e1e5f0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold }
        Rectangle { width: parent.width; height: 1; anchors.bottom: parent.bottom; color: dashboard.controller.controlButtonOutline }
    }
    Column {
        width: parent.width; spacing: 10
        topPadding: 8; bottomPadding: 8
        Text {
            width: parent.width
            text: dashboard.controller.ghostMessage
            textFormat: Text.PlainText; wrapMode: Text.WordWrap
            color: "#d9dcea"; font.family: Appearance.fontFamily
            font.pixelSize: Appearance.bodySize; lineHeight: 1.35
        }
        Text {
            width: parent.width; horizontalAlignment: Text.AlignRight
            text: "- Gosty!"
            color: "#b5bdd0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize
        }
        Rectangle { width: parent.width; height: 1; color: "#414654" }
    }
    Grid {
        width: parent.width; columns: 2; columnSpacing: 6; rowSpacing: 6
        ControlTile { showCaption: true; height: 46; width: (controls.width - 6) / 2; iconName: dashboard.controller.wifiDisplayActive() ? "wifi" : "wifi-off"; caption: "Wi-Fi"; selected: dashboard.controller.wifiDisplayActive(); onActivated: dashboard.controller.openControlSection("wifi") }
        ControlTile { showCaption: true; height: 46; width: (controls.width - 6) / 2; iconName: dashboard.controller.bluetoothDisplayPowered() ? "bluetooth" : "bluetooth-off"; caption: "Bluetooth"; selected: dashboard.controller.bluetoothDisplayPowered(); onActivated: dashboard.controller.openControlSection("bluetooth") }
        ControlTile { showCaption: true; height: 46; width: (controls.width - 6) / 2; iconName: "plane"; caption: "Modo de avião"; selected: dashboard.controller.airplaneMode; enabled: !DesktopActivity.busy; onActivated: DesktopActivity.action(["airplane", dashboard.controller.airplaneMode ? "off" : "on"]) }
        ControlTile { showCaption: true; height: 46; width: (controls.width - 6) / 2; iconName: "settings"; caption: "Mais opções"; onActivated: dashboard.controller.openMoreOptions() }
    }
        }
    }
    Rectangle {
        width: dashboard.width; height: levels.implicitHeight + 20; radius: 18
        color: dashboard.controller.popupPanel
        border.width: 1; border.color: dashboard.controller.shellBorder
        Column {
            id: levels
            x: 10; y: 10; width: parent.width - 20
    Column {
        width: parent.width; spacing: 6
        Row {
            width: parent.width; height: 24; spacing: 8
            LucideIcon { name: dashboard.controller.volumeMuted ? "volume-x" : "volume-2"; width: 18; height: 18; anchors.verticalCenter: parent.verticalCenter }
            Text { text: "Som"; color: Appearance.iconColor; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize; anchors.verticalCenter: parent.verticalCenter }
            Item { width: Math.max(0, parent.width - 112); height: 1 }
            ControlTile { width: 42; height: 24; iconName: "chevron-right"; caption: "Dispositivos de som"; onActivated: dashboard.controller.openControlSection("audio") }
        }
                ControlSlider {
                    id: volume
                    width: parent.width; height: 36
                    from: 0; to: 100; stepSize: 1; activeFocusOnTab: true
                    Accessible.name: "Volume"
                    onMoved: { dashboard.controller.previewVolume(value); if (!pressed) dashboard.controller.commitVolume(value) }
                    onPressedChanged: if (!pressed) dashboard.controller.commitVolume(value)
                    Binding { target: volume; property: "value"; value: dashboard.controller.volumeMuted ? 0 : dashboard.controller.volumeValue; when: !volume.pressed }
                }
        Row {
            width: parent.width; height: 24; spacing: 8
            LucideIcon { name: "sun"; width: 18; height: 18; anchors.verticalCenter: parent.verticalCenter }
            Text { text: "Brilho do ecrã"; color: Appearance.iconColor; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize; anchors.verticalCenter: parent.verticalCenter }
        }
                ControlSlider {
                    id: brightness
                    width: parent.width; height: 36
                    from: 5; to: 100; stepSize: 1; activeFocusOnTab: true
                    Accessible.name: "Brilho do ecrã"
                    onMoved: { dashboard.controller.previewDisplayBrightness(value); if (!pressed) dashboard.controller.commitDisplayBrightness(value) }
                    onPressedChanged: if (!pressed) dashboard.controller.commitDisplayBrightness(value)
                    Binding { target: brightness; property: "value"; value: dashboard.controller.displayBrightness; when: !brightness.pressed }
                }
        Row {
            width: parent.width; spacing: 6
            ControlTile { showCaption: true; height: 42; width: (parent.width - 6) / 2; iconName: dashboard.controller.microphoneMuted ? "mic-off" : "mic"; caption: "Microfone"; selected: !dashboard.controller.microphoneMuted; onActivated: dashboard.controller.openControlSection("microphone") }
            ControlTile { showCaption: true; height: 42; width: (parent.width - 6) / 2; iconName: "keyboard"; caption: "Teclado"; selected: dashboard.controller.keyboardBrightness > 0; onActivated: dashboard.controller.cycleKeyboardBrightness() }
        }
    }
        }
    }
    Rectangle {
        width: dashboard.width; height: sessionActions.implicitHeight + 20; radius: 18
        color: dashboard.controller.popupPanel
        border.width: 1; border.color: dashboard.controller.shellBorder
        Column {
            id: sessionActions
            x: 10; y: 10; width: parent.width - 20; spacing: 6
    Grid {
        width: parent.width; columns: 2; columnSpacing: 6; rowSpacing: 6
        ControlTile { showCaption: true; height: 40; width: (controls.width - 6) / 2; iconName: "lock-keyhole"; caption: "Bloquear"; onActivated: dashboard.controller.runControlAction("lock") }
        ControlTile { showCaption: true; height: 40; width: (controls.width - 6) / 2; iconName: "refresh-cw"; caption: "Atualizar"; onActivated: dashboard.controller.runControlAction("update") }
        ControlTile { showCaption: true; height: 40; width: (controls.width - 6) / 2; iconName: "rotate-cw"; caption: "Reiniciar"; onActivated: dashboard.controller.runControlAction("reboot") }
        ControlTile { showCaption: true; height: 40; width: (controls.width - 6) / 2; iconName: "power"; caption: "Desligar"; onActivated: dashboard.controller.runControlAction("poweroff") }
    }
    Row {
        visible: dashboard.controller.isHub
        width: parent.width; spacing: 6
        ControlTile { showCaption: true; height: 40; width: (parent.width - 6) / 2; iconName: "terminal"; caption: "Terminal do Host"; onActivated: dashboard.controller.runControlAction("terminal") }
        ControlTile { showCaption: true; height: 40; width: (parent.width - 6) / 2; iconName: "log-out"; caption: "Sair para o Host"; onActivated: dashboard.controller.runControlAction("exit") }
    }
        }
    }
    Rectangle {
        width: dashboard.width; height: notifications.implicitHeight + 24; radius: 18
        color: dashboard.controller.popupPanel
        border.width: 1; border.color: dashboard.controller.shellBorder
        ActivityPanel { id: notifications; x: 12; y: 12; width: parent.width - 24; kind: "notifications"; embedded: true }
    }
    Text { visible: DesktopActivity.error.length > 0; width: parent.width; wrapMode: Text.Wrap; text: DesktopActivity.error; color: "#ff9dab"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize }
}
