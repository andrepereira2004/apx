from pathlib import Path
REPO=Path(__file__).resolve().parents[2]
SOURCE=REPO/'config/environment-shell-v1'
AUDIT=Path(__file__).resolve().parent
RELATIVES=['quickshell/apx/MediaIsland.qml','quickshell/apx/shell.qml']
def transform(rel,s):
 if rel.endswith('/shell.qml'):
  return s.replace('transientActive ? 75 :', 'transientActive ? 88 :')
 s=s.replace('            horizontalAlignment: island.showingTransient ? Text.AlignRight : Text.AlignLeft\n', '')
 return s.replace('width: Math.min(implicitWidth, Math.max(0, island.width - 38))', 'width: island.showingTransient ? 36 : Math.min(implicitWidth, Math.max(0, island.width - 38))').replace('text: island.displayTitle; textFormat: Text.PlainText', 'horizontalAlignment: island.showingTransient ? Text.AlignRight : Text.AlignLeft\n            text: island.displayTitle; textFormat: Text.PlainText')
