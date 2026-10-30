pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls

Column {
    id: dashboard
    required property var controller
    readonly property bool brightnessPressed: false
    spacing: 8
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
    ControlTile {
        width: parent.width; height: 64; radius: 14
        iconName: "satellite-dish"; caption: "Ligações"; showCaption: true
        onActivated: dashboard.controller.openControlSection("connectivity")
        Row {
            anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; spacing: 10
            LucideIcon { name: dashboard.controller.wifiDisplayActive() ? "wifi" : "wifi-off"; width: 16; height: 16; opacity: dashboard.controller.wifiDisplayActive() ? 1 : .4 }
            LucideIcon { name: "bluetooth"; width: 16; height: 16; opacity: dashboard.controller.bluetoothDisplayPowered() ? 1 : .4 }
            LucideIcon { name: "plane"; width: 16; height: 16; opacity: dashboard.controller.airplaneMode ? 1 : .4 }
            LucideIcon { name: "chevron-right"; width: 16; height: 16 }
        }
    }
        ControlTile {
            width: parent.width; height: 64; radius: 14
            iconName: "volume-2"; caption: "Som e brilho"; showCaption: true
            onActivated: dashboard.controller.openControlSection("brightness")
            Row {
                anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; spacing: 10
                LucideIcon { name: dashboard.controller.volumeMuted ? "volume-x" : "volume-2"; width: 16; height: 16; opacity: dashboard.controller.volumeMuted ? .4 : 1 }
                LucideIcon { name: "sun"; width: 16; height: 16 }
                LucideIcon { name: "chevron-right"; width: 16; height: 16 }
            }
        }
        ControlTile {
            width: parent.width; height: 64; radius: 14
            iconName: "settings"; caption: "Mais opções"; showCaption: true
            onActivated: dashboard.controller.openMoreOptions()
            LucideIcon { name: "chevron-right"; width: 16; height: 16; anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter }
        }
        }
    }
    Rectangle {
        width: dashboard.width; height: sessionActions.implicitHeight + 20; radius: 18
        color: dashboard.controller.popupPanel
        border.width: 1; border.color: dashboard.controller.shellBorder
        Column {
            id: sessionActions
            x: 10; y: 10; width: parent.width - 20; spacing: 8
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
