from pathlib import Path
RELATIVES=["quickshell/apx/shell.qml"]
def transform(rel,s):
 return (Path(__file__).parent/"shell.qml").read_text()
