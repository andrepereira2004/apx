from pathlib import Path
import re
base=Path('config/environment-shell-v1/quickshell/apx')
p=base/'shell.qml';s=p.read_text()
s=s.replace('menuMouse.containsMouse ? 1.8 : 1.5','1.5')
s=re.sub(r'\b\w+\.containsMouse(?: && modelData !== null)? \? (?:root\.controlButtonHover|"#743541") : ', '',s)
p.write_text(s)
p=base/'ControlTile.qml';s=p.read_text().replace('(mouse.containsMouse ? "#252a32" : "#1b1d26")','"#1b1d26"').replace('!quiet && (selected || mouse.containsMouse)', '(mouse.containsMouse || (!quiet && selected))');p.write_text(s)
p=base/'RadioIconButton.qml';s=p.read_text().replace('mouse.containsMouse ? 1.9 : 1.6','1.6').replace('border.width: activeFocus ? 1 : 0','border.width: activeFocus || mouse.containsMouse ? 1 : 0').replace('border.color: Appearance.iconColor','border.color: activeFocus ? Appearance.iconColor : "#9da8c2"').replace('button.powered || mouse.containsMouse ? 1 : .55','button.powered ? 1 : .55');p.write_text(s)
p=base/'BounceMouseArea.qml';s=p.read_text().replace('property bool keyboardActivationPending: false','''property bool keyboardActivationPending: false
    // Shared pointer feedback for every menu action; keyboard focus stays cyan.
    hoverEnabled: true''').replace('border.color: "#55e6ff"','border.color: bounceMouse.activeFocus || bounceMouse.keyboardActivationPending ? "#55e6ff" : "#9da8c2"').replace('visible: bounceMouse.activeFocus || bounceMouse.keyboardActivationPending','visible: bounceMouse.enabled && (bounceMouse.containsMouse || bounceMouse.activeFocus || bounceMouse.keyboardActivationPending)');p.write_text(s)
p=base/'PersonalizationPanel.qml';s=p.read_text().replace('border.color: "#939bb4"','border.color: "#9da8c2"');p.write_text(s)
p=Path('scripts/physical-pilot/deploy-controls-followup-20261020.py');s=p.read_text().replace("'quickshell/apx/ControlTile.qml',", "'quickshell/apx/ControlTile.qml', 'quickshell/apx/BounceMouseArea.qml', 'quickshell/apx/PersonalizationPanel.qml',");p.write_text(s)
