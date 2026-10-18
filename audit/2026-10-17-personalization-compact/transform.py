from pathlib import Path
RELATIVES=['quickshell/apx/PersonalizationPanel.qml', 'quickshell/apx/ControlDashboard.qml', 'quickshell/apx/ControlTile.qml', 'quickshell/apx/shell.qml', 'quickshell/apx/Appearance.qml', 'local/bin/apx-appearance-v1', 'rofi/config.rasi', 'quickshell/apx/icons/lucide/paintbrush.svg']
def transform(rel,s):
 return (Path(__file__).parent/"assets"/rel).read_text()
