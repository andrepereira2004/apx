pragma Singleton
import QtQuick
import Quickshell.Io

QtObject {
    id: activity
    property var notificationEntries: []
    property var state: ({ players: [], notifications: [], active_notifications: 0 })
    readonly property bool busy: actionProcess.running
    property double clock: Date.now()
    property bool detailsVisible: false
    property string pendingPlayer: ""
    property string pendingStatus: ""
    property string pendingTrack: ""
    property double pendingSince: 0
    property string sentPlayer: ""
    property string sentStatus: ""
    property var pendingSeek: null
    property bool seekInFlight: false
    function clearSeekFeedback() { pendingSeek = null; seekFeedbackTimeout.stop() }
    function sendSeek() {
        if (busy || !pendingSeek || pendingSeek.sent) return
        var player = state.players.find(function(p) { return p.name === pendingSeek.name && p.track_id === pendingSeek.track })
        if (!player || !player.can_seek) { clearSeekFeedback(); return }
        pendingSeek = Object.assign({}, pendingSeek, {sent: true, sentAt: Date.now()})
        if (readProcess.running) readProcess.running = false
        seekInFlight = true
        actionProcess.command = ["/home/apx/.local/bin/apx-desktop-activity-v1", "seek", pendingSeek.name, pendingSeek.track, String(pendingSeek.position), String(player.length)]
        actionProcess.running = true
    }
    function settleSeekFeedback() {
        if (!pendingSeek) return
        var player = state.players.find(function(p) { return p.name === pendingSeek.name && p.track_id === pendingSeek.track })
        if (!player) { clearSeekFeedback(); return }
        if (pendingSeek.sent && Number(player.sampled_at) >= pendingSeek.sentAt && Math.abs(Number(player.position) - pendingSeek.position) < 1.5)
            clearSeekFeedback()
    }
    property Timer seekFeedbackTimeout: Timer {
        interval: 1800
        onTriggered: {
            if (activity.busy) restart()
            else { activity.clearSeekFeedback(); activity.refresh() }
        }
    }
    function clearPlaybackFeedback() {
        pendingPlayer = ""; pendingStatus = ""; pendingTrack = ""
        feedbackTimeout.stop()
    }
    function settlePlaybackFeedback() {
        if (!pendingPlayer.length || busy || sentPlayer.length) return
        var player = state.players.find(function(p) { return p.name === pendingPlayer })
        if (!player || player.track_id !== pendingTrack) { clearPlaybackFeedback(); return }
        if (player.status === pendingStatus && Number(player.sampled_at) >= pendingSince) clearPlaybackFeedback()
    }
    function togglePlayback(player) {
        if (!player || !player.can_control) return
        var current = pendingPlayer === player.name && pendingStatus.length ? pendingStatus : player.status
        pendingPlayer = player.name; pendingTrack = player.track_id
        pendingStatus = current === "Playing" ? "Paused" : "Playing"
        pendingSince = Date.now()
        error = ""
        feedbackTimeout.restart()
        sendPlayback()
    }
    function sendPlayback() {
        if (busy || !pendingPlayer.length) return
        if (readProcess.running) readProcess.running = false
        sentPlayer = pendingPlayer; sentStatus = pendingStatus
        actionProcess.command = ["/home/apx/.local/bin/apx-desktop-activity-v1", "media", sentPlayer, sentStatus === "Playing" ? "play" : "pause"]
        actionProcess.running = true
    }
    property Timer feedbackTimeout: Timer {
        interval: 1200
        onTriggered: {
            if (activity.busy) restart()
            else { activity.clearPlaybackFeedback(); activity.refresh() }
        }
    }
    function hasMedia(player) {
        // Browsers can report Paused at EOF. Ordinary pause stays visible.
        var atEnd = player.length > 0 && player.position >= player.length - 0.05
        return player.status === "Playing" || (player.status === "Paused" && !atEnd)
    }
    function playbackIcon(player) {
        var status = pendingPlayer === player.name && pendingStatus.length ? pendingStatus : player.status
        return status === "Playing" ? "pause" : "play"
    }
    function position(player) {
        if (!player) return 0
        if (pendingSeek && pendingSeek.name === player.name && pendingSeek.track === player.track_id) {
            var advance = player.status === "Playing" ? Math.max(0, clock - pendingSeek.requestedAt) / 1000 * (Number(player.rate) || 1) : 0
            return Math.min(Number(player.length), pendingSeek.position + advance)
        }
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
        pendingSeek = {name: player.name, track: player.track_id, position: Math.max(0, Math.min(player.length, position)), requestedAt: Date.now(), sent: false, sentAt: 0}
        error = ""
        seekFeedbackTimeout.restart()
        sendSeek()
    }
    property Timer progressClock: Timer {
        interval: activity.detailsVisible ? 16 : 250; repeat: true
        running: activity.state.players.some(function(p) { return p.status === "Playing" })
        onTriggered: activity.clock = Date.now()
    }
    property string error: ""
    function accept(text) {
        try {
            if (!text.trim().length) return
            var report = JSON.parse(text)
            clock = Date.now()
            if (report.players) {
                report.players = report.players.map(function(player) {
                    var previous = state.players.find(function(old) { return old.name === player.name && old.track_id === player.track_id })
                    if (previous && Number(previous.sampled_at) > Number(player.sampled_at)) return previous
                    if (previous && previous.status === "Playing" && player.status === "Playing" && !activity.busy && !(pendingSeek && pendingSeek.name === player.name && pendingSeek.track === player.track_id)) {
                        var predicted = position(previous)
                        var measured = position(player)
                        // Ignore sub-frame sampling drift; real seeks remain authoritative.
                        if (Math.abs(predicted - measured) < 0.35) {
                            player.position = predicted
                            player.sampled_at = clock
                        }
                    }
                    return player
                })
            }
            if (report.notifications) {
                if (JSON.stringify(report.notifications) !== JSON.stringify(notificationEntries))
                    notificationEntries = report.notifications
                report.notifications = notificationEntries
            }
            // Notification polling must not rebuild unchanged media/menu models.
            var next = Object.assign({}, state, report)
            if (JSON.stringify(next) !== JSON.stringify(state)) state = next
            settlePlaybackFeedback()
            settleSeekFeedback()
        } catch (e) {}
    }
    function refresh() { if (!busy && !readProcess.running) readProcess.running = true }
    function action(args) {
        if (args[0] === "media" && args[2] === "play-pause") {
            togglePlayback(state.players.find(function(value) { return value.name === args[1] }))
            return
        }
        if (busy) return
        if (args[0] === "notification" && notificationsProcess.running) notificationsProcess.running = false
        error = ""
        if (readProcess.running) readProcess.running = false
        actionProcess.command = ["/home/apx/.local/bin/apx-desktop-activity-v1"].concat(args)
        actionProcess.running = true
    }
    property Process readProcess: Process {
        command: ["/home/apx/.local/bin/apx-desktop-activity-v1", "get-media"]
        stdout: StdioCollector { onStreamFinished: activity.accept(text) }
    }
    property Process notificationsProcess: Process {
        command: ["/home/apx/.local/bin/apx-desktop-activity-v1", "get-notifications"]
        stdout: StdioCollector { onStreamFinished: activity.accept(text) }
    }
    property Timer notificationsTimer: Timer {
        interval: 500; running: true; repeat: true; triggeredOnStart: true
        onTriggered: if (!activity.busy && !activity.notificationsProcess.running) activity.notificationsProcess.running = true
    }
    property Process actionProcess: Process {
        onExited: function(code, status) {
            var completedPlayer = activity.sentPlayer
            var completedStatus = activity.sentStatus
            activity.sentPlayer = ""; activity.sentStatus = ""
            var completedSeek = activity.seekInFlight
            activity.seekInFlight = false
            if (code !== 0) {
                if (completedSeek) activity.clearSeekFeedback()
                activity.clearPlaybackFeedback(); activity.refresh(); return
            }
            activity.settleSeekFeedback()
            if (activity.pendingSeek && !activity.pendingSeek.sent) {
                Qt.callLater(function() { activity.sendSeek() })
                return
            }
            if (activity.pendingPlayer.length && (!completedPlayer.length || activity.pendingPlayer !== completedPlayer || activity.pendingStatus !== completedStatus)) {
                Qt.callLater(function() { activity.sendPlayback() })
            } else activity.settlePlaybackFeedback()
        }
        stdout: StdioCollector { onStreamFinished: activity.accept(text) }
        stderr: StdioCollector { onStreamFinished: if (text.trim().length) activity.error = text.trim() }
    }
    property Process watchProcess: Process {
        command: ["/home/apx/.local/bin/apx-desktop-activity-v1", "watch-media"]
        running: true
        stdout: SplitParser { onRead: function(data) { if (!activity.busy) activity.accept(data) } }
    }
    property Timer watchRestart: Timer {
        interval: 1000; repeat: true; running: !activity.watchProcess.running
        onTriggered: activity.watchProcess.running = true
    }
    property Timer timer: Timer { interval: 500; running: !activity.watchProcess.running; repeat: true; triggeredOnStart: true; onTriggered: activity.refresh() }
}
