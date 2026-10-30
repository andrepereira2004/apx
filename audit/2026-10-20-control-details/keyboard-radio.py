from pathlib import Path
repo=Path(__file__).resolve().parents[2];p=repo/'config/environment-shell-v1/quickshell/apx/shell.qml';s=p.read_text()
s=s.replace('    function applyRadioState(state) {','''    property bool airplaneWifiKnown: false
    property bool airplaneWifiPowered: false
    property bool airplaneBluetoothKnown: false
    property bool airplaneBluetoothPowered: false
    function refreshAirplaneDetails() {
        if (!radioStatusProcess.running) radioStatusProcess.running = true
        if (!airplaneBluetoothStatusProcess.running) airplaneBluetoothStatusProcess.running = true
    }
    function applyRadioState(state) {
        if (state.wifi_powered !== undefined) {
            airplaneWifiPowered = state.wifi_powered === true
            airplaneWifiKnown = true
        }''',1)
s=s.replace('''        DesktopActivity.refresh()
    }
    function openMoreOptions''','''        if (kind === "airplane") refreshAirplaneDetails()
        else if (kind === "keyboard" && !hardwareProfileProcess.running) hardwareProfileProcess.running = true
        DesktopActivity.refresh()
    }
    function openMoreOptions''',1)
# Add per-radio powered fields to the existing read-only kernel query.
s=s.replace('"blocked=1; wlan=0; bluetooth=0; "','"blocked=1; wlan=0; bluetooth=0; wifi_powered=false; "')
s=s.replace('''            + "[ \\"''','''            + "[ \\"''') if False else s
needle='            + "[ \\"' # actual line handled below
line='            + "[ \\"'
old='''            + "[ \\"'''
# Insert after the case clause: powered means at least one unblocked WLAN radio.
needle='            + "[ \\"'
anchor='            + "[ $wlan = 1 ] && [ $bluetooth = 1 ] || exit 1; "'
pos=s.index(anchor)
s=s[:pos]+s[pos:]
# Separate command clause, before the loop ends.
s=s.replace('''            + "[ \\"''','''            + "[ \\"''') if False else s
actual=next(line for line in s.splitlines() if 'blocked=0; done;' in line)
replacement=actual.replace('done; ', 'if [ \\"$kind\\" = wlan ] && [ \\"$(<\\"$directory/soft\\")\\" = 0 ] && [ \\"$(<\\"$directory/hard\\")\\" = 0 ]; then wifi_powered=true; fi; done; ')
# Use direct escaped QML string to avoid quoting ambiguity.
replacement=r'''            + "[ \"$(<\"$directory/soft\")\" = 1 ] || blocked=0; "
            + "if [ \"$kind\" = wlan ] && [ \"$(<\"$directory/soft\")\" = 0 ] && [ \"$(<\"$directory/hard\")\" = 0 ]; then wifi_powered=true; fi; done; "'''
