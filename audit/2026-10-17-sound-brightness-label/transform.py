from pathlib import Path
RELATIVES=["quickshell/apx/ControlDashboard.qml"]
def transform(rel,s):
 return (Path(__file__).parent/"ControlDashboard.qml").read_text()
