import QtQuick
import Quickshell
import "file:/home/apx/.config/quickshell/apx" as Apx
ShellRoot {
    property int stage: 0
    property var checks: []
    property var sample: ({name: "org.mpris.MediaPlayer2.presence_test", status: "Playing", title: "Presence test", artist: "", track_id: "/test/one", kind: "music", length: 120, position: 10, sampled_at: Date.now(), rate: 1, can_control: true, can_seek: true})
    function setState(status) {
        Apx.DesktopActivity.state = ({players: status === "Absent" ? [] : [Object.assign({}, sample, {status: status})], notifications: [], active_notifications: 0})
    }
    function verify(condition, message) {
        if (!condition) { console.error("FAIL " + message); Qt.exit(1) }
        checks.push(message)
    }
    FloatingWindow {
        visible: true; implicitWidth: 700; implicitHeight: 600
        Apx.MediaIsland { id: barMedia; width: 200; y: 550 }
        Apx.ActivityPanel { id: embedded; x: 0; width: 320; embedded: true; kind: "media" }
        Apx.ActivityPanel { id: dedicated; x: 350; width: 320; showBack: false; kind: "media" }
    }
    Component.onCompleted: {
        Apx.DesktopActivity.watchRestart.running = false
        Apx.DesktopActivity.watchProcess.running = false
        Apx.DesktopActivity.notificationsTimer.running = false
        Apx.DesktopActivity.timer.running = false
        Apx.DesktopActivity.readProcess.running = false
        setState("Playing")
    }
    Timer {
        interval: 100; running: true; repeat: true
        onTriggered: {
            ++stage
            if (stage === 29) {
                verify(barMedia.presence === 1 && barMedia.displayTitle === "Volume · 50%", "OSD appears without a player")
                setState("Playing")
                verify(barMedia.displayTitle === "Volume · 50%", "transient keeps priority over arriving playback")
                barMedia.transientActive = false
                verify(barMedia.displayTitle === sample.title && barMedia.presence === 1, "playback returns without hiding the island")
                barMedia.expandedAmount = .5
                verify(barMedia.opacity === .5, "capsule yields to its expanding media panel")
                barMedia.expandedAmount = 0
            }
            if (stage === 30) {
                setState("Absent"); barMedia.transientTitle = "Brilho"; barMedia.transientActive = true
            }
            if (stage === 34) barMedia.transientActive = false
            if (stage === 35) {
                verify(barMedia.presence > 0 && barMedia.presence < 1, "transient exits progressively")
                verify(barMedia.displayTitle.indexOf("Brilho") === 0, "transient snapshot survives exit")
                barMedia.transientActive = true
            }
            if (stage === 39) {
                verify(barMedia.presence === 1, "a repeated transient reverses the current exit")
                barMedia.transientActive = false
            }
            if (stage === 43) {
                verify(barMedia.presence === 0, "transient fully disappears without stale media")
                console.log("TRANSIENT_PASS " + JSON.stringify(checks)); Qt.quit()
            }
            if (stage === 4) {
                verify(embedded.height > 0 && dedicated.height > 0, "playing visible in both")
                setState("Paused")
            }
            if (stage === 8) {
                verify(embedded.entries.length === 1 && embedded.reveal === 1, "pause retains control-centre card")
                verify(dedicated.entries.length === 1 && dedicated.reveal === 1, "pause retains dedicated card")
                setState("Stopped")
            }
            if (stage === 9) {
                verify(embedded.reveal === 1, "exit preserves full height during fade")
                verify(embedded.contentOpacity > 0 && embedded.contentOpacity < 1, "menu visibly fades before collapse")
                verify(barMedia.presence > 0 && barMedia.presence < 1, "bar widget visibly fades")
                verify(embedded.renderedEntries.length === 1 && barMedia.player !== null, "exit retains both snapshots")
            }
            if (stage === 11) verify(embedded.reveal > 0 && embedded.reveal < 1, "collapse follows fade")
            if (stage === 14) {
                verify(embedded.height === 0 && dedicated.height === 0 && barMedia.presence === 0, "stopped hides menus and bar after animations")
                setState("Paused")
            }
            if (stage === 15) verify(embedded.reveal > 0 && embedded.reveal < 1 && barMedia.presence > 0 && barMedia.presence < 1, "menus and bar animate entrance")
            if (stage === 19) {
                verify(embedded.reveal === 1 && dedicated.reveal === 1 && barMedia.presence === 1, "paused persists in all three widgets")
                sample = Object.assign({}, sample, {position: sample.length})
                setState("Paused")
            }
            if (stage === 20) {
                verify(embedded.entries.length === 0 && dedicated.entries.length === 0, "paused at EOF is finished in both menus")
                verify(embedded.contentOpacity > 0 && embedded.contentOpacity < 1 && barMedia.presence > 0 && barMedia.presence < 1, "EOF fades menus and bar")
            }
            if (stage === 25) {
                verify(embedded.reveal === 0 && dedicated.reveal === 0 && barMedia.presence === 0, "EOF completes animated exit")
                console.log("PRESENCE_PASS " + JSON.stringify(checks))
                setState("Absent")
                barMedia.transientTitle = "Volume"; barMedia.transientDetail = "50%"; barMedia.transientProgress = 50
                barMedia.transientActive = true
            }
        }
    }
}