s=s.replace(actual,replacement)
s=s.replace(r'''printf '{\"airplane_mode\":%s}\\n' \"$value\"''',r'''printf '{\"airplane_mode\":%s,\"wifi_powered\":%s}\\n' \"$value\" \"$wifi_powered\"''')
# Insert independent lightweight BlueZ query; do not wait for legacy/full host report.
pos=s.index('    Process {\n        id: radioStatusProcess')
s=s[:pos]+'''    Process {
        id: airplaneBluetoothStatusProcess
        command: ["/run/apx/host-services-client-v3.py", "bluetooth-status"]
        stdout: StdioCollector {
            onStreamFinished: {
                try {
                    var state = JSON.parse(text)
                    if (typeof state.powered === "boolean") {
                        root.airplaneBluetoothPowered = state.powered
                        root.airplaneBluetoothKnown = true
                    }
                } catch (error) {}
            }
        }
    }
    Timer {
        interval: 500; repeat: true
        running: popup.open && root.popupKind === "controls" && root.controlsActivityKind === "airplane"
        triggeredOnStart: true
        onTriggered: root.refreshAirplaneDetails()
    }
    Connections {
        target: DesktopActivity
        function onBusyChanged() {
            if (!DesktopActivity.busy && popup.open && root.controlsActivityKind === "airplane") root.refreshAirplaneDetails()
        }
    }

'''+s[pos:]
# Service rows use dedicated authoritative fast state, preserving fallback before first sample.
a=s.index('visible: root.renderedControls.controlsActivityKind === "airplane"');b=s.index('visible: root.renderedControls.controlsActivityKind === "keyboard"',a)
part=s[a:b].replace('root.wifiDisplayPowered()', '(root.airplaneWifiKnown ? root.airplaneWifiPowered : root.wifiDisplayPowered())').replace('root.bluetoothDisplayPowered()', '(root.airplaneBluetoothKnown ? root.airplaneBluetoothPowered : root.bluetoothDisplayPowered())');s=s[:a]+part+s[b:]
a=s.index('                        Text { text: "Iluminação do teclado";',s.index('visible: root.renderedControls.controlsActivityKind === "keyboard"'));b=s.index('\n                    }\n                    ActivityPanel',a)
s=s[:a]+'''                        Rectangle {
                            width: parent.width; height: 72; radius: 14
                            color: root.controlButtonSurface
                            RadioIconButton {
                                x: 8; anchors.verticalCenter: parent.verticalCenter
                                iconName: "keyboard"; powered: root.keyboardBrightness > 0
                                busy: keyboardBrightnessProcess.running
                                actionLabel: "Alterar iluminação do teclado"
                                onActivated: root.cycleKeyboardBrightness()
                            }
                            Column {
                                anchors.left: parent.left; anchors.leftMargin: 54
                                anchors.right: parent.right; anchors.rightMargin: 12
                                anchors.verticalCenter: parent.verticalCenter; spacing: 4
                                Text { text: "Iluminação do teclado"; color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize; font.weight: Font.DemiBold }
                                Text { text: keyboardBrightnessProcess.running ? "A alterar…" : root.keyboardBrightness > 0 ? "Ligada" : "Desligada"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                            }
                        }
                        Text { text: "Intensidade atual"; color: root.textDim; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }
                        Rectangle {
                            width: parent.width; height: 92; radius: 14
                            color: root.controlButtonSurface
                            Text {
                                x: 14; y: 14
                                text: "Nível " + root.keyboardBrightness + " de " + root.keyboardBrightnessMax
                                color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: root.menuBodySize
                            }
                            Text {
                                anchors.right: parent.right; anchors.rightMargin: 14; y: 10
                                text: (root.keyboardBrightnessMax > 0 ? Math.round(root.keyboardBrightness * 100 / root.keyboardBrightnessMax) : 0) + "%"
                                color: root.textMain; font.family: Appearance.fontFamily; font.pixelSize: Appearance.titleSize; font.weight: Font.DemiBold
                            }
                            Row {
                                x: 14; anchors.bottom: parent.bottom; anchors.bottomMargin: 18
                                width: parent.width - 28; spacing: 6
                                Repeater {
                                    model: Math.max(0, root.keyboardBrightnessMax)
                                    Rectangle {
                                        required property int index
                                        width: (parent.width - Math.max(0, root.keyboardBrightnessMax - 1) * 6) / Math.max(1, root.keyboardBrightnessMax)
                                        height: 8; radius: 4
                                        color: index < root.keyboardBrightness ? root.textMain : root.controlButtonOutline
                                    }
                                }
                            }
                        }
                        Text { visible: root.hardwareControlError.length > 0; width: parent.width; text: root.hardwareControlError; wrapMode: Text.WordWrap; color: "#ff91a4"; font.family: Appearance.fontFamily; font.pixelSize: root.menuSmallSize }'''+s[b:]
s=s.replace('function openAirplaneControls(): void {','function openKeyboardControls(): void { openControls(); root.openActivitySection("keyboard") }\n        function openAirplaneControls(): void {',1)
p.write_text(s)
