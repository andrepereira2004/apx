from pathlib import Path
import re
BASE=Path('config/environment-shell-v1/quickshell/apx')
p=BASE/'Appearance.qml';s=p.read_text().replace('    readonly property int menuTop: 65','    readonly property int menuActionHeight: 44\n    readonly property int menuActionRadius: 14\n    readonly property int menuTop: 65',1);p.write_text(s)
p=BASE/'shell.qml';s=p.read_text()
# Instance dimensions precede nested objects and action handlers.
for match in reversed(list(re.finditer(r'\bMenuButton\s*\{',s))):
 a=match.end();b=s.find('{',a);part=s[a:b]
 part=re.sub(r'\bheight:\s*[^;\n]+',lambda m:'height: '+('visible ? Appearance.menuActionHeight : 0' if 'visible ?' in m[0] else 'Appearance.menuActionHeight'),part,count=1)
 part=re.sub(r'\bradius:\s*\d+', 'radius: Appearance.menuActionRadius',part,count=1)
 s=s[:a]+part+s[b:]
a=s.index('    component MenuButton:');b=s.index('    component EventField:',a);part=s[a:b].replace('height: 34','height: Appearance.menuActionHeight',1).replace('radius: brightActionHover ? 10 : 6','radius: Appearance.menuActionRadius',1);s=s[:a]+part+s[b:]
# Action rows must reserve the shared height too.
s=s.replace('width: parent.width; height: 42; spacing: 6\n                            MenuButton','width: parent.width; height: Appearance.menuActionHeight; spacing: 6\n                            MenuButton',1)
s=s.replace('width: parent.width; height: 36; spacing: 4\n                        Repeater {\n                            model: root.modelStoreState.models','width: parent.width; height: Appearance.menuActionHeight; spacing: 4\n                        Repeater {\n                            model: root.modelStoreState.models',1)
s=s.replace('width: parent.width; height: 34; spacing: 6\n                                MenuButton','width: parent.width; height: Appearance.menuActionHeight; spacing: 6\n                                MenuButton',1)
# Control tiles use the same height as text actions, including connectivity.
for match in reversed(list(re.finditer(r'\bControlTile\s*\{',s))):
 a=match.end();b=s.find('{',a);part=s[a:b];part=re.sub(r'\bheight:\s*\d+', 'height: Appearance.menuActionHeight',part,count=1);s=s[:a]+part+s[b:]
# Single-row control cards retain room for the 36px action circle at 44px high.
for idname in ('combinedVolumeCard','combinedBrightnessCard','mouseSensitivityCard','trackpadSensitivityCard'):
 a=s.find('id: '+idname)
 if a>=0:
  b=s.find('{',a);part=s[a:b].replace('height: 56','height: Appearance.menuActionHeight');s=s[:a]+part+s[b:]
# Existing clickable calendar cells/actions share the compact action height.
a=s.index('id: calendarMenu');b=s.index('id: environmentMenu',a);part=s[a:b]
part=re.sub(r'height: (?:25|28|30|34)(?=\s*[;\n])','height: Appearance.menuActionHeight',part)
part=part.replace('width: 32; height: Appearance.menuActionHeight','width: Appearance.menuActionHeight; height: Appearance.menuActionHeight').replace('width: parent.width - 72; height: Appearance.menuActionHeight','width: parent.width - Appearance.menuActionHeight * 2 - 8; height: Appearance.menuActionHeight')
s=s[:a]+part+s[b:]
# Environment catalogue rows and back control align with all other menu actions.
s=s.replace('width: parent ? parent.width : 400; height: 44; radius: 12','width: parent ? parent.width : 400; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius',1)
s=s.replace('width: parent.width; height: 46; radius: 12','width: parent.width; height: Appearance.menuActionHeight; radius: Appearance.menuActionRadius',1)
s=s.replace('width: parent.width; height: 32; spacing: 8\n                            Rectangle {\n                                width: 92; height: parent.height','width: parent.width; height: Appearance.menuActionHeight; spacing: 8\n                            Rectangle {\n                                width: 92; height: parent.height',1)
# System choice tiles are actionable, so they use the shared dimension too.
s=s.replace('width: parent.width; height: 60; spacing: 8','width: parent.width; height: Appearance.menuActionHeight; spacing: 8',1)
p.write_text(s)
p=BASE/'ControlTile.qml';s=p.read_text().replace('implicitHeight: 36','implicitHeight: Appearance.menuActionHeight',1).replace('radius: 9','radius: Appearance.menuActionRadius',1);p.write_text(s)
p=BASE/'ControlDashboard.qml';s=p.read_text();s=re.sub(r'height: (?:40|64)(?=;)', 'height: Appearance.menuActionHeight',s);p.write_text(s)
p=Path('scripts/physical-pilot/deploy-environments-minimal-20261020.py');s=p.read_text().replace("RELATIVES = ['quickshell/apx/shell.qml']", "RELATIVES = ['quickshell/apx/Appearance.qml', 'quickshell/apx/ControlTile.qml', 'quickshell/apx/ControlDashboard.qml', 'quickshell/apx/shell.qml']",1);p.write_text(s)
p=Path('audit/2026-10-20-environment-create/validate-form.py');s=p.read_text().replace('property int motionDuration:100','property int motionDuration:100; property int menuActionHeight:44; property int menuActionRadius:14');p.write_text(s)
