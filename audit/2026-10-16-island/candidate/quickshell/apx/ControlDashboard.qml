pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls

Column {
    id: dashboard
    required property var controller
    readonly property bool brightnessPressed: brightness.pressed
    spacing: 6
    Row {
        width: parent.width; spacing: 8
        LucideIcon { name: "ghost"; width: 20; height: 20; anchors.verticalCenter: parent.verticalCenter }
        Text { width: parent.width - 28; text: dashboard.controller.ghostMessage; textFormat: Text.PlainText; wrapMode: Text.WordWrap; color: "#d9dcea"; font.family: "JetBrains Mono"; font.pixelSize: 10; lineHeight: 1.15 }
    }
    Row {
        width: parent.width; spacing: 6
        ControlTile { width: (parent.width - 12) / 3; iconName: dashboard.controller.wifiDisplayActive() ? "wifi" : "wifi-off"; caption: "Wi-Fi"; selected: dashboard.controller.wifiDisplayActive(); onActivated: dashboard.controller.openControlSection("wifi") }
        ControlTile { width: (parent.width - 12) / 3; iconName: dashboard.controller.bluetoothDisplayPowered() ? "bluetooth" : "bluetooth-off"; caption: "Bluetooth"; selected: dashboard.controller.bluetoothDisplayPowered(); onActivated: dashboard.controller.openControlSection("bluetooth") }
        ControlTile { width: (parent.width - 12) / 3; iconName: "plane"; caption: dashboard.controller.airplaneMode ? "Desativar modo de avião" : "Ativar modo de avião"; selected: dashboard.controller.airplaneMode; enabled: !DesktopActivity.busy; onActivated: DesktopActivity.action(["airplane", dashboard.controller.airplaneMode ? "off" : "on"]) }
    }
    Row {
        width: parent.width; spacing: 6
        Column {
            width: parent.width - 48; spacing: 6
            Row {
                width: parent.width; spacing: 6; height: 36
                ControlTile { width: 38; iconName: dashboard.controller.volumeMuted ? "volume-x" : "volume-2"; caption: "Som"; onActivated: dashboard.controller.openControlSection("audio") }
                ControlSlider {
                    id: volume
                    width: parent.width - 44; height: 36
                    from: 0; to: 100; stepSize: 1; activeFocusOnTab: true
                    Accessible.name: "Volume"
                    onMoved: { dashboard.controller.previewVolume(value); if (!pressed) dashboard.controller.commitVolume(value) }
                    onPressedChanged: if (!pressed) dashboard.controller.commitVolume(value)
                    Binding { target: volume; property: "value"; value: dashboard.controller.volumeMuted ? 0 : dashboard.controller.volumeValue; when: !volume.pressed }
                }
            }
            Row {
                width: parent.width; spacing: 6; height: 36
                ControlTile { width: 38; iconName: "sun"; caption: "Brilho do ecrã"; onActivated: brightness.forceActiveFocus() }
                ControlSlider {
                    id: brightness
                    width: parent.width - 44; height: 36
                    from: 5; to: 100; stepSize: 1; activeFocusOnTab: true
                    Accessible.name: "Brilho do ecrã"
                    onMoved: { dashboard.controller.previewDisplayBrightness(value); if (!pressed) dashboard.controller.commitDisplayBrightness(value) }
                    onPressedChanged: if (!pressed) dashboard.controller.commitDisplayBrightness(value)
                    Binding { target: brightness; property: "value"; value: dashboard.controller.displayBrightness; when: !brightness.pressed }
                }
            }
        }
        Column {
            width: 42; spacing: 6
            ControlTile { width: 42; iconName: dashboard.controller.microphoneMuted ? "mic-off" : "mic"; caption: "Microfone"; selected: !dashboard.controller.microphoneMuted; onActivated: dashboard.controller.openControlSection("microphone") }
            ControlTile { width: 42; iconName: "keyboard"; caption: "Iluminação do teclado"; selected: dashboard.controller.keyboardBrightness > 0; onActivated: dashboard.controller.cycleKeyboardBrightness() }
        }
    }
    Row {
        width: parent.width; spacing: 6
        ControlTile {
            width: (parent.width - 6) / 2
            iconName: DesktopActivity.state.players.length ? DesktopActivity.state.players[0].kind : "music"
            caption: DesktopActivity.state.players.length ? DesktopActivity.state.players[0].title : "Reprodução atual"
            selected: DesktopActivity.state.players.length > 0 && DesktopActivity.state.players[0].status === "Playing"
            onActivated: dashboard.controller.openActivitySection("media")
        }
        ControlTile { width: (parent.width - 6) / 2; iconName: "bell"; caption: "Notificações"; attention: DesktopActivity.state.active_notifications > 0; onActivated: dashboard.controller.openActivitySection("notifications") }
    }
    Grid {
        width: parent.width; columns: 4; columnSpacing: 6
        ControlTile { width: (dashboard.width - 18) / 4; iconName: "lock-keyhole"; caption: "Bloquear"; onActivated: dashboard.controller.runControlAction("lock") }
        ControlTile { width: (dashboard.width - 18) / 4; iconName: dashboard.controller.isHub ? "rotate-cw" : "folder"; caption: dashboard.controller.isHub ? "Reiniciar" : "Ficheiros"; onActivated: dashboard.controller.runControlAction("files-or-reboot") }
        ControlTile { width: (dashboard.width - 18) / 4; iconName: "refresh-cw"; caption: "Atualizar"; onActivated: dashboard.controller.runControlAction("update") }
        ControlTile { width: (dashboard.width - 18) / 4; iconName: "power"; caption: "Encerrar"; onActivated: dashboard.controller.runControlAction("poweroff") }
    }
    Row {
        visible: dashboard.controller.isHub
        width: parent.width; spacing: 6
        ControlTile { width: (parent.width - 6) / 2; iconName: "terminal"; caption: "Terminal do Host"; onActivated: dashboard.controller.runControlAction("terminal") }
        ControlTile { width: (parent.width - 6) / 2; iconName: "log-out"; caption: "Sair para o Host"; onActivated: dashboard.controller.runControlAction("exit") }
    }
    ControlTile { width: parent.width; iconName: "settings"; caption: "Mais opções"; onActivated: dashboard.controller.openMoreOptions() }
    Text { visible: DesktopActivity.error.length > 0; width: parent.width; wrapMode: Text.Wrap; text: DesktopActivity.error; color: "#ff9dab"; font.family: "JetBrains Mono"; font.pixelSize: 10 }
}
