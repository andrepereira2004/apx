pragma Singleton
import QtQuick
import Quickshell.Io

QtObject {
    id: activity
    property var state: ({ players: [], notifications: [], active_notifications: 0 })
    readonly property bool busy: actionProcess.running
    property double clock: Date.now()
    property bool detailsVisible: false
    function position(player) {
        if (!player) return 0
        var base = Number(player.position) || 0
        var elapsed = player.status === "Playing" ? Math.max(0, clock - Number(player.sampled_at || clock)) / 1000 * (Number(player.rate) || 1) : 0
        return Math.min(Number(player.length) > 0 ? Number(player.length) : Infinity, Math.max(0, base + elapsed))
    }
    function timeLabel(seconds) {
        var total = Math.max(0, Math.floor(seconds || 0))
        return (total >= 3600 ? Math.floor(total / 3600) + ":" : "") + (total >= 3600 ? String(Math.floor(total / 60) % 60).padStart(2,"0") : String(Math.floor(total / 60))) + ":" + String(total % 60).padStart(2,"0")
    }
    function seek(player, position) {
        if (!player || !player.can_seek || player.length <= 0) return
        action(["seek", player.name, player.track_id, String(position), String(player.length)])
    }
    property Timer progressClock: Timer {
        interval: 100; repeat: true
        running: activity.state.players.some(function(p) { return p.status === "Playing" })
        onTriggered: activity.clock = Date.now()
    }
    property string error: ""
    function accept(text) { try { if (text.trim().length) { state = JSON.parse(text); clock = Date.now() } } catch (e) {} }
    function refresh() { if (!busy && !readProcess.running) readProcess.running = true }
    function action(args) {
        if (busy) return
        error = ""
        if (readProcess.running) readProcess.running = false
        actionProcess.command = ["/home/apx/.local/bin/apx-desktop-activity-v1"].concat(args)
        actionProcess.running = true
    }
    property Process readProcess: Process {
        command: ["/home/apx/.local/bin/apx-desktop-activity-v1", "get"]
        stdout: StdioCollector { onStreamFinished: activity.accept(text) }
    }
    property Process actionProcess: Process {
        stdout: StdioCollector { onStreamFinished: activity.accept(text) }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) activity.error = text.trim() }
    }
    property Timer timer: Timer { interval: activity.detailsVisible ? 2000 : (activity.state.players.length ? 5000 : 10000); running: true; repeat: true; triggeredOnStart: true; onTriggered: activity.refresh() }
}
