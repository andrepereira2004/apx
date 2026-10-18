from pathlib import Path
RELATIVES=['quickshell/apx/ControlDashboard.qml', 'quickshell/apx/shell.qml', 'quickshell/apx/MediaTimeline.qml']
def transform(rel,s):
 return (Path(__file__).parent/"assets"/rel).read_text()
