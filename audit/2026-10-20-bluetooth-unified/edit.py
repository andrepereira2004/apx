from pathlib import Path
p=Path('config/environment-shell-v1/quickshell/apx/shell.qml');s=p.read_text()
# Active circle x=8,width=36 => glyph centre x=26. All list glyphs now share it.
needle='name: root.wifiDetails(modelData).signal >= 50 ? "wifi" : (root.wifiDetails(modelData).signal >= 25 ? "wifi-high" : "wifi-low")'
a=s.index(needle);b=s.index('                                LucideIcon {\n                                    visible: !root.wifiIsOpen',a)
part=s[a:b].replace('anchors.leftMargin: 14','anchors.leftMargin: 18',1).replace('anchors.leftMargin: 46','anchors.leftMargin: 54',1).replace('width: parent.width - 86','width: parent.width - 94',1);s=s[:a]+part+s[b:]
s=s.replace('    property string bluetoothPairPin: ""','    property bool bluetoothShowPin: false\n    property string bluetoothPairPin: ""',1)
a=s.index('    function bluetoothConnectedDevices()');b=s.index('    function applyBluetoothPairResult(',a)
s=s[:a]+'''    function bluetoothDevicesUnique() {
        var seen = new Set()
        return (hostState.bluetooth_devices || []).filter(function(device) {
            if (!device || !device.address || seen.has(device.address)) return false
            seen.add(device.address)
            return true
        })
    }
    function bluetoothConnectedDevices() {
        if (!bluetoothDisplayPowered()) return []
        return bluetoothDevicesUnique().filter(function(device) { return device.connected === true })
    }
    function bluetoothKnownDevices() {
        if (!bluetoothDisplayPowered()) return []
        return bluetoothDevicesUnique().filter(function(device) { return device.paired === true && device.connected !== true })
    }
    function bluetoothAvailableDevices() {
        if (!bluetoothDisplayPowered()) return []
        return bluetoothDevicesUnique().filter(function(device) { return device.paired !== true && device.connected !== true })
    }
    function revealBluetoothForm() {
        Qt.callLater(function() {
            menuFlick.stopWheel()
            menuFlick.contentY = 0
            if (root.bluetoothPairPhase === "needs-response" && root.bluetoothPairChallenge === "pin")
                bluetoothPinInput.forceActiveFocus()
        })
    }
''' +s[b:]
s=s.replace('''        if (bluetoothPairPhase === "completed") {''','''        if (bluetoothPairPhase === "needs-response") revealBluetoothForm()
        if (bluetoothPairPhase === "completed") {''',1)
s=s.replace('        bluetoothMessage = "A iniciar o emparelhamento…"','        bluetoothShowPin = false\n        bluetoothMessage = "A iniciar o emparelhamento…"',1).replace('        bluetoothPairBeginProcess.running = true\n','        bluetoothPairBeginProcess.running = true\n        revealBluetoothForm()\n',1)
s=s.replace('    function dismissBluetoothPairing() {\n','    function dismissBluetoothPairing() {\n        bluetoothShowPin = false\n',1).replace('    function cancelBluetoothPairing() {\n','    function cancelBluetoothPairing() {\n        bluetoothShowPin = false\n',1)
s=s.replace('''        bluetoothMessage = ""
    }

    function confirmBluetoothRemove()''','''        bluetoothMessage = ""
        revealBluetoothForm()
    }

    function confirmBluetoothRemove()''',1)
