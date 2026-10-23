from pathlib import Path
RELATIVES=['quickshell/apx/shell.qml', 'quickshell/apx/icons/lucide/paintbrush.svg']
def transform(rel,s):
 return (Path(__file__).parent/"assets"/rel).read_text()
