pragma Singleton

import QtQuick
import Quickshell.Io

QtObject {
    id: appearance
    // Match Hyprland general.gaps_out; capsule borders share the tiled outer edge.
    readonly property int desktopEdgeInset: 20
    // Match Hyprland rounding=10 and rounding_power=2 (circular).
    readonly property int desktopCornerRadius: 10
    readonly property color buttonSelectedBorder: "#d9dcea"
    readonly property color buttonHoverBorder: "#69728a"
    readonly property color buttonIdleBorder: "#304f566c"
    readonly property string fontFamily: "JetBrains Mono"
    readonly property int titleSize: 14
    readonly property int menuTitleInset: 8
    readonly property int bodySize: 12
    readonly property int metaSize: 11
    readonly property int menuIconCircleSize: 32
    readonly property real menuSizeRatio: menuIconCircleSize / 36
    readonly property int menuGlyphSize: Math.round(16 * menuSizeRatio)
    readonly property int menuIconGap: Math.round(10 * menuSizeRatio)
    readonly property int menuActionHeight: Math.round(56 * menuSizeRatio)
    readonly property int menuIconInset: (menuActionHeight - menuIconCircleSize) / 2
    readonly property int menuLabelInset: menuIconInset + menuIconCircleSize + menuIconGap
    readonly property int menuActionRadius: desktopCornerRadius
    readonly property int calendarActionHeight: 32
    readonly property int calendarDayHeight: 30
    // Maximum height measured from the current main Control Centre.
    readonly property int menuMaxHeight: 460
    readonly property int menuTop: 65
    property var state: ({ icon_color: null, global_icon_color: "#d9dcea", effective_icon_color: "#d9dcea", wallpaper: "", warning: "" })
    readonly property var opacityDefaults: ({bar: 93, menus: 95, terminal: 85, files: 85, rofi: 85})
    property bool detailsVisible: false
    property var pendingOpacity: ({})
    property var opacityInFlight: ({})
    function opacityPercent(key) {
        if (pendingOpacity[key] !== undefined) return pendingOpacity[key]
        var values = state.opacity || opacityDefaults
        return values[key] === undefined ? opacityDefaults[key] : values[key]
    }
    function backgroundColor(value, target) {
        var shade = Qt.color(value)
        return Qt.rgba(shade.r, shade.g, shade.b, opacityPercent(target) / 100)
    }
    readonly property color capsuleSurface: backgroundColor("#15171f", "bar")
    function setOpacity(key, value) {
        var pending = Object.assign({}, pendingOpacity)
        pending[key] = Math.max(0, Math.min(100, Math.round(value)))
        pendingOpacity = pending
        opacitySave.restart()
    }
    function flushOpacity() {
        if (busy || !Object.keys(pendingOpacity).length) return
        opacityInFlight = Object.assign({}, pendingOpacity)
        change("opacity", JSON.stringify(opacityInFlight))
    }
    function finishOpacity() {
        var pending = Object.assign({}, pendingOpacity)
        Object.keys(opacityInFlight).forEach(function(key) {
            if (pending[key] === opacityInFlight[key]) delete pending[key]
        })
        pendingOpacity = pending
        opacityInFlight = ({})
        if (Object.keys(pending).length) opacitySave.restart()
    }
    property Timer opacitySave: Timer {
        interval: 180
        onTriggered: appearance.flushOpacity()
    }
    readonly property color iconColor: state.effective_icon_color || "#d9dcea"
    readonly property bool tintButtons: false
    readonly property bool tintWindows: false
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
            if (/^#[0-9a-fA-F]{6}$/.test(value.effective_icon_color)
                    && JSON.stringify(value) !== JSON.stringify(state)) state = value
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
        onExited: (code, status) => { appearance.finishOpacity(); if (code === 0) appearance.refresh() }
    }
    property Process chooserProcess: Process {
        command: ["/home/apx/.local/bin/apx-appearance-v1", "choose-wallpaper"]
        stdout: StdioCollector { onStreamFinished: appearance.acceptReport(text) }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) appearance.error = text.trim() }
        onExited: (code, status) => { if (code === 0) appearance.error = ""; if (Object.keys(appearance.pendingOpacity).length) appearance.opacitySave.restart() }
    }
    property Timer refreshTimer: Timer {
        interval: appearance.detailsVisible ? 500 : 5000; running: true; repeat: true; triggeredOnStart: true
        onTriggered: appearance.refresh()
    }
}