# Close a completed pairing only once current Host state confirms the device is connected.
s=s.replace('                    root.hostState = JSON.parse(text)\n','''                    root.hostState = JSON.parse(text)
                    if (root.bluetoothPairPhase === "completed" && (root.hostState.bluetooth_devices || []).some(function(device) { return device.address === root.bluetoothPairAddress && device.connected === true })) {
                        root.dismissBluetoothPairing()
                        root.bluetoothMessage = ""
                    }
''',1)
# One consistent device-row layout for all Bluetooth groups.
a=s.index('    component MenuButton: Rectangle {')
s=s[:a]+'''    component BluetoothDeviceRow: Rectangle {
        id: deviceRow
        required property var device
        property bool connected: false
        property bool paired: false
        property bool pending: root.bluetoothDevicePendingAddress === device.address
        signal activated()
        signal forgetRequested()
        width: parent ? parent.width : 300; height: connected ? 56 : 44; radius: connected ? 14 : 10
        color: deviceMouse.containsMouse ? root.controlButtonHover : root.controlButtonSurface
        LucideIcon {
            name: "bluetooth"; width: 16; height: 16
            anchors.left: parent.left; anchors.leftMargin: 18; anchors.verticalCenter: parent.verticalCenter
            opacity: deviceRow.connected ? 1 : .65
        }
        Text {
            anchors.left: parent.left; anchors.leftMargin: 54
            anchors.right: deviceActions.left; anchors.rightMargin: 8
            anchors.verticalCenter: parent.verticalCenter; elide: Text.ElideRight
            text: deviceRow.device.name || deviceRow.device.address
            color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
        }
        BounceMouseArea {
            id: deviceMouse
            anchors.fill: parent; anchors.rightMargin: deviceActions.width + 16
            enabled: !deviceRow.connected && !root.bluetoothDevicePendingAddress.length && !bluetoothPairBeginProcess.running && !bluetoothPairRespondProcess.running
            hoverEnabled: true; cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
            onClicked: deviceRow.activated()
        }
        Row {
            id: deviceActions
            anchors.right: parent.right; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter; spacing: 6
            MenuButton {
                width: deviceRow.connected || !deviceRow.paired ? 108 : 68; height: 32
                label: deviceRow.pending ? (deviceRow.connected ? "A desligar…" : "A ligar…") : (deviceRow.connected ? "Desconectar" : (deviceRow.paired ? "Ligar" : "Emparelhar"))
                enabled: !root.bluetoothDevicePendingAddress.length && !bluetoothPairBeginProcess.running && !bluetoothPairRespondProcess.running
                onActivated: deviceRow.activated()
            }
            MenuButton {
                visible: deviceRow.paired && !deviceRow.connected
                width: visible ? 30 : 0; height: 32; label: "…"
                enabled: !root.bluetoothDevicePendingAddress.length
                Accessible.name: "Esquecer " + (deviceRow.device.name || deviceRow.device.address)
                onActivated: deviceRow.forgetRequested()
            }
        }
    }

'''+s[a:]
a=s.index('                    Column {\n                        visible: root.renderedControls.controlsBluetoothOpen');b=s.index('                    Text {\n                        visible: root.renderedControlsAllClosed() && root.hardwareControlError',a)
s=s[:a]+'''                    Column {
                        visible: root.renderedControls.controlsBluetoothOpen
                        width: parent.width; spacing: 8
                        MenuButton { outlined: true; iconName: "chevron-left"; label: root.bluetoothRemoveAddress.length ? "Voltar aos dispositivos" : "Voltar às ligações"; enabled: !bluetoothRemoveProcess.running; onActivated: { if (root.bluetoothRemoveAddress.length) { root.bluetoothRemoveAddress = ""; root.bluetoothRemoveName = "" } else root.openControlSection("bluetooth") } }
                        Text { text: "Bluetooth"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold }
                        Column {
                            id: bluetoothContent
                            property bool formVisible: root.bluetoothPairPhase.length > 0 || root.bluetoothRemoveAddress.length > 0
                            width: parent.width; spacing: 8
                            Rectangle {
                                visible: !bluetoothContent.formVisible
                                width: parent.width; height: 56; radius: 14; color: root.controlButtonSurface
                                RadioIconButton {
                                    x: 8; anchors.verticalCenter: parent.verticalCenter
                                    iconName: root.bluetoothDisplayPowered() ? "bluetooth" : "bluetooth-off"
                                    powered: root.bluetoothDisplayPowered()
                                    busy: bluetoothPowerProcess.running || root.bluetoothPowerPhase.length > 0
                                    actionLabel: root.bluetoothDisplayPowered() ? "Desativar Bluetooth" : "Ativar Bluetooth"
                                    onActivated: root.toggleBluetoothPower()
                                }
                                Column {
                                    anchors.left: parent.left; anchors.leftMargin: 54
                                    anchors.right: bluetoothSearchButton.left; anchors.rightMargin: 10
                                    anchors.verticalCenter: parent.verticalCenter; spacing: 3
                                    Text { width: parent.width; elide: Text.ElideRight; text: "Bluetooth"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize }
                                    Text { text: root.bluetoothDisplayPowered() ? "Ativo" : "Desativado"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuMetaSize }
                                }
                                MenuButton {
                                    id: bluetoothSearchButton
                                    visible: root.bluetoothDisplayPowered()
                                    anchors.right: parent.right; anchors.rightMargin: 8; anchors.verticalCenter: parent.verticalCenter
                                    width: visible ? 108 : 0; height: 32
                                    label: bluetoothScanProcess.running ? "A procurar…" : "Procurar"
                                    enabled: !bluetoothScanProcess.running && !root.bluetoothPowerPhase.length
                                    onActivated: bluetoothScanProcess.running = true
                                }
                            }
                            Rectangle {
                                id: bluetoothPairCard
                                visible: root.bluetoothPairPhase.length > 0
                                width: parent.width; height: visible ? bluetoothPairFields.implicitHeight + 24 : 0
                                radius: 14; color: root.controlButtonSurface; border.width: 1; border.color: root.controlButtonOutline
                                Column {
                                    id: bluetoothPairFields
                                    x: 12; y: 12; width: parent.width - 24; spacing: 10
                                    Row {
                                        width: parent.width; height: 40; spacing: 10
                                        Rectangle { width: 36; height: 36; radius: 18; anchors.verticalCenter: parent.verticalCenter; color: Qt.lighter(root.controlButtonSurface, 1.6); LucideIcon { anchors.centerIn: parent; name: "bluetooth"; width: 16; height: 16 } }
                                        Column {
                                            width: parent.width - 46; anchors.verticalCenter: parent.verticalCenter; spacing: 3
                                            Text { width: parent.width; elide: Text.ElideRight; text: root.bluetoothPairName; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.DemiBold }
                                            Text { text: "Emparelhar dispositivo"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                        }
                                    }
                                    Text {
                                        width: parent.width; wrapMode: Text.Wrap
                                        text: root.bluetoothPairPhase === "needs-response" && root.bluetoothPairChallenge === "confirm" ? "Confirma que este código coincide no dispositivo." : (root.bluetoothPairPhase === "needs-response" && root.bluetoothPairChallenge === "pin" ? "Introduz o PIN apresentado pelo dispositivo." : (root.bluetoothPairPhase === "waiting-device" ? "Escreve este código no dispositivo Bluetooth." : (root.bluetoothMessage || "A aguardar o dispositivo…")))
                                        color: root.bluetoothPairPhase === "failed" ? "#ffb0bd" : root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize
                                    }
                                    Rectangle {
                                        visible: root.bluetoothPairPasskey.length > 0
                                        width: parent.width; height: visible ? 52 : 0; radius: 9; color: root.controlButtonActive
                                        Text { anchors.centerIn: parent; text: root.bluetoothPairPasskey; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: 24; font.letterSpacing: 4 }
                                    }
                                    Text { visible: bluetoothPinField.visible; text: "PIN"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                    Rectangle {
                                        id: bluetoothPinField
                                        visible: root.bluetoothPairPhase === "needs-response" && root.bluetoothPairChallenge === "pin"
                                        width: parent.width; height: visible ? 40 : 0; radius: 9; color: root.controlButtonActive
                                        border.width: bluetoothPinInput.activeFocus ? 1 : 0; border.color: root.textMain
                                        enabled: !bluetoothPairRespondProcess.running
                                        TextInput {
                                            id: bluetoothPinInput
                                            anchors.fill: parent; anchors.leftMargin: 9; anchors.rightMargin: 94
                                            verticalAlignment: TextInput.AlignVCenter; activeFocusOnTab: true
                                            Accessible.name: "PIN do dispositivo Bluetooth"
                                            text: root.bluetoothPairPin; onTextChanged: root.bluetoothPairPin = text
                                            echoMode: root.bluetoothShowPin ? TextInput.Normal : TextInput.Password; maximumLength: 16
                                            color: root.textMain; selectionColor: root.controlButtonOutline; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                                            Keys.onPressed: event => { if (event.key === Qt.Key_Tab || event.key === Qt.Key_Backtab) root.navigateGenericMenu(event) }
                                            onActiveFocusChanged: if (activeFocus) { root.clearPendingMenuFocus(); root.focusedMenuItem = bluetoothPinInput }
                                            onAccepted: if (text.length) root.respondBluetoothPair(true, text)
                                        }
                                        MenuButton {
                                            anchors.right: parent.right; anchors.rightMargin: 5; anchors.verticalCenter: parent.verticalCenter
                                            width: 84; height: 30; lighterSurface: true; label: root.bluetoothShowPin ? "Ocultar" : "Mostrar"
                                            onActivated: { root.bluetoothShowPin = !root.bluetoothShowPin; if (!root.menuKeyboardNavigation) bluetoothPinInput.forceActiveFocus() }
                                        }
                                    }
                                    Row {
                                        width: parent.width; spacing: 8
                                        MenuButton {
                                            width: root.bluetoothPairPhase === "needs-response" ? (parent.width - 8) / 2 : parent.width; height: 38
                                            label: root.bluetoothPairPhase === "completed" || root.bluetoothPairPhase === "failed" ? "Fechar" : (root.bluetoothPairPhase === "needs-response" ? "Cancelar" : "A aguardar…")
                                            enabled: !bluetoothPairBeginProcess.running && !bluetoothPairRespondProcess.running && ["needs-response", "completed", "failed"].indexOf(root.bluetoothPairPhase) >= 0
                                            onActivated: root.bluetoothPairPhase === "needs-response" ? root.cancelBluetoothPairing() : root.dismissBluetoothPairing()
                                        }
                                        MenuButton {
                                            visible: root.bluetoothPairPhase === "needs-response"
                                            width: (parent.width - 8) / 2; height: 38; accent: true
                                            label: root.bluetoothPairChallenge === "pin" ? "Emparelhar" : "Confirmar"
                                            enabled: !bluetoothPairRespondProcess.running && (root.bluetoothPairChallenge !== "pin" || root.bluetoothPairPin.length > 0)
                                            onActivated: root.respondBluetoothPair(true, root.bluetoothPairChallenge === "pin" ? root.bluetoothPairPin : "")
                                        }
                                    }
                                }
                            }
                            Rectangle {
                                id: bluetoothForgetCard
                                visible: root.bluetoothRemoveAddress.length > 0
                                width: parent.width; height: visible ? bluetoothForgetFields.implicitHeight + 24 : 0
                                radius: 14; color: root.controlButtonSurface; border.width: 1; border.color: root.controlButtonOutline
                                Column {
                                    id: bluetoothForgetFields
                                    x: 12; y: 12; width: parent.width - 24; spacing: 10
                                    Text { width: parent.width; elide: Text.ElideRight; text: root.bluetoothRemoveName; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.DemiBold }
                                    Text { width: parent.width; wrapMode: Text.Wrap; text: "Esquecer este dispositivo? Para voltar a usá-lo, será necessário emparelhar novamente."; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                                    Row {
                                        width: parent.width; spacing: 8
                                        MenuButton { width: (parent.width - 8) / 2; height: 38; label: "Cancelar"; enabled: !bluetoothRemoveProcess.running; onActivated: { root.bluetoothRemoveAddress = ""; root.bluetoothRemoveName = "" } }
                                        MenuButton { width: (parent.width - 8) / 2; height: 38; label: bluetoothRemoveProcess.running ? "A esquecer…" : "Esquecer"; enabled: !bluetoothRemoveProcess.running; onActivated: root.confirmBluetoothRemove() }
                                    }
                                }
                            }
                            Text { visible: !bluetoothContent.formVisible && root.bluetoothMessage.length > 0; width: parent.width; wrapMode: Text.Wrap; text: root.bluetoothMessage; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            Text { visible: !bluetoothContent.formVisible && root.bluetoothConnectedDevices().length > 0; text: "Ligados"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            Repeater {
                                model: bluetoothContent.formVisible ? [] : root.bluetoothConnectedDevices()
                                BluetoothDeviceRow {
                                    required property var modelData
                                    device: modelData; connected: true; paired: modelData.paired === true
                                    onActivated: root.bluetoothDeviceAction("bluetooth-disconnect", modelData)
                                }
                            }
                            Text { visible: !bluetoothContent.formVisible && root.bluetoothKnownDevices().length > 0; text: "Guardados"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            Repeater {
                                model: bluetoothContent.formVisible ? [] : root.bluetoothKnownDevices()
                                BluetoothDeviceRow {
                                    required property var modelData
                                    device: modelData; paired: true
                                    onActivated: root.bluetoothDeviceAction("bluetooth-connect", modelData)
                                    onForgetRequested: root.beginBluetoothRemove(modelData)
                                }
                            }
                            Text { visible: !bluetoothContent.formVisible && root.bluetoothAvailableDevices().length > 0; text: "Disponíveis"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            Repeater {
                                model: bluetoothContent.formVisible ? [] : root.bluetoothAvailableDevices()
                                BluetoothDeviceRow {
                                    required property var modelData
                                    device: modelData
                                    onActivated: root.beginBluetoothPair(modelData)
                                }
                            }
                            Text { visible: !bluetoothContent.formVisible && root.bluetoothDisplayPowered() && !bluetoothScanProcess.running && !root.bluetoothKnownDevices().length && !root.bluetoothConnectedDevices().length && !root.bluetoothAvailableDevices().length && !root.bluetoothMessage.length; width: parent.width; wrapMode: Text.Wrap; text: "Nenhum dispositivo encontrado"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                        }
                    }

'''+s[b:]
p.write_text(s)
