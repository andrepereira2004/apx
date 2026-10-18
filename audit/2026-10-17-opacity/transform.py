from pathlib import Path
RELATIVES=['local/bin/apx-appearance-v1', 'quickshell/apx/Appearance.qml', 'quickshell/apx/PersonalizationPanel.qml', 'quickshell/apx/shell.qml', 'quickshell/apx/BarButton.qml', 'quickshell/apx/MediaIsland.qml']
def transform(rel,s):
 return (Path(__file__).parent/"assets"/rel).read_text()
