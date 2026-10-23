from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'config/environment-shell-v1'
AUDIT=Path(__file__).resolve().parent
RELATIVES=['quickshell/apx/shell.qml','quickshell/apx/MediaIsland.qml','quickshell/apx/WorkspaceStrip.qml','quickshell/apx/icons/lucide/audio-lines.svg','quickshell/apx/icons/lucide/square-stack.svg','rofi/config.rasi']
def once(s,a,b):
 assert s.count(a)==1,(a[:100],s.count(a));return s.replace(a,b,1)
def finish_shell(s):
 if '// APX shared launcher pointer focus' not in s:
  s=once(s, '        WlrLayershell.layer: popup.open || environmentAppsProcess.running ? WlrLayer.Overlay : WlrLayer.Top\n        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None', '        WlrLayershell.layer: popup.open || environmentAppsProcess.running ? WlrLayer.Overlay : WlrLayer.Top\n        // APX shared launcher pointer focus: Hyprland hits only exclusive surfaces while Rofi owns focus.\n        WlrLayershell.keyboardFocus: environmentAppsProcess.running ? WlrKeyboardFocus.Exclusive : WlrKeyboardFocus.None')
 return s

def shell(s):
 if '// APX queued main menu switch' in s:return finish_shell(s)
 s=once(s,'    property string popupKind: ""','''    // APX queued main menu switch: never reveal a new page at the old anchor.
    property var pendingPopupRequest: null
    property string popupKind: ""''')
 s=once(s,'    function finishClosePopup() {','''    function finishClosePopup() {
        var pending = pendingPopupRequest
        pendingPopupRequest = null''')
 s=once(s,'        calendarFocusAction = ({ kind: "", key: "" })\n    }','''        calendarFocusAction = ({ kind: "", key: "" })
        if (pending && pending.target) {
            root.togglePopup(pending.kind, pending.target, pending.keyboardRequested)
            if (pending.controlSection === "more") root.openMoreOptions()
            else if (pending.controlSection === "shortcuts") root.shortcutsOpen = true
            else if (pending.controlSection && pending.controlSection.length) root.openControlSection(pending.controlSection)
            root.syncRenderedControls()
        }
    }''')
 s=once(s,'    function togglePopup(kind, target, keyboardRequested) {\n        if (!target) return','''    function togglePopup(kind, target, keyboardRequested) {
        if (!target) return
        if (popup.open && root.popupKind !== kind) {
            pendingPopupRequest = {kind: kind, target: target, keyboardRequested: keyboardRequested === true}
            root.closePopup()
            return
        }
        pendingPopupRequest = null''')
 # IPC shortcuts must obey the same anchor/close sequence as bar pointer navigation.
 s=once(s,'    function toggleFocusedPopup(kind) {','''    function queueControlPage(section) {
        if (!popup.open || root.popupKind === "controls") return false
        root.toggleFocusedPopup("controls")
        if (pendingPopupRequest) pendingPopupRequest.controlSection = section
        return true
    }

    function toggleFocusedPopup(kind) {''')
 for name,section in [('openControls',''),('openWifiControls','wifi'),('openMoreControls','more'),('openBluetoothControls','bluetooth'),('openVolumeControls','audio'),('openMicrophoneControls','microphone'),('openShortcuts','shortcuts')]:
  if name == 'openShortcuts' and f'function {name}(): void' not in s:continue
  s=once(s,f'        function {name}(): void {{',f'        function {name}(): void {{\n            if (root.queueControlPage("{section}")) return')
 s=once(s,'duration: 240; easing.type: Easing.InOutCubic\n                onFinished: if (root.popupClosing)', 'duration: root.pendingPopupRequest ? 140 : 240; easing.type: Easing.InOutCubic\n                onFinished: if (root.popupClosing)')
 s=once(s,'        if (popupKind === "controls") return Math.max(left, right)', '        if (popupKind === "controls" || popupKind === "media") return Math.max(left, right)')
 s=once(s,'width: Math.min(transientActive ? 150 : 220, availableWidth) * presence','width: Math.min(transientActive ? 75 : selected ? 36 : 220, availableWidth) * presence')
 s=once(s,'availableWidth >= 90','availableWidth >= (transientActive ? 75 : selected ? 36 : 90)')
 s=once(s,'transientActive: root.hotkeyOsdVisible && root.bar === screenBar && !popup.open && !root.focusedFullscreen','transientActive: root.hotkeyOsdVisible && root.bar === screenBar && (!root.focusedFullscreen || popup.open)')
 s=once(s,'expandedAmount: root.bar === screenBar && popup.open && root.popupKind === "media" ? root.islandProgress : 0','selected: root.bar === screenBar && popup.open && root.popupKind === "media" && !root.popupClosing')
 s=once(s,'visible: root.hotkeyOsdVisible && (!root.mediaButton || !root.mediaButton.visible || popup.open || root.focusedFullscreen)','visible: root.hotkeyOsdVisible && (!root.mediaButton || !root.mediaButton.visible || (root.focusedFullscreen && !popup.open))')
 s=once(s,'        WlrLayershell.layer: WlrLayer.Top\n        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None','        WlrLayershell.layer: popup.open || environmentAppsProcess.running ? WlrLayer.Overlay : WlrLayer.Top\n        WlrLayershell.keyboardFocus: WlrKeyboardFocus.None')
 # Passive diagnostics, without media titles or other private display content.
 s=once(s,'                                    files_active: root.filesFocused,', '''                                    pending_kind: root.pendingPopupRequest ? root.pendingPopupRequest.kind : "",
                                    media_width: root.mediaButton ? root.mediaButton.width : 0, media_selected: root.mediaButton ? root.mediaButton.selected : false,
                                    osd_fallback: hotkeyOsdWindow.visible, launcher_running: environmentAppsProcess.running,
                                    media_summary_width: root.mediaButton ? root.mediaButton.summaryWidth : 0, media_summary_x: root.mediaButton ? root.mediaButton.summaryX : 0,
                                    bar_targets: ({ calendar: root.barTargetRect(root.calendarButton), controls: root.barTargetRect(root.controlCenterButton), media: root.barTargetRect(root.mediaButton) }),
                                    files_active: root.filesFocused,''')
 s=once(s,'    function popupBarTargetAt(x, y) {','''    function barTargetRect(button) {
        if (!button || !bar) return null
        var point = button.mapToItem(bar.contentItem, 0, 0)
        return {x: point.x + bar.margins.left, y: point.y + bar.margins.top, width: button.width, height: button.height}
    }

    function popupBarTargetAt(x, y) {''')
 return finish_shell(s)

def transform(rel,s):
 if rel.endswith('/shell.qml'):return shell(s)
 if rel.endswith('/MediaIsland.qml'):return (AUDIT/'MediaIsland.qml').read_text()
 if rel.endswith('/WorkspaceStrip.qml'):
  if 'id: workspaceSymbol' not in s:
   s=once(s,'    Repeater {','''    Item {
        id: workspaceSymbol
        width: 30; height: 32
        LucideIcon { anchors.centerIn: parent; name: "square-stack"; width: 17; height: 17 }
        Accessible.role: Accessible.StaticText
        Accessible.name: "Workspaces"
    }

    Repeater {''')
  return s
 if rel.endswith('.svg'):return (AUDIT/Path(rel).name).read_text()
 if rel=='rofi/config.rasi':
  s=s.replace('height: calc(100% - 46px);', 'height: 100%;')
  return s.replace('window { fullscreen: true; background-color: transparent; border: 0px; padding: 0px; }','window { fullscreen: false; location: south; anchor: south; width: 100%; height: 100%; background-color: transparent; border: 0px; padding: 0px; }')
 return s
