from pathlib import Path
RELATIVES=["quickshell/apx/shell.qml","quickshell/apx/WorkspaceStrip.qml","hypr/hyprland.lua","quickshell/apx/DesktopActivity.qml","quickshell/apx/MediaTimeline.qml"]
def transform(rel,s):
 if rel == "hypr/hyprland.lua":
  if "ipc call host toggleWorkspaces" not in s:
   s += '\n-- Toggle workspace labels while keeping their icon in the bar.\nhl.bind(mainMod .. " + W", hl.dsp.exec_cmd("quickshell -c apx ipc call host toggleWorkspaces"))\n'
  return s
 return (Path(__file__).parent/Path(rel).name).read_text()
