import QtQuick
import Quickshell
import "file:/home/apx/.config/quickshell/apx" as Apx
ShellRoot {
    id: test
    property int stage: 0
    property int ticks: 0
    readonly property var player: Apx.DesktopActivity.state.players.find(function(p) { return p.name === "org.mpris.MediaPlayer2.apx_trial" }) || null
    function verify(condition, message) { if (!condition) { console.error("FEEDBACK_FAIL " + message); Qt.exit(1) } }
    FloatingWindow {
        visible: true; implicitWidth: 100; implicitHeight: 70
        Apx.ControlTile {
            id: button
            width: 90; height: 50
            playbackToggle: true
            playing: test.player ? Apx.DesktopActivity.playbackIcon(test.player) === "pause" : false
            onActivated: Apx.DesktopActivity.togglePlayback(test.player)
        }
    }
    Timer {
        interval: 20; running: true; repeat: true
        onTriggered: {
            ++test.ticks
            if (test.ticks > 150) { test.verify(false,"timeout waiting for confirmed rapid toggle"); return }
            if (test.stage === 0 && test.player) {
                test.verify(test.player.status === "Playing", "initial test player must play")
                button.activated()
                test.verify(!button.playing, "first click must swap icon synchronously")
                test.stage = 1
            } else if (test.stage === 1) {
                button.activated()
                test.verify(button.playing, "second click must swap back synchronously")
                test.stage = 2
            } else if (test.stage === 2) {
                test.verify(button.playing,"icon must never revert during confirmation")
                if (!Apx.DesktopActivity.busy && Apx.DesktopActivity.pendingPlayer === "") {
                    test.verify(test.player.status === "Playing","last requested playback state must be confirmed")
                    console.log("FEEDBACK_PASS instant icons, rapid-toggle queue, stable confirmation; ticks=" + test.ticks)
                    Qt.quit()
                }
            }
        }
    }
}
