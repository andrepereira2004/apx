from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'config/environment-shell-v1'
AUDIT=Path(__file__).resolve().parent
RELATIVES=['quickshell/apx/shell.qml']
def transform(rel,s):
 s=s.replace('    property bool hotkeyOsdVisible: false', '    readonly property bool fullscreenOsd: focusedFullscreen && !popup.open\n    property bool hotkeyOsdVisible: false') if 'readonly property bool fullscreenOsd:' not in s else s
 s=s.replace('(!root.focusedFullscreen || popup.open)', '!root.fullscreenOsd')
 s=s.replace('root.hotkeyOsdVisible && (!root.mediaButton || !root.mediaButton.visible || (root.focusedFullscreen && !popup.open))', 'root.hotkeyOsdVisible && root.fullscreenOsd')
 s=s.replace('Math.min(transientActive ? 88 : selected ? 36 : 220, availableWidth)', '(transientActive ? 88 : Math.min(selected ? 36 : 220, availableWidth))')
 s=s.replace('availableWidth >= (transientActive ? 88 : selected ? 36 : 90)', '(transientActive || availableWidth >= (selected ? 36 : 90))')
 return s
