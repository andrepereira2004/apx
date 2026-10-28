pragma ComponentBehavior: Bound
import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Wayland

PanelWindow {
    id: toasts
    screen: Quickshell.screens.length ? Quickshell.screens[0] : null
    anchors { top: true; bottom: true; right: true }
    implicitWidth: Math.min(440, screen ? screen.width : 440)
    exclusiveZone: 0
    color: "transparent"
    visible: cards.count > 0
    mask: Region { item: stack }
    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
    readonly property int cardHeight: Math.min(200, Math.max(120, Math.floor(((screen ? screen.height : 720)-100)/3)))
    property var queue: []
    function refresh() { if (!reader.running) reader.running = true }
    function status() {
        var result=[]
        for (var i=0;i<cards.count;++i) result.push({id: cards.get(i).noteId,closed: cards.get(i).closed,width: toastRepeater.itemAt(i) ? toastRepeater.itemAt(i).width : 0,height: toastRepeater.itemAt(i) ? toastRepeater.itemAt(i).height : 0})
        return {visible: visible,cards: result}
    }
    function command(args) {
        queue = queue.concat([args])
        runNext()
    }
    function runNext() {
        if (worker.running || !queue.length) return
        worker.command = queue[0]
        queue = queue.slice(1)
        worker.running = true
    }
    function indexFor(id) {
        for (var i=0; i<cards.count; ++i) if (cards.get(i).noteId === id) return i
        return -1
    }
    function removeCard(id) {
        var i=indexFor(id)
        if (i>=0) cards.remove(i)
    }
    function closeCard(id, activate, action) {
        var i=indexFor(id)
        if (i<0 || cards.get(i).closed) return
        var note=JSON.parse(cards.get(i).payload)
        cards.setProperty(i,"closed",true)
        if (activate) command(["makoctl","invoke","-n",String(id),action || "default"])
        command(["makoctl","dismiss","-n",String(id)].concat(note.app_name === "APX Captura" ? ["--no-history"] : []))
        DesktopActivity.refreshNotifications()
    }
    function openCard(id) {
        var i=indexFor(id)
        if (i<0 || cards.get(i).closed || opener.running) return
        var note=JSON.parse(cards.get(i).payload)
        if ((note.app_name === "APX Captura" || note.app_name === "APX Browser") && note.actions && note.actions.default) {
            closeCard(id,true,"default")
            return
        }
        opener.noteId=id
        opener.command=["/home/apx/.local/bin/apx-desktop-activity-v1","notification","open-mako",String(id)]
        opener.running=true
    }
    function reconcile(text) {
        try {
            var notes=JSON.parse(text)
            if (!Array.isArray(notes)) return
            var visibleNotes=notes.slice(0,3)
            var ids=visibleNotes.map(function(n) { return n.id })
            for (var i=0;i<cards.count;++i) {
                if (ids.indexOf(cards.get(i).noteId)<0) cards.setProperty(i,"closed",true)
            }
            visibleNotes.reverse().forEach(function(note) {
                var index=toasts.indexFor(note.id)
                if (index<0) cards.append({noteId: note.id,payload: JSON.stringify(note),closed: false})
                else if (!cards.get(index).closed) cards.setProperty(index,"payload",JSON.stringify(note))
            })
        } catch(e) { console.warn("Notification list:",e) }
    }
    ListModel { id: cards }
    Process {
        id: reader
        command: ["makoctl","list","-j"]
        stdout: StdioCollector { onStreamFinished: toasts.reconcile(text) }
    }
    Process {
        id: worker
        onExited: { toasts.refresh(); DesktopActivity.refreshNotifications(); Qt.callLater(toasts.runNext) }
    }
    Process {
        id: opener
        property int noteId: -1
        onExited: function(code) {
            if (code === 0) toasts.closeCard(noteId,false,"")
            toasts.refresh()
        }
    }
    Process { id: modeEnable; command: ["makoctl","mode","-a","apx-animated"] }
    Timer { interval: 250; running: true; onTriggered: modeEnable.running=true }
    Timer { interval: 700; repeat: true; running: true; triggeredOnStart: true; onTriggered: toasts.refresh() }
    Component.onDestruction: Quickshell.execDetached(["makoctl","mode","-r","apx-animated"])
    Column {
        id: stack
        x: 12; y: 76
        width: parent.width-28
        spacing: 10
        Repeater {
            id: toastRepeater
            model: cards
            Item {
                id: holder
                required property int noteId
                required property string payload
                required property bool closed
                readonly property var note: JSON.parse(payload)
                readonly property bool screenshot: note.app_name === "APX Captura"
                width: stack.width
                height: visual.height
                property real entrance: width+30
                property real dragOffset: 0
                property bool dragging: false
                onClosedChanged: if (closed) { entrance=width+30; removal.restart() }
                Component.onCompleted: entrance=0
                Behavior on entrance { NumberAnimation { duration: 240; easing.type: Easing.OutCubic } }
                Behavior on dragOffset { enabled: !holder.dragging; NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }
                Timer { id: removal; interval: 250; onTriggered: toasts.removeCard(holder.noteId) }
                // Other applications retain their existing Mako expiry policy.
                Timer { interval: 5000; running: holder.screenshot && !holder.closed; onTriggered: toasts.closeCard(holder.noteId,false,"") }
                Rectangle {
                    id: visual
                    x: holder.entrance+holder.dragOffset
                    width: holder.width
                    height: toasts.cardHeight
                    clip: true
                    radius: 14
                    color: "#f2101117"
                    border.width: 1
                    border.color: "#343947"
                    opacity: Math.max(0,1-holder.dragOffset/(width*1.15))
                    MouseArea {
                        id: gesture
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        property real origin: 0
                        property real distance: 0
                        onPressed: function(mouse) { origin=mapToGlobal(mouse.x,mouse.y).x; distance=0; holder.dragging=true }
                        onPositionChanged: function(mouse) {
                            if (!pressed) return
                            distance=mapToGlobal(mouse.x,mouse.y).x-origin
                            holder.dragOffset=Math.max(0,distance)
                        }
                        onReleased: {
                            holder.dragging=false
                            if (distance>Math.min(110,width*.3)) toasts.closeCard(holder.noteId,false,"")
                            else { holder.dragOffset=0; if (Math.abs(distance)<6) toasts.openCard(holder.noteId) }
                        }
                        onCanceled: { holder.dragging=false;holder.dragOffset=0 }
                    }
                    Item {
                        id: contents
                        anchors.fill: parent
                        anchors.margins: 14
                        Row {
                            id: noteHeader
                            anchors { left: parent.left; right: parent.right; top: parent.top }
                            height: 16
                            spacing: 8
                            Image {
                                id: appIcon
                                width: 16; height: 16; fillMode: Image.PreserveAspectFit
                                visible: status === Image.Ready
                                source: {
                                    if (holder.screenshot) return ""
                                    var icon=String(holder.note.app_icon || "")
                                    if (icon.startsWith("file://")) return icon
                                    if (icon.startsWith("/")) return "file://"+icon
                                    return icon ? Quickshell.iconPath(icon,true) : ""
                                }
                            }
                            LucideIcon { name: holder.screenshot ? "scissors" : "bell"; visible: appIcon.status !== Image.Ready; width: 16; height: 16 }
                            Text { text: holder.note.app_name || "Notificação"; width: contents.width-54; elide: Text.ElideRight; color: "#a4abc0"; font.family: Appearance.fontFamily; font.pixelSize: 11 }
                        }
                        Text {
                            id: noteTitle
                            anchors { left: parent.left; right: parent.right; top: noteHeader.bottom; topMargin: 8 }
                            text: holder.note.summary || ""
                            textFormat: Text.PlainText
                            wrapMode: Text.WordWrap
                            color: "#d9dcea"
                            font.family: Appearance.fontFamily
                            font.pixelSize: 13
                            maximumLineCount: 2
                            elide: Text.ElideRight
                        }
                        Flow {
                            id: noteActions
                            anchors { left: parent.left; right: parent.right; bottom: parent.bottom }
                            spacing: 6
                            visible: actionRepeater.count>0
                            height: visible ? implicitHeight : 0
                            Repeater {
                                id: actionRepeater
                                model: Object.keys(holder.note.actions || {}).filter(function(key) { return key!=="default" }).slice(0,4)
                                Rectangle {
                                    id: actionButton
                                    required property string modelData
                                    width: Math.min((contents.width-6)/2,actionLabel.implicitWidth+22)
                                    height: 32
                                    radius: 8
                                    color: actionMouse.containsMouse ? "#292d3a" : "#1b1d26"
                                    border.width: 1
                                    border.color: "#343947"
                                    Text { id: actionLabel; anchors.centerIn: parent; width: parent.width-16; horizontalAlignment: Text.AlignHCenter; elide: Text.ElideRight; text: holder.note.actions[actionButton.modelData]; color: "#d9dcea"; font.family: Appearance.fontFamily; font.pixelSize: 11 }
                                    MouseArea { id: actionMouse; anchors.fill: parent;hoverEnabled: true;cursorShape: Qt.PointingHandCursor;onClicked: toasts.closeCard(holder.noteId,true,actionButton.modelData) }
                                }
                            }
                        }
                        Item {
                            id: bodyRegion
                            anchors { left: parent.left; right: parent.right; top: noteTitle.bottom; topMargin: 8; bottom: noteActions.top; bottomMargin: noteActions.visible ? 8 : 0 }
                            clip: true
                            Image {
                                anchors.fill: parent
                                visible: holder.screenshot
                                source: holder.screenshot && holder.note.app_icon ? "file://"+holder.note.app_icon : ""
                                fillMode: Image.PreserveAspectFit
                                smooth: true
                                cache: false
                            }
                            Text {
                                anchors.fill: parent
                                visible: !holder.screenshot && text.length>0
                                text: (holder.note.body || "").replace(/<[^>]*>/g,"")
                                textFormat: Text.PlainText
                                wrapMode: Text.WordWrap
                                maximumLineCount: Math.max(1,Math.floor(bodyRegion.height/16))
                                elide: Text.ElideRight
                                color: "#a4abc0"
                                font.family: Appearance.fontFamily
                                font.pixelSize: 11
                            }
                        }
                    }
                    Item {
                        anchors.right: parent.right;anchors.top: parent.top;anchors.margins: 9;width: 28;height: 28
                        LucideIcon { anchors.centerIn: parent;name: "x";width: 14;height: 14 }
                        MouseArea { anchors.fill: parent;cursorShape: Qt.PointingHandCursor;onClicked: toasts.closeCard(holder.noteId,false,"") }
                    }
                }
            }
        }
    }
}
