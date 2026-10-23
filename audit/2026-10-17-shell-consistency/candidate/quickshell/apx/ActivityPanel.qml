pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls

Item {
    id: panel
    property string kind: "media"
    property bool embedded: false
    property bool showBack: !embedded
    readonly property var entries: kind === "media" ? DesktopActivity.state.players.filter(function(p) { return DesktopActivity.hasMedia(p) }) : DesktopActivity.state.notifications.filter(function(n) { return !embedded || n.active })
    // Retain the last visual snapshot until the exit transition finishes.
    property var renderedEntries: []
    property var entryKeys: []
    property bool ready: false
    readonly property bool transitioning: appear.running || disappear.running
    readonly property bool hasContent: kind !== "media" || entries.length > 0
    property real reveal: 0
    property real contentOpacity: 0
    implicitHeight: body.implicitHeight * reveal
    height: implicitHeight
    visible: kind !== "media" || reveal > 0
    clip: kind === "media"
    function syncPresence() {
        if (!ready) return
        appear.stop(); disappear.stop()
        if (kind !== "media") { reveal = 1; contentOpacity = 1 }
        else if (hasContent) appear.start()
        else disappear.start()
    }
    onHasContentChanged: syncPresence()
    ParallelAnimation {
        id: appear
        NumberAnimation { target: panel; property: "reveal"; to: 1; duration: 320; easing.type: Easing.InOutCubic }
        NumberAnimation { target: panel; property: "contentOpacity"; to: 1; duration: 260; easing.type: Easing.InOutQuad }
    }
    SequentialAnimation {
        id: disappear
        NumberAnimation { target: panel; property: "contentOpacity"; to: 0; duration: 220; easing.type: Easing.InOutQuad }
        NumberAnimation { target: panel; property: "reveal"; to: 0; duration: 220; easing.type: Easing.InOutCubic }
    }
    function syncEntries() {
        if (entries.length || kind !== "media") renderedEntries = entries
        var keys = renderedEntries.map(function(entry) { return panel.kind === "media" ? entry.name : String(entry.id) })
        if (JSON.stringify(keys) !== JSON.stringify(entryKeys)) entryKeys = keys
    }
    onEntriesChanged: syncEntries()
    Component.onCompleted: { syncEntries(); ready = true; syncPresence() }
    signal back()
    Column {
        id: body
        width: panel.width
        y: panel.kind === "media" ? 6 * (1 - panel.reveal) : 0
        opacity: panel.contentOpacity
        enabled: panel.kind !== "media" || panel.entries.length > 0
        spacing: 7
    ControlTile { visible: panel.showBack; width: parent.width; iconName: "chevron-left"; caption: "Voltar aos controlos"; onActivated: panel.back() }
    Text {
        width: parent.width; wrapMode: Text.WordWrap
        text: panel.kind === "media" ? (panel.renderedEntries.length ? "Em reprodução" : "Nada em reprodução") : (panel.entries.length ? "Notificações por ler" : "Sem notificações por ler")
        color: "#d9dcea"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize
    }
    Repeater {
        model: panel.entryKeys
        Rectangle {
            id: card
            required property string modelData
            readonly property var entry: panel.renderedEntries.find(function(value) { return (panel.kind === "media" ? value.name : String(value.id)) === card.modelData }) || ({})
            width: panel.width; height: content.implicitHeight + 20; radius: 8
            color: Appearance.tintWindows ? Appearance.surface : "#1b1d26"
            Column {
                id: content
                anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top
                anchors.margins: 10; spacing: 6
                IconLabel { iconName: panel.kind === "media" ? (card.entry.kind || "music") : "bell"; text: panel.kind === "media" ? (card.entry.status === "Playing" ? "A reproduzir" : card.entry.status === "Paused" ? "Em pausa" : "Parado") : (card.entry.app || ""); pixelSize: Appearance.bodySize; iconSize: 16 }
                Text { width: parent.width; wrapMode: Text.WordWrap; text: card.entry.title || ""; textFormat: Text.PlainText; color: "#e1e5f0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize }
                Text { width: parent.width; visible: text.length > 0; wrapMode: Text.WordWrap; text: panel.kind === "media" ? (card.entry.artist || "") : (card.entry.body || ""); textFormat: Text.PlainText; color: "#b5bdd0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize }
                Image {
                    width: 84; height: 84; anchors.horizontalCenter: parent.horizontalCenter
                    visible: panel.kind === "media" && source.toString().length > 0
                    source: panel.kind === "media" ? (card.entry.art_url || "") : ""
                    fillMode: Image.PreserveAspectCrop; asynchronous: true
                }
                MediaTimeline { width: parent.width; visible: panel.kind === "media"; player: card.entry }
                Row {
                    visible: panel.kind === "media"
                    width: parent.width; spacing: 6
                    ControlTile { opacity: 1; width: (parent.width - 12) / 3; iconName: "skip-back"; caption: "Voltar ao início"; enabled: !!card.entry.can_seek && card.entry.length > 0 && !DesktopActivity.busy; onActivated: DesktopActivity.seek(card.entry, 0) }
                    ControlTile {
                        opacity: 1; width: (parent.width - 12) / 3
                        caption: DesktopActivity.playbackIcon(card.entry) === "pause" ? "Pausar" : "Reproduzir"
                        enabled: !!card.entry.can_control
                        onActivated: DesktopActivity.togglePlayback(card.entry)
                        playbackToggle: true
                        playing: DesktopActivity.playbackIcon(card.entry) === "pause"
                    }
                    ControlTile { opacity: 1; width: (parent.width - 12) / 3; iconName: "skip-forward"; caption: "Ir para o fim"; enabled: !!card.entry.can_seek && card.entry.length > 0 && !DesktopActivity.busy; onActivated: DesktopActivity.seek(card.entry, card.entry.length) }
                }
            }
        }
    }
}
}
