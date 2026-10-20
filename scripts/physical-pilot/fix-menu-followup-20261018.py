from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=ROOT/'scripts/physical-pilot/deploy-menu-icons-20261018.py'
s=p.read_text().replace("'undo-2','check','x']","'undo-2','check','x','bring-to-front']")
s=s.replace('            target=config/rel','            target=(directory/"home/apx/.local"/rel.removeprefix("local/")) if rel.startswith("local/") else config/rel')
p.write_text(s)
p=ROOT/'scripts/physical-pilot/update-menu-icons-20261018.py';s=p.read_text();a=s.index('def workspace(s):');b=s.index('\ndef apps(s):',a)
s=s[:a]+'''def workspace(s):
 s=s.replace('    readonly property var focusedWorkspace: Hyprland.focusedWorkspace\\n    onFocusedWorkspaceChanged: workspaceFlash.restart()\\n    Timer { id: workspaceFlash; interval: 1000 }\\n', '')
 s=s.replace('iconName: "box"\\n        alternateActive: workspaceFlash.running', 'iconName: "square-stack"')
 if 'property bool environmentArrival' not in s:
  s=s.replace('    signal toggleRequested()', '    property bool environmentArrival: false\\n    signal toggleRequested()')
  s=s.replace('iconName: "square-stack"', 'iconName: "square-stack"\\n        alternateIconName: "bring-to-front"\\n        alternateActive: strip.environmentArrival')
 return s
''' +s[b:]
anchor=' return s\n\ndef laptop'
s=s.replace(anchor,''' if 'id: environmentArrivalTimer' not in s:
  s=s.replace('    readonly property var openWorkspaces:', '    Timer { id: environmentArrivalTimer; interval: 1000 }\\n    onStartupReadyChanged: if (startupReady) environmentArrivalTimer.restart()\\n    readonly property var openWorkspaces:',1)
  s=s.replace('id: workspaceStrip\\n', 'id: workspaceStrip\\n                    environmentArrival: environmentArrivalTimer.running\\n',1)
 return s

def laptop''')
p.write_text(s)
