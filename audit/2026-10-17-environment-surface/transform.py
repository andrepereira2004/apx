from pathlib import Path
RELATIVES=["quickshell/apx/BarButton.qml"]
def transform(rel,s):
 return (Path(__file__).parent/"BarButton.qml").read_text()
