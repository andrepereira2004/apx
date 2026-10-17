from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'config/environment-shell-v1'
AUDIT=Path(__file__).resolve().parent
RELATIVES=['quickshell/apx/ControlDashboard.qml','quickshell/apx/shell.qml']
def transform(rel,s):
 if rel.endswith('/ControlDashboard.qml'):
  s=s.replace('    readonly property bool mediaTransitionRunning: playback.transitioning\n','')
  if '        ActivityPanel { id: playback;' in s:
   a=s.index('    Rectangle {\n        width: dashboard.width; height: playback.')
   b=s.index('    Rectangle {\n        width: dashboard.width; height: levels.',a)
   s=s[:a]+s[b:]
  return s
 s=s.replace(' && !(root.popupKind === "controls" && root.renderedControlsAllClosed() && !root.renderedControls.controlsMoreOpen && compactDashboard.mediaTransitionRunning)','')
 s=s.replace('value: popup.open && (root.popupKind === "media" || (root.popupKind === "controls" && root.controlsAllClosed()))','value: popup.open && root.popupKind === "media"')
 return s
