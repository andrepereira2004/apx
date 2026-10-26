from pathlib import Path
repo=Path(__file__).resolve().parents[2];p=repo/'config/environment-shell-v1/quickshell/apx/shell.qml';s=p.read_text()
a=s.index('                    Rectangle {',s.index('visible: root.popupKind === "battery"',s.index('id: mediaMenu')));b=s.index('                    Text {\n                        visible: root.hardwareStatusError',a)
s=s[:a]+'''                    Rectangle {
                        width: parent.width; height: 130; radius: 14; color: root.controlButtonSurface
                        Rectangle {
                            x: 8; y: 18; width: 36; height: 36; radius: 18
                            color: Qt.lighter(root.controlButtonSurface, 1.6)
                            LucideIcon { anchors.centerIn: parent; width: 16; height: 16; name: root.batteryIconName }
                        }
                        Text { id: batteryCapacity; x: 54; y: 10; text: root.batteryText; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: 28; font.weight: Font.DemiBold }
                        Text {
                            x: 54; y: 45; width: parent.width - 68
                            text: root.batteryStatus; elide: Text.ElideRight
                            color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                        }
                        Rectangle {
                            x: 14; y: 77; width: parent.width - 28; height: 6; radius: 3; color: root.controlButtonOutline
                            Rectangle { height: parent.height; radius: 3; color: parseInt(root.batteryText) <= 20 ? "#ffb15a" : "#9dc8bd"; width: parent.width * Math.max(0, Math.min(100, parseInt(root.batteryText) || 0)) / 100 }
                        }
                        LucideIcon { x: 14; y: 99; width: 16; height: 16; name: "battery"; tint: root.textDim }
                        Text {
                            x: 38; y: 99; width: parent.width - 52; elide: Text.ElideRight
                            text: root.batteryMinutes >= 0 ? "Restam cerca de " + Math.floor(root.batteryMinutes / 60) + " h " + (root.batteryMinutes % 60) + " min" : root.batteryDischarging ? "Autonomia indisponível" : root.batteryStatus === "A carregar" ? "Ligada à corrente · a carregar" : root.batteryStatus === "Carga completa" ? "Bateria carregada" : root.batteryStatus
                            color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                        }
                    }
'''+s[b:]
a=s.index('                    Row {\n                        id: energyModeRow');b=s.index('                    Text {\n                        visible: root.hardwareMessage',a)
s=s[:a]+'''                    Text { text: "Modo de energia"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                    Column {
                        id: energyModeRow
                        width: parent.width; spacing: 8
                        Repeater {
                            model: [
                                { profile: "low-power", label: "Poupar energia", icon: "battery-low" },
                                { profile: "balanced", label: "Equilibrado", icon: "cpu" },
                                { profile: "performance", label: "Desempenho", icon: "zap" }
                            ]
                            MenuButton {
                                required property var modelData
                                width: energyModeRow.width; height: 56; radius: 14; alignedIcon: true
                                label: modelData.label; iconName: modelData.icon
                                accent: root.hardwareProfile.platform_profile === modelData.profile
                                selected: accent
                                enabled: !root.hardwareBusy && (root.hardwareProfile.platform_profiles || []).indexOf(modelData.profile) >= 0
                                onActivated: root.setPlatformProfile(modelData.profile)
                            }
                        }
                    }
'''+s[b:]
s=s.replace('label: root.batteryDetailsOpen ? "− Ocultar detalhes" : "+ Detalhes e gráficos"\n                        height: 36','label: root.batteryDetailsOpen ? "Ocultar detalhes" : "Detalhes e gráficos"\n                        iconName: "list"; alignedIcon: true; radius: 14\n                        height: 56',1)
s=s.replace('{ title: "Potência", value:', '{ title: "Potência", icon: "zap", value:',1).replace('{ title: "Saúde da bateria", value:', '{ title: "Saúde", icon: "shield-check", value:',1)
old='''                                    width: (parent.width - 8) / 2; height: 48; radius: 9; color: root.controlButtonSurface
                                    Text { x: 10; y: 7; text: modelData.title; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: Appearance.metaSize }
                                    Text { x: 10; y: 24; text: modelData.value; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: 14 }'''
new='''                                    width: (parent.width - 8) / 2; height: 72; radius: 14; color: root.controlButtonSurface
                                    LucideIcon { x: 12; anchors.verticalCenter: parent.verticalCenter; width: 16; height: 16; name: modelData.icon }
                                    Text { x: 40; y: 14; width: parent.width - 50; text: modelData.title; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                                    Text { x: 40; y: 36; width: parent.width - 50; text: modelData.value; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }'''
assert old in s;s=s.replace(old,new,1)
s=s.replace('height: 40; label: "Híbridos · NVIDIA sob pedido"','height: 56; radius: 14; alignedIcon: true; iconName: "cpu"; label: "Híbridos · NVIDIA sob pedido"',1).replace('height: 40; label: "NVIDIA dedicada · maior consumo"','height: 56; radius: 14; alignedIcon: true; iconName: "monitor"; label: "NVIDIA dedicada · maior consumo"',1)
s=s.replace('label: root.hardwareApplied ? "Mais tarde" : "Cancelar"','iconName: root.hardwareApplied ? "rotate-cw" : "x"\n                                        label: root.hardwareApplied ? "Mais tarde" : "Cancelar"',1).replace('label: root.hardwareApplied ? "Reiniciar agora" : (root.hardwareBusy ? "A processar..." : "Confirmar")','iconName: root.hardwareApplied ? "rotate-cw" : "check"\n                                        label: root.hardwareApplied ? "Reiniciar agora" : (root.hardwareBusy ? "A processar..." : "Confirmar")',1)
# Preserve the Hub card as-is; add a workload-only alternative.
s=s.replace('id: hubEnvironmentCard\n                        property bool', 'id: hubEnvironmentCard\n                        visible: root.isHub\n                        property bool',1)
a=s.index('\n                    Column {',s.index('id: hubEnvironmentCard'))
s=s[:a]+'''
                    Rectangle {
                        visible: !root.isHub
                        width: parent.width; height: 80; radius: 14; color: root.controlButtonSurface
                        Rectangle {
                            x: 8; anchors.verticalCenter: parent.verticalCenter
                            width: 36; height: 36; radius: 18; color: Qt.lighter(root.controlButtonSurface, 1.6)
                            LucideIcon { anchors.centerIn: parent; width: 16; height: 16; name: "box" }
                        }
                        Column {
                            anchors.left: parent.left; anchors.leftMargin: 54
                            anchors.right: parent.right; anchors.rightMargin: 14
                            anchors.verticalCenter: parent.verticalCenter; spacing: 5
                            Text { width: parent.width; text: root.environmentLabel; elide: Text.ElideRight; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.DemiBold }
                            Row {
                                spacing: 6
                                LucideIcon { width: 14; height: 14; name: "check"; tint: root.textDim }
                                Text { text: "Environment ativo"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            }
                        }
                    }
'''+s[a:]
s=s.replace('height: visible ? 46 : 0; label: root.environmentSwitchPending', 'height: visible ? 56 : 0; radius: 14; alignedIcon: true; iconName: "log-out"; label: root.environmentSwitchPending',1)
s=s.replace('Text { visible: !root.isHub; width: parent.width; horizontalAlignment: Text.AlignHCenter; text: "O Environment será fechado em segurança antes da troca.";', 'Text { visible: !root.isHub; width: parent.width; wrapMode: Text.WordWrap; text: "Regressa ao Hub para escolher outro Environment. Este será fechado em segurança.";',1)
p.write_text(s)
