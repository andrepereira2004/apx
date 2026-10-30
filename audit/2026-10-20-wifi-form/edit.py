from pathlib import Path
p=Path('config/environment-shell-v1/quickshell/apx/shell.qml');s=p.read_text().replace('    property bool wifiPasswordVisible: false','    property bool wifiShowPassword: false\n    property bool wifiPasswordVisible: false',1)
s=s.replace('    function beginWifiConnect(name) {\n', '    function beginWifiConnect(name) {\n        wifiShowPassword = false\n',1).replace('    function cancelWifiPassword() {\n','    function cancelWifiPassword() {\n        wifiShowPassword = false\n        wifiMessage = ""\n',1)
# A dedicated form persists until Back/Cancel; background taps no longer erase input.
a=s.index('            TapHandler {\n                acceptedButtons: Qt.LeftButton',s.index('id: popupBackground'));b=s.index('            Flickable {\n                id: menuFlick',a);s=s[:a]+s[b:]
s=s.replace('MenuButton { outlined: true; iconName: "chevron-left"; label: "Voltar às ligações"; onActivated: root.openControlSection("wifi") }', 'MenuButton { outlined: true; iconName: "chevron-left"; label: root.wifiPasswordVisible ? "Escolher outra rede" : "Voltar às ligações"; enabled: !wifiCredentialProcess.running && !hostActionProcess.running; onActivated: { if (root.wifiPasswordVisible) root.cancelWifiPassword(); else root.openControlSection("wifi") } }',1)
a=s.index('                        Rectangle {\n                            width: parent.width; height: 56;',s.index('                        Text { text: "Wi-Fi";'));s=s[:a]+s[a:].replace('                        Rectangle {\n                            width:', '                        Rectangle {\n                            visible: !root.wifiPasswordVisible\n                            width:',1)
s=s.replace('visible: root.wifiDisplayPowered() && !!root.hostState.network_name && ["portal"','visible: !root.wifiPasswordVisible && root.wifiDisplayPowered() && !!root.hostState.network_name && ["portal"',1).replace('visible: root.wifiDisplayPowered()\n                            text: "Outras redes"','visible: root.wifiDisplayPowered() && !root.wifiPasswordVisible\n                            text: "Outras redes"',1)
a=s.index('                            id: wifiPasswordCard');b=s.index('                        Text { visible: root.wifiMessage',a);part=s[a:b]
part=part.replace('wifiCredentialFields.implicitHeight + 16','wifiCredentialFields.implicitHeight + 24').replace('radius: 11','radius: 14',1).replace('border.color: root.cyan','border.color: root.controlButtonOutline',1).replace('x: 8; y: 8; width: parent.width - 16; spacing: 5','x: 12; y: 12; width: parent.width - 24; spacing: 10',1)
old='                                Text { text: root.wifiSelectedSsid; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.Normal; elide: Text.ElideRight; width: parent.width }'
part=part.replace(old,'''                                Row {
                                    width: parent.width; spacing: 10; height: 40
                                    Rectangle {
                                        width: 36; height: 36; radius: 18; color: root.controlButtonActive
                                        anchors.verticalCenter: parent.verticalCenter
                                        LucideIcon { anchors.centerIn: parent; name: "wifi"; width: 18; height: 18 }
                                    }
                                    Column {
                                        width: parent.width - 46; anchors.verticalCenter: parent.verticalCenter; spacing: 3
                                        Text { text: root.wifiSelectedSsid; width: parent.width; elide: Text.ElideRight; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.DemiBold }
                                        Text { text: root.wifiIsKnown(root.wifiSelectedSsid) ? "Rede guardada" : (root.wifiIsOpen(root.wifiSelectedSsid) ? "Rede aberta" : (root.wifiIsEnterprise(root.wifiSelectedSsid) ? "Rede da organização" : "Rede protegida")); color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                    }
                                }
                                Text {
                                    visible: root.wifiIsKnown(root.wifiSelectedSsid) || root.wifiIsOpen(root.wifiSelectedSsid)
                                    width: parent.width; wrapMode: Text.Wrap
                                    text: root.wifiIsKnown(root.wifiSelectedSsid) ? "As credenciais guardadas serão usadas para ligar." : "Esta rede não pede palavra-passe."
                                    color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                                }''',1)
# Responsive enterprise methods, previously wider than the popup.
part=part.replace('                                    spacing: 8\n                                    MenuButton { width: 86; height: 27;', '                                    width: parent.width; spacing: 6\n                                    MenuButton { width: (parent.width - 12) / 3; height: 32;',1).replace('MenuButton { width: 100; height: 27;','MenuButton { width: (parent.width - 12) / 3; height: 32;',1).replace('MenuButton { width: 98; height: 27;','MenuButton { width: (parent.width - 12) / 3; height: 32;',1)
for field,label in [('Username','Utilizador'),('Password','Palavra-passe'),('Domain','Domínio do servidor'),('Ca','Certificado CA')]:
    marker='                                    TextInput {\n                                        id: wifi'+field+'Input'
    pos=part.index(marker);begin=part.rfind('                                Rectangle {',0,pos)
    # The label stays visible when text is entered; no placeholder-only labels.
    part=part[:begin]+'''                                Text { visible: wifiFIELDField.visible; text: "LABEL"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
'''.replace('FIELD',field).replace('LABEL',label)+part[begin:]
    pos=part.index(marker);begin=part.rfind('                                Rectangle {',0,pos)
    part=part[:begin]+part[begin:].replace('                                Rectangle {','                                Rectangle {\n                                    id: wifi'+field+'Field',1)
