from pathlib import Path
RELATIVES=["quickshell/apx/ControlDashboard.qml","quickshell/apx/shell.qml"]
def transform(rel,s):
 return (Path(__file__).parent/Path(rel).name).read_text()
