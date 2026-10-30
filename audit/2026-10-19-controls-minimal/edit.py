from pathlib import Path
p=Path('config/environment-shell-v1/quickshell/apx/shell.qml');s=p.read_text()
for flag,route,title,back in [('controlsBluetoothOpen','bluetooth','Bluetooth','Voltar às ligações'),('controlsAudioOpen','audio','Som','Voltar a som e brilho'),('controlsMicrophoneOpen','microphone','Microfone','Voltar a som e brilho')]:
 a=s.index('                    Rectangle {\n                        visible: root.renderedControls.'+flag); b=s.index('\n                    '+('Flickable' if route=='bluetooth' else 'Column')+' {',a)
 s=s[:a]+f'''                    Column {{
                        visible: root.renderedControls.{flag}
                        width: parent.width; spacing: 8
                        MenuButton {{ outlined: true; iconName: "chevron-left"; label: "{back}"; onActivated: root.openControlSection("{route}") }}
                        Text {{ text: "{title}"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold }}
                    }}'''+s[b:]
# Keep one scroll surface for Bluetooth rather than a small nested list.
s=s.replace('width: parent.width; height: visible ? 216 : 0','width: parent.width; height: visible ? bluetoothContent.implicitHeight : 0')
s=s.replace('width: parent.width - (implicitHeight > 216 ? 7 : 0); spacing: 5','width: parent.width; spacing: 8')
a=s.index('                            Rectangle {',s.index('id: bluetoothContent')); b=s.index('                            Rectangle {\n                                visible: root.bluetoothDisplayPowered()',a)
s=s[:a]+'''                            ControlTile {
                                width: parent.width; height: 56; radius: 14; showCaption: true
                                iconName: root.bluetoothDisplayPowered() ? "bluetooth" : "bluetooth-off"
                                caption: root.bluetoothPowerPhase === "turning-on" ? "A ligar…" : (root.bluetoothDisplayPowered() ? "Desligar Bluetooth" : "Ligar Bluetooth")
                                enabled: !root.bluetoothPowerPhase.length
                                onActivated: root.toggleBluetoothPower()
                            }

'''+s[b:]
for func,label in [('Connected','Ligados'),('Known','Guardados'),('Available','Disponíveis')]:
 old='Item { width: parent.width; height: 18; Text { anchors.verticalCenter: parent.verticalCenter; text: "Dispositivos '+{'Connected':'ligados','Known':'anteriores','Available':'disponíveis'}[func]+'  ·  " + root.bluetooth'+func+'Devices().length;'
 new='Item { visible: root.bluetoothDisplayPowered() && root.bluetooth'+func+'Devices().length > 0; width: parent.width; height: visible ? 18 : 0; Text { anchors.verticalCenter: parent.verticalCenter; text: "'+label+'";'
 assert old in s;s=s.replace(old,new)
for f,t in [('Connected','ligado'),('Known','anterior')]:
 import re
 s=re.sub(r'                            Text \{ visible: root.bluetooth'+f+r'Devices\(\).length === 0;[^\n]+\n','',s)
s=s.replace('"-- a procurar dispositivos --" : "-- nenhum dispositivo disponível --"','"A procurar…" : "Nenhum dispositivo encontrado"').replace('"-- liga o Bluetooth para procurar dispositivos --"','"Liga o Bluetooth para procurar"')
# Remove duplicate fine-adjustment buttons; sliders retain keyboard adjustment.
a=s.index('                    Column {\n                        width: parent.width; spacing: 5; visible: root.renderedControls.controlsAudioOpen');b=s.index('\n\n                    Column {\n                        visible: root.renderedControls.controlsMicrophoneOpen',a)
part=s[a:b];start=part.index('                        Row {\n                            width: parent.width; height: 30; spacing: 4');end=part.index('                        Rectangle {',start);part=part[:start]+part[end:];s=s[:a]+part+s[b:]
a=s.index('                    Column {\n                        width: parent.width; spacing: 5; visible: root.renderedControls.controlsMicrophoneOpen');b=s.index('                        Row {\n                            width: parent.width; height: 30; spacing: 4',a);end=s.index('                        Rectangle {',b);s=s[:b]+s[end:]
# Softer matching surfaces for the affected pages.
a=s.index('                    Column {\n                        visible: root.renderedControls.controlsBluetoothOpen');b=s.index('                    Column {',s.index('id: microphoneMuteMouse',a)) if False else s.index('                    Column {\n',s.index('id: microphoneMuteMouse',a))
part=s[a:b].replace('radius: 11','radius: 14').replace('border.width: 1; border.color: root.controlButtonOutline','border.width: 0; border.color: root.controlButtonOutline')
s=s[:a]+part+s[b:]
p.write_text(s)
# Personalization: three focused sections instead of all controls at once.
p=Path('config/environment-shell-v1/quickshell/apx/PersonalizationPanel.qml');s=p.read_text().replace('    property string scope:', '    property string section: ""\n    property string scope:')
s=s.replace('        radius: 7','        radius: 14').replace('        implicitHeight: 36','        implicitHeight: 44')
s=s.replace('IconLabel { anchors.centerIn: parent;', 'IconLabel { anchors.left: parent.left; anchors.leftMargin: 14; anchors.verticalCenter: parent.verticalCenter;')
a=s.index('    Action { text: "Voltar às opções"');b=s.index('    Caption { text: "Cor dos ícones"',a)
s=s[:a]+'''    Action { text: panel.section.length ? "Voltar à personalização" : "Voltar às opções"; iconName: "chevron-left"; onClicked: { if (panel.section.length) panel.section = ""; else panel.back() } }
    Column {
        width: parent.width; spacing: 8; visible: !panel.section.length
        Action { text: "Cor dos ícones"; iconName: "palette"; onClicked: panel.section = "color" }
        Action { text: "Transparência"; iconName: "blend"; onClicked: panel.section = "opacity" }
        Action { text: "Fundo do ecrã"; iconName: "image"; onClicked: panel.section = "wallpaper" }
    }
    Column {
        width: parent.width; spacing: 8; visible: panel.section === "color"
'''+s[b:]
a=s.index('    Rectangle { width: parent.width; height: 1; color: "#414654" }');s=s[:a]+'''    }
    Column {
        width: parent.width; spacing: 8; visible: panel.section === "opacity"
'''+s[a:];a=s.index('    Rectangle { width: parent.width; height: 1; color: "#414654" }',a+100);s=s[:a]+'''    }
    Column {
        width: parent.width; spacing: 8; visible: panel.section === "wallpaper"
'''+s[a:];a=s.index('    Caption { visible: Appearance.error');s=s[:a]+'    }\n'+s[a:]
s=s.replace('    Rectangle { width: parent.width; height: 1; color: "#414654" }\n','').replace('Opacidade deste Environment','Transparência').replace('Wallpaper deste Environment','Fundo do ecrã').replace('label: "Rofi"','label: "Aplicações"').replace('label: "Menus APX"','label: "Menus"')
s=s.replace('    Caption {\n        text: panel.scope', '    Caption {\n        visible: false\n        text: panel.scope')
s=s.replace('text: "0% transparente · 100% opaco. O gestor de ficheiros pode precisar de ser reaberto."','text: "O gestor de ficheiros pode precisar de ser reaberto."')
p.write_text(s)
