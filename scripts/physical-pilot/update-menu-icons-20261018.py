from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'config/environment-shell-v1'
def shell(s):
 for name in ['package','box','book-a','layout-panel-left']:
  s=s.replace('return "'+name+'"','return "layout-grid"',1)
 for name in ['package-open','book-open','layout-dashboard','layout-grid']:
  s=s.replace('icons/lucide/'+name+'.svg','icons/lucide/layout-panel-left.svg')
  s=s.replace('alternateIconName: "'+name+'"','alternateIconName: "layout-panel-left"')
 pos=s.index('    readonly property bool filesFocused:')
 if 'readonly property bool filesOpen:' not in s:
  s=s[:pos]+'''    readonly property bool filesOpen: Hyprland.toplevels.values.some(function(window) {
        return /^(thunar|org\\.xfce\\.Thunar)$/i.test(String(window.wayland ? window.wayland.appId : window.lastIpcObject.class || ""))
    })
'''+s[pos:]
 s=s.replace('iconName: "folder"\n                    accessibleLabel:', 'iconName: "folder"\n                    alternateIconName: "folder-open"\n                    accessibleLabel:')
 s=s.replace('alternateActive: root.filesFocused && !popup.open && !environmentAppsProcess.running','alternateActive: root.filesOpen')
 s=s.replace('iconName: "calendar-days"\n','iconName: "calendar-days"\n                    alternateIconName: "calendar-search"\n',1) if 'alternateIconName: "calendar-search"' not in s else s
 s=s.replace('''            // Repeated shortcut requests must not cancel a pending launch.
            if (popup.open) root.closePopup()
            if (!environmentAppsProcess.running) environmentAppsProcess.running = true''','''            root.toggleApplicationLauncher()''')
 s=s.replace("WlrLayershell.keyboardFocus: open\n                                     ? WlrKeyboardFocus.Exclusive", "WlrLayershell.keyboardFocus: open\n                                     ? WlrKeyboardFocus.OnDemand")
 s=s.replace('''WlrLayershell.keyboardFocus: open && root.popupKeyboardRequested
                                     ? WlrKeyboardFocus.OnDemand''','''WlrLayershell.keyboardFocus: open
                                     ? WlrKeyboardFocus.OnDemand''')
 anchor='        WlrLayershell.keyboardFocus: environmentAppsProcess.running ? WlrKeyboardFocus.Exclusive : WlrKeyboardFocus.None'
 if 'enabled: environmentAppsProcess.running\n            onActivated:' not in s:
  s=s.replace(anchor,anchor+'''
        Shortcut {
            sequence: "Escape"
            enabled: environmentAppsProcess.running
            onActivated: environmentAppsProcess.running = false
        }''')
 s=s.replace('active: popup.open\n        onCleared:', 'active: false // The full-screen input mask handles outside clicks.\n        onCleared:')
 s=s.replace('WlrLayershell.keyboardFocus: open\n                                     ? WlrKeyboardFocus.OnDemand', 'WlrLayershell.keyboardFocus: open\n                                     ? WlrKeyboardFocus.Exclusive')
 s=s.replace("// Layer-shell Exclusive traps pointer delivery on the other monitor in\n    // this Hyprland build. Use the compositor's dismissible focus grab instead.", "// Exclusive keyboard input closes menus reliably with Escape.\n    // Outside clicks on this monitor use the full-screen popup input mask.")
 s=s.replace('    Timer { id: environmentArrivalTimer; interval: 1000 }\n    onStartupReadyChanged: if (startupReady) environmentArrivalTimer.restart()\n', '')
 s=s.replace('                    environmentArrival: environmentArrivalTimer.running\n', '')
 return s

def laptop(s):
 s=s.replace("--new-window", "--window")
 if '    # Runs as the Environment' in s:
  a=s.index('    # Runs as the Environment');b=s.index('    try:',a)
  s=s[:a]+'''    # Ask Thunar for a fresh window on every shortcut invocation.
    code = 'hl.exec_cmd("env -u GIO_USE_VFS USER=apx LOGNAME=apx HOME=/home/apx /usr/bin/thunar --window /home/apx")'
'''+s[b:]
 return s

def workspace(s):
 s=s.replace('    property bool environmentArrival: false\n', '')
 s=s.replace('    readonly property var focusedWorkspace: Hyprland.focusedWorkspace\n    onFocusedWorkspaceChanged: workspaceFlash.restart()\n    Timer { id: workspaceFlash; interval: 1000 }\n', '')
 s=s.replace('        alternateIconName: "bring-to-front"\n', '')
 s=s.replace('        alternateActive: strip.environmentArrival\n', '')
 s=s.replace('        alternateActive: workspaceFlash.running\n', '')
 s=s.replace('iconName: workspaceFlash.running ? "bring-to-front" : "square-stack"', 'iconName: "square-stack"')
 if 'id: workspaceSymbol\n        border.width: 0' not in s:
  s=s.replace('id: workspaceSymbol\n', 'id: workspaceSymbol\n        border.width: 0\n',1)
 return s

def activity(s):
 old='text: panel.kind === "media" ? (panel.renderedEntries.length ? "Em reprodução" : "Nada em reprodução") : (panel.entries.length ? "Notificações por ler" : "Sem notificações por ler")'
 new='visible: panel.kind !== "media"\n        text: panel.entries.length ? "Notificações por ler" : "Sem notificações por ler"'
 return s.replace(old,new)

def apps(s):
 s=s.replace(".config/quickshell/apx/icons/lucide", ".config/quickshell/apx/icons/rofi")
 s=s.replace('''    display = (f'<span foreground="{color}"><b>{symbol}</b></span>  '
               + html.escape(label))''','''    display = html.escape(label)
    icon = {'open': 'copy-plus', 'terminate': 'x', 'nvidia': 'cpu',
            'uninstall': 'trash-2', 'confirm': 'check', 'cancel': 'undo-2'}[action]
    icon_path = str(Path.home() / '.config/quickshell/apx/icons/rofi' / (icon + '.svg'))''')
 s=s.replace("+ action + ':' + value + '\\x1fmeta\\x1f' + name)","+ action + ':' + value + '\\x1fmeta\\x1f' + name + '\\x1ficon\\x1f' + icon_path)")
 return s
TRANSFORMS={'quickshell/apx/ActivityPanel.qml':activity,'quickshell/apx/shell.qml':shell,'quickshell/apx/WorkspaceStrip.qml':workspace,'local/bin/apx-laptop-action-v1':laptop,'local/bin/apx-window-apps-v1':apps}
if __name__=='__main__':
 for rel,transform in TRANSFORMS.items():
  p=BASE/rel;p.write_text(transform(p.read_text()))
