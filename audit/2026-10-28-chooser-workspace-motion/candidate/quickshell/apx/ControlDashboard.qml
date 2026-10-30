pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import "NotificationGroups.js" as NotificationGroups

Column {
    id: dashboard
    required property var controller
    property real displayScale: 1
    property real topCornerRadius: Appearance.desktopCornerRadius
    readonly property real outlineWidth: Math.max(1, Math.round(displayScale)) / displayScale
    readonly property real topCardHeight: dashboardContent.implicitHeight + 2 * buttonSpacing
    readonly property int buttonSpacing: 8
    readonly property int pairedButtonSpacing: 6
    component DashboardCard: Rectangle {
        id: card
        property bool showInsetOutline: true
        color: dashboard.controller.popupPanel
        antialiasing: true
        Rectangle {
            visible: card.showInsetOutline
            anchors.fill: parent
            anchors.margins: 1 / dashboard.displayScale
            radius: Math.max(0, card.radius - anchors.margins)
            color: "transparent"
            antialiasing: true
            border.pixelAligned: false
            border.width: dashboard.outlineWidth
            border.color: dashboard.controller.shellBorder
            z: 100
        }
    }
    readonly property bool brightnessPressed: false
    spacing: buttonSpacing
    DashboardCard {
        showInsetOutline: false
        width: dashboard.width
        height: dashboard.topCardHeight
        radius: dashboard.topCornerRadius
        Column {
            id: dashboardContent
            x: dashboard.buttonSpacing
            y: dashboard.buttonSpacing
            width: parent.width - 2 * dashboard.buttonSpacing
            spacing: dashboard.buttonSpacing
            Item {
                width: parent.width; height: 30
                Text { renderType: Text.QtRendering; x: Appearance.menuTitleInset; width: parent.width - x; height: 24; verticalAlignment: Text.AlignVCenter; text: "Central de Controlo"; color: "#e1e5f0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold }
                Rectangle { width: parent.width; height: 1; anchors.bottom: parent.bottom; color: dashboard.controller.controlButtonOutline }
            }
            ControlTile {
                width: parent.width; height: Appearance.menuActionHeight
                iconName: "satellite-dish"; caption: "Ligações"; showCaption: true
                onActivated: dashboard.controller.openControlSection("connectivity")
                Row {
                    anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; spacing: 10
                    LucideIcon { name: dashboard.controller.wifiDisplayActive() ? "wifi" : "wifi-off"; width: Appearance.menuGlyphSize; height: width; opacity: dashboard.controller.wifiDisplayActive() ? 1 : .4 }
                    LucideIcon { name: "bluetooth"; width: Appearance.menuGlyphSize; height: width; opacity: dashboard.controller.bluetoothDisplayPowered() ? 1 : .4 }
                    LucideIcon { name: "plane"; width: Appearance.menuGlyphSize; height: width; opacity: dashboard.controller.airplaneMode ? 1 : .4 }
                    LucideIcon { name: "chevron-right"; width: Appearance.menuGlyphSize; height: width }
                }
            }
            ControlTile {
                width: parent.width; height: Appearance.menuActionHeight
                iconName: "volume-2"; caption: "Som e Brilho"; showCaption: true
                onActivated: dashboard.controller.openControlSection("brightness")
                Row {
                    anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter; spacing: 10
                    LucideIcon { name: dashboard.controller.volumeMuted ? "volume-x" : "volume-2"; width: Appearance.menuGlyphSize; height: width; opacity: dashboard.controller.volumeMuted ? .4 : 1 }
                    LucideIcon { name: "sun"; width: Appearance.menuGlyphSize; height: width }
                    LucideIcon { name: "chevron-right"; width: Appearance.menuGlyphSize; height: width }
                }
            }
            ControlTile {
                width: parent.width; height: Appearance.menuActionHeight
                iconName: "settings"; caption: "Mais opções"; showCaption: true
                onActivated: dashboard.controller.openMoreOptions()
                LucideIcon { name: "chevron-right"; width: Appearance.menuGlyphSize; height: width; anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter }
            }
            Grid {
                width: parent.width; columns: 2
                columnSpacing: dashboard.pairedButtonSpacing; rowSpacing: dashboard.buttonSpacing
                ControlTile { showCaption: true; height: Appearance.menuActionHeight; width: (parent.width - dashboard.pairedButtonSpacing) / 2; iconName: "lock-keyhole"; caption: "Bloquear"; onActivated: dashboard.controller.runControlAction("lock") }
                ControlTile { showCaption: true; height: Appearance.menuActionHeight; width: (parent.width - dashboard.pairedButtonSpacing) / 2; iconName: "refresh-cw"; caption: "Atualizar"; onActivated: dashboard.controller.runControlAction("update") }
                ControlTile { showCaption: true; height: Appearance.menuActionHeight; width: (parent.width - dashboard.pairedButtonSpacing) / 2; iconName: "rotate-cw"; caption: "Reiniciar"; onActivated: dashboard.controller.runControlAction("reboot") }
                ControlTile { showCaption: true; height: Appearance.menuActionHeight; width: (parent.width - dashboard.pairedButtonSpacing) / 2; iconName: "power"; caption: "Desligar"; onActivated: dashboard.controller.runControlAction("poweroff") }
            }
            ControlTile {
                id: notificationShortcut
                objectName: "notificationShortcut"
                width: parent.width; height: Appearance.menuActionHeight
                showOutline: false
                iconName: "bell"; showCaption: true
                caption: NotificationGroups.unreadLabel(DesktopActivity.notificationEntries.length)
                onActivated: dashboard.controller.openActivitySection("notifications")
                LucideIcon {
                    name: "chevron-right"; width: Appearance.menuGlyphSize; height: width
                    anchors.right: parent.right; anchors.rightMargin: 12; anchors.verticalCenter: parent.verticalCenter
                }
            }
        }
    }
    Text { renderType: Text.QtRendering; visible: DesktopActivity.error.length > 0; width: parent.width; wrapMode: Text.Wrap; text: DesktopActivity.error; color: "#ff9dab"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize }
}
