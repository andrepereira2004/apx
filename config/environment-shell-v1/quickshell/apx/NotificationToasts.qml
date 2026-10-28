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
    readonly property int cardHeight: Math.min(128, Math.max(122, Math.floor(((screen ? screen.height : 720)-110)/3)))
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
            visibleNotes.reverse().forEach(function(note, order) {
                var index=toasts.indexFor(note.id)
                if (index<0) cards.append({noteId: note.id,payload: JSON.stringify(note),closed: false,arrivalOrder: order})
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
        spacing: 9
        move: Transition { NumberAnimation { properties: "x,y"; duration: 300; easing.type: Easing.OutCubic } }
        Repeater {
            id: toastRepeater
            model: cards
            Item {
                id: holder
                required property int noteId
                required property string payload
                required property bool closed
                required property int arrivalOrder
                readonly property var note: JSON.parse(payload)
                readonly property bool screenshot: note.app_name === "APX Captura"
                width: stack.width
                height: visual.height
                property real reveal: 0
                property real dragOffset: 0
                property bool dragging: false
                onClosedChanged: if (closed) { reveal=0; removal.restart() }
                Behavior on reveal { NumberAnimation { duration: 280; easing.type: Easing.OutCubic } }
                Behavior on dragOffset { enabled: !holder.dragging; NumberAnimation { duration: 180; easing.type: Easing.OutCubic } }
                Timer { interval: 65 * holder.arrivalOrder; running: true; onTriggered: if (!holder.closed) holder.reveal=1 }
                Timer { id: removal; interval: 290; onTriggered: toasts.removeCard(holder.noteId) }
                // Other applications retain their existing Mako expiry policy.
                Timer { interval: 5000; running: holder.screenshot && !holder.closed; onTriggered: toasts.closeCard(holder.noteId,false,"") }
                Rectangle {
                    id: visual
                    x: 26*(1-holder.reveal)+holder.dragOffset
                    width: holder.width
                    height: holder.screenshot ? 198 : toasts.cardHeight
                    clip: true
                    radius: 16
                    color: "#181c25"
                    border.width: 1
                    border.color: "#383e4c"
                    opacity: holder.reveal * Math.max(0,1-holder.dragOffset/(width*1.15))
                    scale: .985 + .015*holder.reveal
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
                        anchors.margins: 16
                        Row {
                            id: noteHeader
                            anchors { left: parent.left; right: parent.right; top: parent.top }
                            height: 19
                            spacing: 10
                            Image {
                                id: appIcon
                                width: 19; height: 19; fillMode: Image.PreserveAspectFit
                                visible: status === Image.Ready
                                source: {
                                    if (holder.screenshot) return ""
                                    var icon=String(holder.note.app_icon || "")
                                    if (icon.startsWith("file://")) return icon
                                    if (icon.startsWith("/")) return "file://"+icon
                                    var supplied=icon ? Quickshell.iconPath(icon,true) : ""
                                    if (supplied.length) return supplied
                                    var entryId=String(holder.note.desktop_entry || "")
                                    var entry=entryId ? (DesktopEntries.byId(entryId) || DesktopEntries.byId(entryId.replace(/\.desktop$/, ""))) : null
                                    if (!entry) entry=DesktopEntries.heuristicLookup(holder.note.app_name || "")
                                    return entry ? Quickshell.iconPath(entry.icon,true) : ""
                                }
                            }
                            LucideIcon { name: holder.screenshot ? "scissors" : "bell"; visible: appIcon.status !== Image.Ready; width: 19; height: 19 }
                            Text { text: holder.note.app_name || "Notificação"; width: contents.width-58; elide: Text.ElideRight; color: "#aac0d2"; font.family: Appearance.fontFamily; font.pixelSize: 11; font.weight: Font.DemiBold }
                        }
                        Text {
                            id: noteTitle
                            anchors { left: parent.left; right: parent.right; top: noteHeader.bottom; topMargin: 10 }
                            text: holder.note.summary || ""
                            textFormat: Text.PlainText
                            wrapMode: Text.WordWrap
                            color: "#f0f5fb"
                            font.family: Appearance.fontFamily
                            font.pixelSize: 14
                            font.weight: Font.DemiBold
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
                                    radius: 9
                                    color: actionMouse.containsMouse ? "#35485c" : "#2a3647"
                                    border.width: 1
                                    border.color: "#506177"
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
                                color: "#b9c8d6"
                                font.family: Appearance.fontFamily
                                font.pixelSize: 12
                            }
                        }
                    }
                        Rectangle {
                            anchors.right: parent.right;anchors.top: parent.top;anchors.margins: 12;width: 28;height: 28;radius: 9
                            color: closeMouse.containsMouse ? "#405065" : "#293545"
                            LucideIcon { anchors.centerIn: parent;name: "x";width: 14;height: 14 }
                            MouseArea { id: closeMouse; anchors.fill: parent;hoverEnabled: true;cursorShape: Qt.PointingHandCursor;onClicked: toasts.closeCard(holder.noteId,false,"") }
                    }
                }
            }
        }
    }
}
