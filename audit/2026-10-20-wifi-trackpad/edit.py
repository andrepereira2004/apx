from pathlib import Path
base=Path('config/environment-shell-v1')
p=base/'quickshell/apx/shell.qml';s=p.read_text()
# Reuse the existing local preference flow and controls for each independent setting.
functions=s[s.index('    function setMouseSensitivity(value)'):s.index('    property color cyan:')]
card=s[s.index('                    Rectangle {\n                        width: parent.width; height: 72; radius: 11; color: root.controlButtonSurface\n                        border.width: 1; border.color: root.controlButtonOutline\n                        IconLabel {'):s.index('                    MenuButton { outlined: true; iconName: "keyboard"; label: "Lista de atalhos"')]
for kind,label,icon,default in [('trackpad','Sensibilidade do trackpad','touchpad',-30),('menuScroll','Velocidade do scroll nos menus','touchpad',100)]:
    cap=kind[0].upper()+kind[1:]
    f=functions.replace('MouseSensitivity',cap+'Sensitivity').replace('mouseSensitivity',kind+'Sensitivity').replace('apx-mouse-sensitivity-v1','apx-'+kind+'-sensitivity-v1').replace(' || 0',' || '+str(default))
    s=s.replace('    property color cyan:',f+'    property color cyan:',1)
    s=s.replace('    property int mouseSensitivity: 0',f'    property int {kind}Sensitivity: {default}\n    property string {kind}SensitivityError: ""\n    property int mouseSensitivity: 0',1)
    c=card.replace('MouseSensitivity',cap+'Sensitivity').replace('mouseSensitivity',kind+'Sensitivity').replace('Sensibilidade do rato',label).replace('iconName: "mouse"',f'iconName: "{icon}"')
    if kind=='menuScroll':c=c.replace('from: -100; to: 100','from: 25; to: 300')
    s=s.replace('                    MenuButton { outlined: true; iconName: "keyboard"; label: "Lista de atalhos"',c+'                    MenuButton { outlined: true; iconName: "keyboard"; label: "Lista de atalhos"',1)
# Selecting any network brings the complete form into view before focusing a field.
s=s.replace('        if (!wifiIsKnown(name) && !wifiIsOpen(name)) {\n            Qt.callLater(function() {','        Qt.callLater(function() {\n            if (!root.wifiPasswordVisible || root.wifiSelectedSsid !== name) return\n            menuFlick.cancelFlick()\n            menuFlick.contentY = 0\n        })\n        if (!wifiIsKnown(name) && !wifiIsOpen(name)) {\n            Qt.callLater(function() {',1)
s=s.replace('text: "Ligar a " + root.wifiSelectedSsid','text: root.wifiSelectedSsid')
s=s.replace('color: root.controlButtonSurface; border.width: 1; border.color: root.controlButtonOutline\n                            Column {\n                                anchors.fill: parent; anchors.margins: 8; spacing: 5','color: root.controlButtonSurface; border.width: 1; border.color: root.cyan\n                            Column {\n                                anchors.fill: parent; anchors.margins: 8; spacing: 5',1)
s=s.replace('model: root.hostState.available_networks || []\n                            Rectangle {','model: Array.from(new Set(root.hostState.available_networks || []))\n                            Rectangle {',1)
s=s.replace('enabled: root.wifiSelectedSsid !== root.hostState.network_name; hoverEnabled:', 'enabled: !wifiCredentialProcess.running && !hostActionProcess.running && root.wifiSelectedSsid !== root.hostState.network_name; hoverEnabled:',1)
s=s.replace('text: wifiCredentialProcess.running ? "A ligar…" : (root.wifiSelectedSsid', 'text: (wifiCredentialProcess.running || hostActionProcess.running) ? "A ligar…" : (root.wifiSelectedSsid',1)
s=s.replace('        if (wifiIsKnown(wifiSelectedSsid) || wifiIsOpen(wifiSelectedSsid)) {','        if (wifiCredentialProcess.running || hostActionProcess.running) return\n        if (wifiIsKnown(wifiSelectedSsid) || wifiIsOpen(wifiSelectedSsid)) {',1)
# Prevent native wheel + handler double scrolling. The compositor has already scaled input.
s=s.replace('                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOff }','''                WheelHandler {
                    target: null
                    onWheel: event => {
                        var delta = event.pixelDelta.y || event.angleDelta.y / 120 * 48
                        if (!delta) return
                        menuFlick.cancelFlick()
                        menuFlick.contentY = Math.max(0, Math.min(Math.max(0, menuFlick.contentHeight - menuFlick.height), menuFlick.contentY - delta * root.menuScrollSensitivity / 100 * 2.5))
                        event.accepted = true
                    }
                }
                ScrollBar.vertical: ScrollBar { policy: ScrollBar.AlwaysOff }''',1)