part=part.replace('height: visible ? 28 : 0; radius: 5','height: visible ? 40 : 0; radius: 9').replace('height: visible ? 30 : 0; radius: 5','height: visible ? 40 : 0; radius: 9').replace('color: root.controlButtonSurface\n                                    border.width:', 'color: root.controlButtonActive\n                                    enabled: !wifiCredentialProcess.running && !hostActionProcess.running\n                                    border.width:').replace('radius: 9; color: root.controlButtonSurface; border.width:','radius: 9; color: root.controlButtonActive; enabled: !wifiCredentialProcess.running && !hostActionProcess.running; border.width:')
part=part.replace('border.color: root.cyan','border.color: root.textMain')
part=part.replace('anchors.rightMargin: 9; verticalAlignment: TextInput.AlignVCenter\n                                        activeFocusOnTab:', 'anchors.rightMargin: 80; verticalAlignment: TextInput.AlignVCenter\n                                        activeFocusOnTab:',1).replace('echoMode: TextInput.Password;', 'echoMode: root.wifiShowPassword ? TextInput.Normal : TextInput.Password;',1)
# Give all fields meaningful accessible names, retaining their native editing/tab handling.
for field,label in [('Username','Utilizador'),('Password','Palavra-passe'),('Domain','Domínio do servidor'),('Ca','Certificado CA')]:
    part=part.replace('id: wifi'+field+'Input', 'id: wifi'+field+'Input\n                                        Accessible.name: "'+label+'"',1) if field!='Password' else part.replace('id: wifiPasswordInput; anchors.fill:', 'id: wifiPasswordInput; Accessible.name: "Palavra-passe"; anchors.fill:',1)
# Simple text toggle uses existing controls, with enough space reserved in the input.
pos=part.index('                                    Text { anchors.left:',part.index('id: wifiPasswordField'))
part=part[:pos]+'''                                    MenuButton {
                                        anchors.right: parent.right; anchors.rightMargin: 5; anchors.verticalCenter: parent.verticalCenter
                                        width: 70; height: 30; label: root.wifiShowPassword ? "Ocultar" : "Mostrar"
                                        onActivated: { root.wifiShowPassword = !root.wifiShowPassword; wifiPasswordInput.forceActiveFocus() }
                                    }
'''+part[pos:]
# Replace the tiny text actions with stable, keyboard-accessible full-size buttons.
actions=part.index('                                Row {\n                                    spacing: 14')
part=part[:actions]+'''                                Text {
                                    visible: root.wifiMessage.length > 0; width: parent.width; wrapMode: Text.Wrap
                                    text: root.wifiMessage; color: root.wifiMessage.indexOf("A ligar") === 0 ? root.textDim : "#ffb0bd"
                                    font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                                }
                                Row {
                                    width: parent.width; spacing: 8
                                    MenuButton {
                                        width: (parent.width - 8) / 2; height: 38; label: "Cancelar"
                                        enabled: !wifiCredentialProcess.running && !hostActionProcess.running
                                        onActivated: root.cancelWifiPassword()
                                    }
                                    MenuButton {
                                        width: (parent.width - 8) / 2; height: 38; accent: true
                                        label: (wifiCredentialProcess.running || hostActionProcess.running) ? "A ligar…" : "Ligar"
                                        enabled: !wifiCredentialProcess.running && !hostActionProcess.running && root.wifiSelectedSsid !== root.hostState.network_name
                                        onActivated: root.submitWifiPassword()
                                    }
                                }
                            }
                        }
'''
s=s[:a]+part+s[b:]
s=s.replace('Text { visible: root.wifiMessage.length > 0; width:', 'Text { visible: !root.wifiPasswordVisible && root.wifiMessage.length > 0; width:',1)
s=s.replace('model: root.wifiDisplayPowered() ? Array.from(new Set(root.hostState.available_networks || [])) : []','model: root.wifiDisplayPowered() && !root.wifiPasswordVisible ? Array.from(new Set(root.hostState.available_networks || [])) : []',1)
s=s.replace('visible: root.wifiDisplayPowered() && !(root.hostState.available_networks || []).length','visible: root.wifiDisplayPowered() && !root.wifiPasswordVisible && !(root.hostState.available_networks || []).length',1)
s=s.replace('        onStarted: {\n            write(root.wifiIsEnterprise', '        onStarted: {\n            root.wifiShowPassword = false\n            write(root.wifiIsEnterprise',1)
# Same quiet icon semantics for airplane mode; dimmed icon is its off state.
s=s.replace('caption: "Modo de avião  ·  " + (root.airplaneMode ? "Ligado" : "Desligado"); selected: root.airplaneMode; enabled: !DesktopActivity.busy; onActivated: DesktopActivity.action(["airplane", root.airplaneMode ? "off" : "on"])', 'caption: "Modo de avião"; quiet: true; selected: root.airplaneMode; iconActionEnabled: true; iconActionAvailable: !DesktopActivity.busy; iconActionLabel: root.airplaneMode ? "Desativar modo de avião" : "Ativar modo de avião"; onIconActivated: DesktopActivity.action(["airplane", root.airplaneMode ? "off" : "on"]); onActivated: DesktopActivity.action(["airplane", root.airplaneMode ? "off" : "on"])',1)
p.write_text(s)
