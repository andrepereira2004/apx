pragma ComponentBehavior: Bound
import QtQuick
import Quickshell
import "NotificationGroups.js" as Groups

Column {
    id: inbox
    property var notes: DesktopActivity.notificationEntries
    readonly property bool continuousScrollContent: true
    property var groups: []
    property var groupKeys: []
    property var expandedApps: ({})
    readonly property var desktopApplications: DesktopEntries.applications.values
    spacing: 8
    move: Transition { NumberAnimation { properties: "x,y"; duration: 280; easing.type: Easing.OutCubic } }
    add: Transition { NumberAnimation { property: "opacity"; from: 0; to: 1; duration: 200 } }
    function rebuild() {
        groups = Groups.build(notes)
        var keys = groups.map(function(g) { return g.key })
        if (JSON.stringify(keys) !== JSON.stringify(groupKeys)) groupKeys = keys
    }
    function toggleApp(key) {
        var next = Object.assign({}, expandedApps)
        next[key] = !next[key]
        expandedApps = next
    }
    function iconFor(group) {
        var applications = desktopApplications
        var note = group.notes.find(function(n) { return !!n.icon || !!n.desktop_entry }) || group.notes[0] || ({})
        var icon = String(note.icon || "")
        if (icon.length) {
            if (icon.startsWith("file://")) return icon
            if (icon.startsWith("/")) return "file://" + icon
            var supplied = Quickshell.iconPath(icon, true)
            if (supplied.length) return supplied
        }
        var entryId = String(note.desktop_entry || "")
        var entry = entryId ? (DesktopEntries.byId(entryId) || DesktopEntries.byId(entryId.replace(/\.desktop$/, ""))) : null
        if (!entry) entry = DesktopEntries.heuristicLookup(group.app)
        return entry ? Quickshell.iconPath(entry.icon, true) : ""
    }
    function readGroup(items) {
        DesktopActivity.action(["notification", "read-group", JSON.stringify(items.map(function(n) { return n.id }))])
    }
    onNotesChanged: rebuild()
    Component.onCompleted: rebuild()

    component Message: Rectangle {
        id: message
        required property var note
        height: messageContent.implicitHeight + 26
        radius: 12
        color: messageMouse.containsMouse && note.can_open ? "#2b303d" : "#20232d"
        border.width: 1
        border.color: messageMouse.containsMouse && note.can_open ? "#536577" : "#343b48"
        Behavior on color { ColorAnimation { duration: 160 } }
        Behavior on border.color { ColorAnimation { duration: 160 } }
        Accessible.role: Accessible.Button
        Accessible.name: (note.title || "Notificação") + (note.can_open ? ", abrir aplicação" : ", sem ação de abertura")
        activeFocusOnTab: !!note.can_open
        function open() {
            if (note.can_open && !DesktopActivity.busy)
                DesktopActivity.action(["notification", "open", String(note.id)])
        }
        MouseArea {
            id: messageMouse
            anchors.fill: parent
            enabled: !!message.note.can_open && !DesktopActivity.busy
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: message.open()
        }
        Keys.onReturnPressed: message.open()
        Keys.onSpacePressed: message.open()
        Column {
            id: messageContent
            x: 14; y: 12; width: parent.width - 27; spacing: 8
            Text {
                renderType: Text.CurveRendering
                width: parent.width; text: message.note.title || ""
                textFormat: Text.PlainText; wrapMode: Text.WordWrap
                color: "#f1f5fb"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize; font.weight: Font.DemiBold
            }
            Text {
                renderType: Text.CurveRendering
                width: parent.width; visible: text.length > 0
                text: message.note.body || ""; textFormat: Text.PlainText; wrapMode: Text.WordWrap
                color: "#b8c5d5"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize
            }
            Row {
                width: parent.width; height: 26; spacing: 8
                Text {
                    width: parent.width - readButton.width - parent.spacing
                    anchors.verticalCenter: parent.verticalCenter
                    text: message.note.can_open ? "Abrir aplicação" : "Notificação arquivada"
                    color: "#8fa3b6"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize
                }
                Rectangle {
                    id: readButton
                    width: 26; height: 26; radius: 8
                    color: readMouse.containsMouse ? "#385065" : "#303b4d"
                    border.width: 1; border.color: "#4a5b70"
                    Accessible.role: Accessible.Button
                    Accessible.name: "Marcar como lida"
                    LucideIcon { anchors.centerIn: parent; name: "check"; width: 14; height: 14 }
                    MouseArea { id: readMouse; anchors.fill: parent; enabled: !DesktopActivity.busy; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                        onClicked: DesktopActivity.action(["notification", "read", String(message.note.id)]) }
                }
            }
        }
    }
    Text {
        objectName: "notificationUnreadLabel"
        renderType: Text.CurveRendering
        width: parent.width; text: Groups.unreadLabel(inbox.notes.length)
        color: "#d9dcea"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize
    }
    Text {
        renderType: Text.CurveRendering
        width: parent.width; visible: DesktopActivity.error.length > 0
        text: DesktopActivity.error; textFormat: Text.PlainText; wrapMode: Text.WordWrap
        color: "#f0b7b7"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize
    }
    ControlTile {
        width: parent.width; visible: inbox.notes.length > 0
        iconName: "check"; showCaption: true; caption: "Marcar todas como lidas"
        enabled: !DesktopActivity.busy
        onActivated: DesktopActivity.action(["notification", "read-all"])
    }
    Repeater {
        model: inbox.groupKeys
        Item {
            id: groupItem
            required property string modelData
            readonly property var group: inbox.groups.find(function(g) { return g.key === groupItem.modelData }) || ({app: "", notes: [], threads: []})
            readonly property bool expanded: !!inbox.expandedApps[modelData]
            width: inbox.width; height: 54 + details.height
            clip: true
            Rectangle {
                id: groupButton
                width: parent.width; height: 52; radius: 12
                color: groupMouse.containsMouse ? "#2b303d" : "#1d2029"
                border.width: 1; border.color: groupMouse.containsMouse ? "#4b586b" : "#333947"
                Behavior on color { ColorAnimation { duration: 160 } }
                Behavior on border.color { ColorAnimation { duration: 160 } }
                Item {
                    anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12
                    Accessible.role: Accessible.Button
                    Accessible.name: groupItem.group.app + ", " + groupItem.group.notes.length + " mensagens"
                    activeFocusOnTab: true
                    Image {
                        id: appIcon
                        anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                        width: 24; height: 24; sourceSize.width: 48; sourceSize.height: 48
                        source: inbox.iconFor(groupItem.group); fillMode: Image.PreserveAspectFit
                        asynchronous: true
                    }
                    LucideIcon { id: bell; anchors.centerIn: appIcon; visible: appIcon.status !== Image.Ready; name: "bell"; width: 16; height: 16 }
                    Text {
                        renderType: Text.CurveRendering
                        anchors.left: appIcon.right; anchors.leftMargin: 12; anchors.right: count.left; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter
                        text: groupItem.group.app; elide: Text.ElideRight
                        color: "#e9eff7"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize; font.weight: Font.DemiBold
                    }
                    Rectangle {
                        id: count; width: 26; height: 24; radius: 8
                        anchors.right: appArrow.left; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter
                        color: "#37475a"
                        Text { anchors.centerIn: parent; text: groupItem.group.notes.length; color: "#d7e8f4"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize }
                    }
                    LucideIcon {
                        id: appArrow; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                        name: "chevron-right"; rotation: groupItem.expanded ? 90 : 0; width: 16; height: 16
                        Behavior on rotation { NumberAnimation { duration: 220; easing.type: Easing.OutCubic } }
                    }
                    MouseArea {
                        id: groupMouse; anchors.fill: parent; cursorShape: Qt.PointingHandCursor; hoverEnabled: true
                        onClicked: inbox.toggleApp(groupItem.modelData)
                    }
                    Keys.onReturnPressed: inbox.toggleApp(groupItem.modelData)
                    Keys.onSpacePressed: inbox.toggleApp(groupItem.modelData)
                }
            }
            Item {
                id: details; y: 54; width: parent.width
                height: groupItem.expanded ? detailContent.implicitHeight + 12 : 0
                opacity: groupItem.expanded ? 1 : 0
                clip: true
                Behavior on height { NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
                Behavior on opacity { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                Column {
                    id: detailContent; y: 6; width: parent.width; spacing: 8
                    Repeater {
                        model: groupItem.group.notes
                        Message { required property var modelData; width: detailContent.width; note: modelData }
                    }
                    ControlTile {
                        visible: groupItem.group.notes.length > 1; width: parent.width
                        iconName: "check"; showCaption: true; caption: "Marcar grupo como lido"
                        enabled: !DesktopActivity.busy
                        onActivated: inbox.readGroup(groupItem.group.notes)
                    }
                }
            }
        }
    }
}
