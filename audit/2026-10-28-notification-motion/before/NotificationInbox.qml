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
        height: messageContent.implicitHeight + 16
        radius: Appearance.menuActionRadius
        color: "#252936"
        Accessible.role: Accessible.Button
        Accessible.name: (note.title || "Notificação") + (note.can_open ? ", abrir aplicação" : ", sem ação de abertura")
        activeFocusOnTab: !!note.can_open
        function open() {
            if (note.can_open && !DesktopActivity.busy)
                DesktopActivity.action(["notification", "open", String(note.id)])
        }
        MouseArea {
            anchors.fill: parent
            enabled: !!message.note.can_open && !DesktopActivity.busy
            cursorShape: Qt.PointingHandCursor
            onClicked: message.open()
        }
        Keys.onReturnPressed: message.open()
        Keys.onSpacePressed: message.open()
        Column {
            id: messageContent
            x: 8; y: 8; width: parent.width - 16; spacing: 6
            Text {
                renderType: Text.CurveRendering
                width: parent.width; text: message.note.title || ""
                textFormat: Text.PlainText; wrapMode: Text.WordWrap
                color: "#e1e5f0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize
            }
            Text {
                renderType: Text.CurveRendering
                width: parent.width; visible: text.length > 0
                text: message.note.body || ""; textFormat: Text.PlainText; wrapMode: Text.WordWrap
                color: "#b5bdd0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize
            }
            ControlTile {
                width: parent.width; showCaption: true
                iconName: "check"; caption: "Marcar como lida"; enabled: !DesktopActivity.busy
                onActivated: DesktopActivity.action(["notification", "read", String(message.note.id)])
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
        Rectangle {
            id: stack
            required property string modelData
            readonly property var group: inbox.groups.find(function(g) { return g.key === stack.modelData }) || ({app: "", notes: [], threads: []})
            readonly property bool expanded: !!inbox.expandedApps[modelData]
            width: inbox.width; height: content.implicitHeight + 20; radius: Appearance.menuActionRadius
            color: "#1b1d26"
            Rectangle {
                visible: !stack.expanded
                x: 5; y: parent.height - 3; width: parent.width - 10; height: 7; radius: 6
                color: "#292d3a"; z: -1
            }
            Column {
                id: content
                x: 10; y: 10; width: parent.width - 20; spacing: 8
                Item {
                    width: parent.width; height: 30
                    Accessible.role: Accessible.Button
                    Accessible.name: stack.group.app + ", " + stack.group.notes.length + " mensagens"
                    activeFocusOnTab: true
                    Image {
                        id: appIcon
                        anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                        width: 20; height: 20; sourceSize.width: 40; sourceSize.height: 40
                        source: inbox.iconFor(stack.group); fillMode: Image.PreserveAspectFit
                        asynchronous: true
                    }
                    LucideIcon { id: bell; anchors.centerIn: appIcon; visible: appIcon.status !== Image.Ready; name: "bell"; width: 16; height: 16 }
                    Text {
                        renderType: Text.CurveRendering
                        anchors.left: appIcon.right; anchors.leftMargin: 8; anchors.right: count.left; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter
                        text: stack.group.app; elide: Text.ElideRight
                        color: "#d9dcea"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize
                    }
                    Text {
                        id: count; renderType: Text.CurveRendering
                        anchors.right: appArrow.left; anchors.rightMargin: 6; anchors.verticalCenter: parent.verticalCenter
                        text: stack.group.notes.length; color: "#a4abc0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize
                    }
                    LucideIcon {
                        id: appArrow; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                        name: "chevron-right"; rotation: stack.expanded ? 90 : 0; width: 14; height: 14
                    }
                    MouseArea {
                        anchors.fill: parent; cursorShape: Qt.PointingHandCursor
                        onClicked: inbox.toggleApp(stack.modelData)
                    }
                    Keys.onReturnPressed: inbox.toggleApp(stack.modelData)
                    Keys.onSpacePressed: inbox.toggleApp(stack.modelData)
                }
                Loader {
                    width: parent.width; visible: active; active: stack.expanded
                    sourceComponent: Column {
                        spacing: 10
                        Repeater {
                            model: stack.group.notes
                            Message { required property var modelData; width: parent.width; note: modelData }
                        }
                    }
                }
                ControlTile {
                    visible: stack.expanded && stack.group.notes.length > 1; width: parent.width
                    iconName: "check"; showCaption: true; caption: "Marcar grupo como lido"
                    enabled: !DesktopActivity.busy
                    onActivated: inbox.readGroup(stack.group.notes)
                }
            }
        }
    }
}
