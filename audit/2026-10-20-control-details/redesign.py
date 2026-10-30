from pathlib import Path
repo=Path(__file__).resolve().parents[2]
p=repo/'config/environment-shell-v1/quickshell/apx/shell.qml';s=p.read_text()
s=s.replace('function openBrightnessControls(): void {', 'function openAirplaneControls(): void { openControls(); root.openActivitySection("airplane") }\n        function openBrightnessControls(): void {',1)
a=s.index('                        Text { text: "Modo de avião";',s.index('visible: root.renderedControls.controlsActivityKind === "airplane"'))
b=s.index('\n                    }\n                    Column {',a)
s=s[:a]+'''                        Rectangle {
                            width: parent.width; height: 72; radius: 14
                            color: root.controlButtonSurface
                            RadioIconButton {
                                x: 8; anchors.verticalCenter: parent.verticalCenter
                                iconName: "plane"; powered: root.airplaneMode
                                busy: DesktopActivity.busy
                                actionLabel: root.airplaneMode ? "Desativar modo de avião" : "Ativar modo de avião"
                                onActivated: DesktopActivity.action(["airplane", root.airplaneMode ? "off" : "on"])
                            }
                            Column {
                                anchors.left: parent.left; anchors.leftMargin: 54
                                anchors.right: parent.right; anchors.rightMargin: 12
                                anchors.verticalCenter: parent.verticalCenter; spacing: 4
                                Text { text: "Modo de avião"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.DemiBold }
                                Text { text: DesktopActivity.busy ? "A alterar…" : root.airplaneMode ? "Ativado" : "Desativado"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            }
                        }
                        Text { text: "Comunicações afetadas"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                        Repeater {
                            model: [
                                {name: "Wi-Fi", icon: root.wifiDisplayPowered() ? "wifi" : "wifi-off", powered: root.wifiDisplayPowered(), detail: "Internet e pesquisa de redes"},
                                {name: "Bluetooth", icon: root.bluetoothDisplayPowered() ? "bluetooth" : "bluetooth-off", powered: root.bluetoothDisplayPowered(), detail: "Ligações e pesquisa de dispositivos"}
                            ]
                            Rectangle {
                                required property var modelData
                                width: parent.width; height: 72; radius: 14
                                color: root.controlButtonSurface
                                Rectangle {
                                    x: 8; anchors.verticalCenter: parent.verticalCenter
                                    width: 36; height: 36; radius: 18
                                    color: Qt.lighter(root.controlButtonSurface, 1.6)
                                    LucideIcon { anchors.centerIn: parent; width: 16; height: 16; name: modelData.icon; opacity: modelData.powered ? 1 : .55 }
                                }
                                Text {
                                    id: airplaneServiceState
                                    anchors.right: parent.right; anchors.rightMargin: 12; y: 14
                                    text: modelData.powered ? "Ligado" : "Desligado"
                                    color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                                }
                                Text {
                                    anchors.left: parent.left; anchors.leftMargin: 54
                                    anchors.right: airplaneServiceState.left; anchors.rightMargin: 8; y: 12
                                    text: modelData.name; elide: Text.ElideRight
                                    color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                }
                                Text {
                                    anchors.left: parent.left; anchors.leftMargin: 54
                                    anchors.right: parent.right; anchors.rightMargin: 12; y: 38
                                    text: modelData.detail; wrapMode: Text.WordWrap
                                    color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize
                                }
                            }
                        }
                        Text {
                            width: parent.width; wrapMode: Text.WordWrap
                            text: root.airplaneMode ? "Wi-Fi e Bluetooth bloqueados pelo modo de avião." : "Ao ativar, o Wi-Fi e o Bluetooth serão desativados."
                            color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                        }'''+s[b:]
p.write_text(s)