p.write_text(s)
# Dedicated trackpad helper; external mice remain excluded.
p=base/'local/bin/apx-mouse-sensitivity-v1';helper=p.read_text().replace('external mouse pointer','trackpad pointer').replace('apx-mouse-sensitivity.lua','apx-trackpad-sensitivity.lua').replace('APX mouse sensitivity','APX trackpad sensitivity').replace('apx-mouse-sensitivity-v1','apx-trackpad-sensitivity-v1').replace('else 0.0','else -0.30').replace('return 0.0','return -0.30').replace('and "touchpad" not in','and "touchpad" in').replace('Nenhum rato externo está ligado','Nenhum trackpad está ligado').replace('configuração de rato','configuração de trackpad').replace('alteração do rato','alteração do trackpad')
p=base/'local/bin/apx-trackpad-sensitivity-v1';p.write_text(helper);p.chmod(0o755)
p=base/'local/bin/apx-menuScroll-sensitivity-v1';p.write_text('''#!/usr/bin/env python3
"""Environment-local menu scroll preference, expressed as a percentage."""
import os
from pathlib import Path
import sys
CONFIG = Path.home() / ".config/apx-menu-scroll-v1"
try:
    if sys.argv[1:] == ["get"]:
        try:
            value = int(CONFIG.read_text())
        except (OSError, ValueError):
            value = 100
        print(max(25, min(300, value)))
    elif len(sys.argv) == 3 and sys.argv[1] == "set":
        value = int(sys.argv[2])
        if not 25 <= value <= 300:
            raise ValueError("O scroll deve estar entre 25% e 300%")
        CONFIG.parent.mkdir(parents=True, exist_ok=True)
        temporary = CONFIG.with_name(CONFIG.name + f".{os.getpid()}.tmp")
        try:
            with temporary.open("x") as stream:
                os.chmod(temporary, 0o600)
                stream.write(str(value) + "\\n")
            os.replace(temporary, CONFIG)
        finally:
            temporary.unlink(missing_ok=True)
        print(value)
    else:
        raise ValueError("Argumentos inválidos")
except (OSError, ValueError) as error:
    print(str(error), file=sys.stderr)
    raise SystemExit(2)
''');p.chmod(0o755)
p=base/'hypr/hyprland.lua';s=p.read_text();s+='''\n-- Environment-local trackpad preference from the Control Centre.
local trackpadChoice = "/home/apx/.config/hypr/apx-trackpad-sensitivity.lua"
local trackpadChoiceFile = io.open(trackpadChoice, "r")
if trackpadChoiceFile then
    trackpadChoiceFile:close()
    dofile(trackpadChoice)
end
''';p.write_text(s)
p=Path('scripts/physical-pilot/deploy-wifi-trackpad-20261020.py');s=Path('scripts/physical-pilot/deploy-wifi-minimal-20261019.py').read_text().replace('2026-10-19-wifi-minimal','2026-10-20-wifi-trackpad').replace('-wifi-minimal','-wifi-trackpad').replace("['quickshell/apx/shell.qml']","['quickshell/apx/shell.qml', 'hypr/hyprland.lua', 'local/bin/apx-trackpad-sensitivity-v1', 'local/bin/apx-menuScroll-sensitivity-v1']").replace("assert path.is_file() or rel.endswith('.svg'),path","assert path.is_file() or rel.startswith('local/bin/'),path").replace("mode=stat.st_mode&0o777 if existed else 0o644","mode=stat.st_mode&0o777 if existed else (0o755 if '/bin/' in str(path) else 0o644)")
p.write_text(s)
