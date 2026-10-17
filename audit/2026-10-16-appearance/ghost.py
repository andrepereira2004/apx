def ghost(text):
    if 'function refreshGhostGreeting()' in text:return text
    text=text.replace('import Quickshell.Widgets','import Quickshell.Widgets\nimport "GhostLines.js" as GhostLines',1)
    anchor='    property string controlsActivityKind: ""'
    text=text.replace(anchor,anchor+'\n    property string ghostMessage: ""\n    property var ghostRecent: []')
    anchor='    function showPopup() {'
    method='''    function refreshGhostGreeting() {
        var apps = []; var count = 0
        var seen = ({})
        for (var i=0; i<openWorkspaces.length; ++i) {
            var windows = openWorkspaces[i].toplevels.values
            for (var j=0; j<windows.length; ++j) {
                var window = windows[j]
                var data = window.lastIpcObject || ({})
                var key = data.address || String(window)
                if (seen[key]) continue
                seen[key] = true; ++count
                apps.push(window.wayland ? window.wayland.appId : (data.class || ""))
            }
        }
        var playing = (DesktopActivity.state.players || []).filter(function(p) {return p.status === "Playing"})
        var chosen = GhostLines.pick({ now: new Date(), environment: environmentIdentity.name || (isHub ? "hub" : ""), apps: apps, count: count, media: playing.length ? playing[0].kind : "" }, ghostRecent)
        ghostMessage = chosen.text
        ghostRecent = ghostRecent.concat([chosen.id]).slice(-200)
    }

'''
    text=text.replace(anchor,method+anchor+'\n        if (root.popupKind === "controls") root.refreshGhostGreeting()',1)
    text=text.replace('visible: root.popupKind !== "calendar" && !(root.popupKind === "controls" && root.controlsAllClosed() && !root.controlsMoreOpen && !root.shortcutsOpen)','visible: root.popupKind !== "calendar"')
    return text
