pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls

Column {
    id: panel
    property string kind: "media"
    signal back()
    spacing: 7
    ControlTile { width: parent.width; iconName: "chevron-left"; caption: "Voltar aos controlos"; onActivated: panel.back() }
    Text {
        width: parent.width; wrapMode: Text.WordWrap
        text: panel.kind === "media" ? (DesktopActivity.state.players.length ? "Em reprodução" : "Nada em reprodução") : (DesktopActivity.state.notifications.length ? "Notificações e histórico" : "Sem notificações")
        color: "#d9dcea"; font.family: "JetBrains Mono"; font.pixelSize: 12
    }
    Repeater {
        model: panel.kind === "media" ? DesktopActivity.state.players : DesktopActivity.state.notifications
        Rectangle {
            id: card
            required property var modelData
            width: panel.width; height: content.implicitHeight + 20; radius: 8
            color: Appearance.tintWindows ? Appearance.surface : "#303445"
            Column {
                id: content
                anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top
                anchors.margins: 10; spacing: 6
                IconLabel { iconName: panel.kind === "media" ? card.modelData.kind : "bell"; text: panel.kind === "media" ? (card.modelData.status === "Playing" ? "A reproduzir" : card.modelData.status === "Paused" ? "Em pausa" : "Parado") : card.modelData.app; pixelSize: 10; iconSize: 16 }
                Text { width: parent.width; wrapMode: Text.WordWrap; text: card.modelData.title || ""; textFormat: Text.PlainText; color: "#e1e5f0"; font.family: "JetBrains Mono"; font.pixelSize: 11 }
                Text { width: parent.width; visible: text.length > 0; wrapMode: Text.WordWrap; text: panel.kind === "media" ? (card.modelData.artist || "") : (card.modelData.body || ""); textFormat: Text.PlainText; color: "#b5bdd0"; font.family: "JetBrains Mono"; font.pixelSize: 10 }
                Image {
                    width: 84; height: 84; anchors.horizontalCenter: parent.horizontalCenter
                    visible: panel.kind === "media" && source.toString().length > 0
                    source: panel.kind === "media" ? (card.modelData.art_url || "") : ""
                    fillMode: Image.PreserveAspectCrop; asynchronous: true
                }
                MediaTimeline { width: parent.width; visible: panel.kind === "media"; player: card.modelData }
                Row {
                    visible: panel.kind === "media"
                    width: parent.width; spacing: 6
                    ControlTile { width: (parent.width - 12) / 3; iconName: "skip-back"; caption: "Anterior"; enabled: !!card.modelData.can_previous; onActivated: DesktopActivity.action(["media", card.modelData.name, "previous"]) }
                    ControlTile { width: (parent.width - 12) / 3; iconName: card.modelData.status === "Playing" ? "pause" : "play"; caption: "Reproduzir ou pausar"; enabled: !!card.modelData.can_control; onActivated: DesktopActivity.action(["media", card.modelData.name, "play-pause"]) }
                    ControlTile { width: (parent.width - 12) / 3; iconName: "skip-forward"; caption: "Seguinte"; enabled: !!card.modelData.can_next; onActivated: DesktopActivity.action(["media", card.modelData.name, "next"]) }
                }
            }
        }
    }
}
