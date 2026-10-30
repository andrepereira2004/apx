from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'config/environment-shell-v1'
AUDIT=Path(__file__).resolve().parent
RELATIVES=['quickshell/apx/shell.qml']
def transform(rel,s):
 return s.replace('Hyprland.activeToplevel && Hyprland.activeToplevel.lastIpcObject.fullscreen > 0', 'Hyprland.activeToplevel && Hyprland.activeToplevel.wayland && Hyprland.activeToplevel.wayland.fullscreen')
