pragma ComponentBehavior: Bound
import QtQuick
import "NotificationGroups.js" as Groups

Column {
    id: inbox
    property var notes: DesktopActivity.notificationEntries
    readonly property bool continuousScrollContent: true
    property var groups: []
    property var groupKeys: []
    property var expandedApps: ({})
    property var expandedThreads: ({})
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
    function toggleThread(key) {
        var next = Object.assign({}, expandedThreads)
        next[key] = !next[key]
        expandedThreads = next
    }
    function readGroup(items) {
        DesktopActivity.action(["notification", "read-group", JSON.stringify(items.map(function(n) { return n.id }))])
    }
    onNotesChanged: rebuild()
    Component.onCompleted: rebuild()

    component Message: Column {
        id: message
        required property var note
        property bool compact: false
        spacing: 6
        Text {
            renderType: Text.CurveRendering
            width: parent.width; text: message.note.title || ""
            textFormat: Text.PlainText; wrapMode: Text.WordWrap
            maximumLineCount: message.compact ? 2 : 2147483647; elide: Text.ElideRight
            color: "#e1e5f0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize
        }
        Text {
            renderType: Text.CurveRendering
            width: parent.width; visible: text.length > 0
            text: message.note.body || ""; textFormat: Text.PlainText; wrapMode: Text.WordWrap
            maximumLineCount: message.compact ? 2 : 2147483647; elide: Text.ElideRight
            color: "#b5bdd0"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize
        }
        Row {
            visible: !message.compact
            width: parent.width; spacing: 6
            ControlTile {
                visible: !!message.note.can_open; showCaption: true
                width: (parent.width - 6) * .36; iconName: "bring-to-front"; caption: "Abrir"
                enabled: !DesktopActivity.busy
                onActivated: DesktopActivity.action(["notification", "open", String(message.note.id)])
            }
            ControlTile {
                showCaption: true; width: message.note.can_open ? (parent.width - 6) * .64 : parent.width
                iconName: "check"; caption: "Marcar como lida"; enabled: !DesktopActivity.busy
                onActivated: DesktopActivity.action(["notification", "read", String(message.note.id)])
            }
        }
    }
    component Thread: Column {
        id: thread
        required property var threadData
        readonly property bool multiple: threadData.notes.length > 1
        readonly property bool expanded: !multiple || !!inbox.expandedThreads[threadData.key]
        spacing: 6
        Item {
            visible: thread.multiple
            width: parent.width; height: 30
            Accessible.role: Accessible.Button
            Accessible.name: thread.threadData.title + ", " + thread.threadData.notes.length + " mensagens"
            activeFocusOnTab: visible
            Text {
                renderType: Text.CurveRendering
                anchors.left: parent.left; anchors.right: arrow.left; anchors.verticalCenter: parent.verticalCenter
                text: thread.threadData.title + " · " + thread.threadData.notes.length
                color: "#d9dcea"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize
                elide: Text.ElideRight
            }
            LucideIcon { id: arrow; anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter; name: "chevron-right"; rotation: thread.expanded ? 90 : 0; width: 14; height: 14 }
            MouseArea { anchors.fill: parent; cursorShape: Qt.PointingHandCursor; onClicked: inbox.toggleThread(thread.threadData.key) }
            Keys.onReturnPressed: inbox.toggleThread(thread.threadData.key)
            Keys.onSpacePressed: inbox.toggleThread(thread.threadData.key)
        }
        Loader {
            width: parent.width; visible: active; active: !thread.expanded
            sourceComponent: Message { note: thread.threadData.notes[0]; compact: true }
        }
        Loader {
            width: parent.width; visible: active; active: thread.expanded
            sourceComponent: Column {
                spacing: 10
                Repeater {
                    model: thread.threadData.notes
                    Message { required property var modelData; width: parent.width; note: modelData }
                }
            }
        }
        ControlTile {
            visible: thread.multiple; width: parent.width; iconName: "check"; showCaption: true
            caption: "Marcar conversa como lida"; enabled: !DesktopActivity.busy
            onActivated: inbox.readGroup(thread.threadData.notes)
        }
    }
    Text {
        objectName: "notificationUnreadLabel"
        renderType: Text.CurveRendering
        width: parent.width; text: Groups.unreadLabel(inbox.notes.length)
        color: "#d9dcea"; font.family: Appearance.fontFamily; font.pixelSize: Appearance.bodySize
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
            readonly property bool expanded: group.notes.length <= 1 || !!inbox.expandedApps[modelData]
            width: inbox.width; height: content.implicitHeight + 20; radius: 14
            color: "#1b1d26"
            Rectangle {
                visible: stack.group.notes.length > 1 && !stack.expanded
                x: 5; y: parent.height - 3; width: parent.width - 10; height: 7; radius: 6
                color: "#292d3a"; z: -1
            }
            Column {
                id: content
                x: 10; y: 10; width: parent.width - 20; spacing: 8
                Item {
                    width: parent.width; height: 30
                    Accessible.role: stack.group.notes.length > 1 ? Accessible.Button : Accessible.StaticText
                    Accessible.name: stack.group.app + ", " + stack.group.notes.length + " mensagens"
                    activeFocusOnTab: stack.group.notes.length > 1
                    LucideIcon { id: bell; anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter; name: "bell"; width: 16; height: 16 }
                    Text {
                        renderType: Text.CurveRendering
                        anchors.left: bell.right; anchors.leftMargin: 8; anchors.right: count.left; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter
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
                        visible: stack.group.notes.length > 1
                        name: "chevron-right"; rotation: stack.expanded ? 90 : 0; width: 14; height: 14
                    }
                    MouseArea {
                        anchors.fill: parent; enabled: stack.group.notes.length > 1; cursorShape: Qt.PointingHandCursor
                        onClicked: inbox.toggleApp(stack.modelData)
                    }
                    Keys.onReturnPressed: if (stack.group.notes.length > 1) inbox.toggleApp(stack.modelData)
                    Keys.onSpacePressed: if (stack.group.notes.length > 1) inbox.toggleApp(stack.modelData)
                }
                Loader {
                    width: parent.width; visible: active; active: !stack.expanded && stack.group.notes.length > 0
                    sourceComponent: Message { note: stack.group.notes[0]; compact: true }
                }
                Loader {
                    width: parent.width; visible: active; active: stack.expanded
                    sourceComponent: Column {
                        spacing: 10
                        Repeater {
                            model: stack.group.threads
                            Thread { required property var modelData; width: parent.width; threadData: modelData }
                        }
                    }
                }
                ControlTile {
                    visible: stack.group.notes.length > 1; width: parent.width
                    iconName: "check"; showCaption: true; caption: "Marcar grupo como lido"
                    enabled: !DesktopActivity.busy
                    onActivated: inbox.readGroup(stack.group.notes)
                }
            }
        }
    }
}
