pragma Singleton

import QtQuick
import Quickshell.Io

QtObject {
    id: appearance
    readonly property string fontFamily: "JetBrains Mono"
    readonly property int titleSize: 14
    readonly property int bodySize: 12
    readonly property int metaSize: 11
    readonly property int menuTop: 65
    property var state: ({ icon_color: null, global_icon_color: "#d9dcea", effective_icon_color: "#d9dcea", wallpaper: "", warning: "" })
    readonly property color iconColor: state.effective_icon_color || "#d9dcea"
    readonly property bool tintButtons: !!(state.effective_style && state.effective_style.buttons)
    readonly property bool tintWindows: !!(state.effective_style && state.effective_style.windows)
    readonly property color surface: state.surface || "#262939"
    readonly property color hover: state.hover || "#41475b"
    readonly property color active: state.active || "#454d64"
    readonly property color border: state.border || "#50586d"
    readonly property color barSurface: Qt.rgba(surface.r, surface.g, surface.b, 0.70)
    readonly property string wallpaper: state.wallpaper || ""
    readonly property bool busy: writeProcess.running || chooserProcess.running
    property string error: ""

    function acceptReport(text) {
        if (!text.trim().length) return
        try {
            var value = JSON.parse(text)
            if (/^#[0-9a-fA-F]{6}$/.test(value.effective_icon_color)) state = value
        } catch (e) { error = "Não foi possível ler a personalização." }
    }
    function refresh() {
        if (!busy && !readProcess.running) readProcess.running = true
    }
    function change(operation, value) {
        if (busy) return
        error = ""
        // Do not let a stale polling response overwrite a completed write.
        if (readProcess.running) readProcess.running = false
        writeProcess.command = ["/home/apx/.local/bin/apx-appearance-v1", operation, value]
        writeProcess.running = true
    }
    function setStyle(scope, style) {
        change(scope === "global" ? "global-style" : "environment-style", JSON.stringify(style))
    }
    function chooseWallpaper() {
        if (busy) return
        error = ""
        if (readProcess.running) readProcess.running = false
        chooserProcess.running = true
    }
    property Process readProcess: Process {
        command: ["/home/apx/.local/bin/apx-appearance-v1", "get"]
        stdout: StdioCollector { onStreamFinished: if (!appearance.busy) appearance.acceptReport(text) }
    }
    property Process writeProcess: Process {
        stdout: StdioCollector { onStreamFinished: appearance.acceptReport(text) }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) appearance.error = text.trim() }
        onExited: (code, status) => { if (code === 0) appearance.refresh() }
    }
    property Process chooserProcess: Process {
        command: ["/home/apx/.local/bin/apx-appearance-v1", "choose-wallpaper"]
        stdout: StdioCollector { onStreamFinished: appearance.acceptReport(text) }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) appearance.error = text.trim() }
        onExited: (code, status) => { if (code === 0) appearance.error = "" }
    }
    property Timer refreshTimer: Timer {
        interval: 5000; running: true; repeat: true; triggeredOnStart: true
        onTriggered: appearance.refresh()
    }
}
