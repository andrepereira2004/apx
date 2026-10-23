from pathlib import Path
RELATIVES=["quickshell/apx/shell.qml","quickshell/apx/GhostLines.js"]
def transform(rel,s):
 return (Path(__file__).parent/Path(rel).name).read_text()
