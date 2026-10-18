from pathlib import Path
RELATIVES=['quickshell/apx/ControlSlider.qml', 'quickshell/apx/Appearance.qml', 'quickshell/apx/PersonalizationPanel.qml', 'quickshell/apx/shell.qml']
def transform(rel,s):
 return (Path(__file__).parent/"assets"/rel).read_text()
