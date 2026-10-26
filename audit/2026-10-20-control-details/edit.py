from pathlib import Path
root=Path(__file__).resolve().parents[2]
p=root/'config/environment-shell-v1/quickshell/apx/shell.qml'
s=p.read_text()
s=s.replace('onActivated: DesktopActivity.action(["airplane", root.airplaneMode ? "off" : "on"]) }','onActivated: root.openActivitySection("airplane") }')
s=s.replace('onIconActivated: root.cycleKeyboardBrightness(); onActivated: root.cycleKeyboardBrightness()', 'onIconActivated: root.cycleKeyboardBrightness(); onActivated: root.openActivitySection("keyboard")')
s=s.replace('visible: root.renderedControls.controlsActivityKind.length > 0','visible: root.renderedControls.controlsActivityKind.length > 0 && ["airplane", "keyboard"].indexOf(root.renderedControls.controlsActivityKind) < 0')
marker='                    ActivityPanel {\n                        width: parent.width\n                        visible: root.renderedControls.controlsActivityKind.length'
pos=s.index(marker)
s=s[:pos]+'''                    Column {
                        width: parent.width; spacing: 8
                        visible: root.renderedControls.controlsActivityKind === "airplane"
                        MenuButton { outlined: true; iconName: "chevron-left"; label: "Voltar às ligações"; onActivated: root.openControlSection("connectivity") }
                        Text { text: "Modo de avião"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold }
                        ControlTile { width: parent.width; height: 56; quiet: true; showCaption: true; iconName: "plane"; caption: root.airplaneMode ? "Ativado" : "Desativado"; selected: root.airplaneMode; iconActionEnabled: true; iconActionAvailable: !DesktopActivity.busy; iconActionLabel: "Alterar modo de avião"; onIconActivated: DesktopActivity.action(["airplane", root.airplaneMode ? "off" : "on"]); onActivated: DesktopActivity.action(["airplane", root.airplaneMode ? "off" : "on"]) }
                        Text { width: parent.width; wrapMode: Text.WordWrap; text: "Ao ativar, são bloqueadas as comunicações sem fios de Wi-Fi e Bluetooth:"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        Text { width: parent.width; wrapMode: Text.WordWrap; text: "Wi-Fi · ligação à rede e pesquisa de redes.\\nBluetooth · ligações a dispositivos e pesquisa de dispositivos."; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        Text { text: "Wi-Fi: " + (root.wifiDisplayPowered() ? "Ativado" : "Desativado"); color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                        Text { text: "Bluetooth: " + (root.bluetoothDisplayPowered() ? "Ativado" : "Desativado"); color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                    }
                    Column {
                        width: parent.width; spacing: 8
                        visible: root.renderedControls.controlsActivityKind === "keyboard"
                        MenuButton { outlined: true; iconName: "chevron-left"; label: "Voltar ao som e brilho"; onActivated: root.openControlSection("brightness") }
                        Text { text: "Iluminação do teclado"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold }
                        ControlTile { width: parent.width; height: 56; quiet: true; showCaption: true; iconName: "keyboard"; caption: "Intensidade: " + root.keyboardBrightness + " / " + root.keyboardBrightnessMax + " · " + (root.keyboardBrightnessMax > 0 ? Math.round(root.keyboardBrightness * 100 / root.keyboardBrightnessMax) : 0) + "%"; selected: root.keyboardBrightness > 0; iconActionEnabled: true; iconActionAvailable: !keyboardBrightnessProcess.running; iconActionLabel: "Alterar iluminação do teclado"; onIconActivated: root.cycleKeyboardBrightness(); onActivated: root.cycleKeyboardBrightness() }
                    }
'''+s[pos:]
s=s.replace('MenuButton { height: 44; radius: 14; alignedIcon: true; outlined: true; iconName: "chevron-left"; label: "Voltar aos controlos";', 'MenuButton { outlined: true; iconName: "chevron-left"; label: "Voltar aos controlos";')
for kind in ['mouse','trackpad']:
 start=s.index('                        BounceMouseArea {',s.index('id: '+kind+'SensitivityCard'))
 end=s.index('                        RadioIconButton {',start)
 s=s[:start]+s[end:]
 s=s.replace('iconName: "'+('mouse' if kind=='mouse' else 'touchpad')+'"; powered: root.pointerDevices.'+kind+'.enabled','cardHoverEnabled: false\n                            iconName: '+ ('"mouse"' if kind=='mouse' else '(root.pointerDevices.trackpad.available && root.pointerDevices.trackpad.enabled ? "touchpad" : "touchpad-off")')+'; powered: root.pointerDevices.'+kind+'.available && root.pointerDevices.'+kind+'.enabled')
s=s.replace('                    Text { visible: root.pointerPowerError.length > 0; width: parent.width; text: root.pointerPowerError; color: "#ff91a4"; wrapMode: Text.WordWrap; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }\n','')
p.write_text(s)
p=root/'config/environment-shell-v1/quickshell/apx/RadioIconButton.qml';s=p.read_text().replace('property bool busy: false','property bool busy: false\n    property bool cardHoverEnabled: true').replace('enabled: button.enabled && !button.parent.children.some','enabled: button.cardHoverEnabled && button.enabled && !button.parent.children.some');p.write_text(s)
