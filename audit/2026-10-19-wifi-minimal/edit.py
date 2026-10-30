from pathlib import Path
p=Path('config/environment-shell-v1/quickshell/apx/shell.qml')
s=p.read_text(); a=s.index('                    Rectangle {\n                        visible: root.renderedControls.controlsWifiOpen'); b=s.index('                        Rectangle {\n                            id: wifiPasswordCard',a)
s=s[:a]+'''                    Column {
                        width: parent.width; spacing: 8
                        visible: root.renderedControls.controlsWifiOpen
                        MenuButton { outlined: true; iconName: "chevron-left"; label: "Voltar às ligações"; onActivated: root.openControlSection("wifi") }
                        Text { text: "Wi-Fi"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold }
                        Rectangle {
                            width: parent.width; height: 56; radius: 14
                            color: root.controlButtonSurface
                            LucideIcon {
                                name: root.wifiDisplayActive() ? "wifi" : "wifi-off"
                                width: 20; height: 20
                                anchors.left: parent.left; anchors.leftMargin: 14; anchors.verticalCenter: parent.verticalCenter
                            }
                            Column {
                                anchors.left: parent.left; anchors.leftMargin: 46; anchors.right: disconnectButton.left; anchors.rightMargin: 10
                                anchors.verticalCenter: parent.verticalCenter; spacing: 3
                                Text {
                                    width: parent.width; elide: Text.ElideRight
                                    text: root.wifiDisplayActive() ? root.hostState.network_name : (root.wifiTogglePhase === "connecting" ? "A ligar…" : "Sem ligação")
                                    color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                }
                                Text {
                                    visible: root.wifiDisplayActive()
                                    text: "Ligado"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize
                                }
                            }
                            MenuButton {
                                id: disconnectButton
                                visible: root.wifiDisplayActive() && root.wifiTogglePhase !== "connecting"
                                anchors.right: parent.right; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter
                                width: visible ? 84 : 0; height: 32
                                label: "Desligar"
                                onActivated: { root.cancelWifiPassword(); root.toggleWifiConnection() }
                            }
                        }
                        Row {
                            visible: !!root.hostState.network_name && ["portal", "limited", "none"].indexOf(root.hostState.network_connectivity) >= 0
                            width: parent.width; height: visible ? 32 : 0; spacing: 8
                            Text {
                                anchors.verticalCenter: parent.verticalCenter
                                text: root.hostState.network_connectivity === "portal" ? "Iniciar sessão na rede" : "Sem acesso à Internet"
                                color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                            }
                            MenuButton { visible: root.hostState.network_connectivity === "portal"; height: 32; width: 112; label: "Abrir acesso"; onActivated: if (!wifiPortalProcess.running) wifiPortalProcess.running = true }
                        }
                        Text {
                            text: "Outras redes"; color: root.textDim
                            font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                        }
'''+s[b:]
a=s.index('                                Text {\n                                    anchors.left: parent.left; anchors.leftMargin: 12; anchors.top: parent.top;',a); b=s.index('                                BounceMouseArea {',a)
s=s[:a]+'''                                LucideIcon {
                                    name: root.wifiDetails(modelData).signal >= 50 ? "wifi" : (root.wifiDetails(modelData).signal >= 25 ? "wifi-high" : "wifi-low")
                                    width: 18; height: 18
                                    anchors.left: parent.left; anchors.leftMargin: 14; anchors.verticalCenter: parent.verticalCenter
                                    opacity: .7
                                }
                                Text {
                                    anchors.left: parent.left; anchors.leftMargin: 46; anchors.verticalCenter: parent.verticalCenter
                                    width: parent.width - 86; elide: Text.ElideRight
                                    text: modelData; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                }
                                LucideIcon {
                                    visible: !root.wifiIsOpen(modelData)
                                    name: "lock-keyhole"; width: 14; height: 14; opacity: .4
                                    anchors.right: parent.right; anchors.rightMargin: 14; anchors.verticalCenter: parent.verticalCenter
                                }
'''+s[b:]
s=s.replace('text: "-- nenhuma rede encontrada --"','text: "Nenhuma rede encontrada"')
p.write_text(s)
