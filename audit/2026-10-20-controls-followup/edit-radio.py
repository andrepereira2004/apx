from pathlib import Path
p=Path('src/apx_host_services_v3_contract.py');s=p.read_text().replace('"network.portal.open", "network.scan", "network.status", "radio.status", "radio.airplane",','"network.portal.open", "network.scan", "network.status", "network.power", "radio.status", "radio.airplane",',1).replace('    if operation == "bluetooth.power":','    if operation in {"bluetooth.power", "network.power"}:');p.write_text(s)
p=Path('scripts/physical-pilot/apx-host-services-v3.py');s=p.read_text().replace('"network.scan", "network.status", "radio.status",','"network.scan", "network.status", "network.power", "radio.status",',1)
s=s.replace('    state.update(_cached_connectivity(identity, bool(state["connected"])))','    state.update(_cached_connectivity(identity, bool(state["connected"])))\n    radio = radio_state()\n    state["powered"] = radio["wlan_present"] and not radio["wlan_soft_blocked"]\n    state["hardware_blocked"] = radio["wlan_hard_blocked"]')
s=s.replace('    for directory in sorted(RFKILL_ROOT.glob("rfkill*")):\n','    wlan_hard_blocked = False\n    for directory in sorted(RFKILL_ROOT.glob("rfkill*")):\n',1)
s=s.replace('            radios[kind].append(blocked)','            radios[kind].append(blocked)\n            if kind == "wlan":\n                try: wlan_hard_blocked = wlan_hard_blocked or (directory / "hard").read_text().strip() == "1"\n                except OSError: pass',1)
s=s.replace('        "airplane_mode": present', '        "wlan_present": bool(radios["wlan"]),\n        "wlan_hard_blocked": wlan_hard_blocked,\n        "airplane_mode": present',1)
s=s.replace('\ndef set_airplane(enabled:', '''
def set_wifi_power(powered: bool) -> dict[str, object]:
    before = radio_state()
    if not before["wlan_present"]:
        raise UnsupportedError("O rádio Wi-Fi não está disponível")
    if powered and before["wlan_hard_blocked"]:
        raise ConflictError("O Wi-Fi está bloqueado pelo interruptor físico")
    result = run((RFKILL, "unblock" if powered else "block", "wlan"))
    if result.returncode or radio_state()["wlan_soft_blocked"] == powered:
        raise HostServicesV3Error("Não foi possível confirmar a alimentação do Wi-Fi")
    emit("network.changed")
    return network_state()


def set_airplane(enabled:''',1)
s=s.replace('    if operation == "network.status": return network_state()','    if operation == "network.status": return network_state()\n    if operation == "network.power": return set_wifi_power(bool(payload["powered"]))',1)
s=s.replace('"network.connect", "network.disconnect", "network.forget", "network.scan", "radio.airplane"}', '"network.connect", "network.disconnect", "network.power", "network.forget", "network.scan", "radio.airplane"}',1);p.write_text(s)
p=Path('scripts/physical-pilot/apx-host-services-client-v3.py');s=p.read_text().replace('"wifi-portal-open", "wifi-scan", "wifi-status",','"wifi-portal-open", "wifi-scan", "wifi-status", "wifi-power",',1).replace('"wifi-status": "network.status",','"wifi-status": "network.status", "wifi-power": "network.power",',1).replace('if arguments.operation == "bluetooth-power":','if arguments.operation in {"bluetooth-power", "wifi-power"}:',1);p.write_text(s)
p=Path('scripts/physical-pilot/apx-host-services-ui-v3.py');s=p.read_text().replace('        "network_details": details,','        "network_details": details,\n        "wifi_powered": network.get("powered", True),\n        "wifi_hardware_blocked": network.get("hardware_blocked", False),').replace('elif operation in {"bluetooth-power", "bluetooth-connect", "bluetooth-disconnect"}', 'elif operation in {"wifi-power", "bluetooth-power", "bluetooth-connect", "bluetooth-disconnect"}').replace('mapped = {"bluetooth-power":', 'mapped = {"wifi-power": "wifi-power", "bluetooth-power":');p.write_text(s)
p=Path('config/environment-shell-v1/quickshell/apx/shell.qml');s=p.read_text();a=s.index('    function wifiDisplayActive()');s=s[:a]+'''    function wifiDisplayPowered() { return hostState.wifi_powered !== false }
    function toggleWifiPower() {
        if (wifiPowerProcess.running) return
        cancelWifiPassword()
        wifiMessage = ""
        wifiPowerProcess.command = ["/run/apx/host-services-ui-v3.py", "wifi-power", wifiDisplayPowered() ? "off" : "on"]
        wifiPowerProcess.running = true
    }
    Process {
        id: wifiPowerProcess
        stderr: StdioCollector { onStreamFinished: if (text.trim()) root.wifiMessage = text.trim() }
        onExited: (code, status) => {
            if (code && !root.wifiMessage.length) root.wifiMessage = "Não foi possível alterar o Wi-Fi."
            hostStatusProcess.running = true
        }
    }

'''+s[a:]
s=s.replace('iconName: root.wifiDisplayActive() ? "wifi" : "wifi-off"; caption: "Wi-Fi  ·  " + (root.wifiDisplayActive() ? "Ligado" : "Desligado"); selected: root.wifiDisplayActive()', 'iconName: root.wifiDisplayPowered() ? "wifi" : "wifi-off"; caption: "Wi-Fi  ·  " + (root.wifiDisplayPowered() ? "Ativo" : "Desativado"); selected: root.wifiDisplayPowered()')
start=s.index('                        Text { text: "Wi-Fi";',s.index('id: menuFlick'));pos=s.index('                        Rectangle {',start)
s=s[:pos]+'''                        ControlTile {
                            width: parent.width; height: 48; showCaption: true
                            iconName: root.wifiDisplayPowered() ? "wifi" : "wifi-off"
                            caption: wifiPowerProcess.running ? "A alterar…" : (root.wifiDisplayPowered() ? "Desativar Wi-Fi" : "Ativar Wi-Fi")
                            enabled: !wifiPowerProcess.running
                            onActivated: root.toggleWifiPower()
                        }
'''+s[pos:]
start=s.index('                                id: disconnectButton');end=s.index('                        Row {',start);part=s[start:end].replace('84 : 0','108 : 0').replace('label: "Desligar"','label: "Desconectar"');s=s[:start]+part+s[end:]
s=s.replace('text: "Outras redes"; color:', 'visible: root.wifiDisplayPowered()\n                            text: "Outras redes"; color:',1).replace('model: Array.from(new Set(root.hostState.available_networks || []))','model: root.wifiDisplayPowered() ? Array.from(new Set(root.hostState.available_networks || [])) : []',1).replace('visible: !(root.hostState.available_networks || []).length\n                            text: "Nenhuma rede encontrada"','visible: !root.wifiDisplayPowered() || !(root.hostState.available_networks || []).length\n                            text: root.wifiDisplayPowered() ? "Nenhuma rede encontrada" : "Wi-Fi desativado"',1)
s=s.replace('(root.bluetoothDisplayPowered() ? "Desligar Bluetooth" : "Ligar Bluetooth")','(root.bluetoothDisplayPowered() ? "Desativar Bluetooth" : "Ativar Bluetooth")',1)
s=s.replace('text: "Desligar"; color: root.textMain;', 'text: "Desconectar"; color: root.textMain;',1)
# Avoid a second wheel receiver in the Bluetooth content; the outer menu owns scrolling.
s=s.replace('                        contentWidth: width; contentHeight: bluetoothContent.implicitHeight\n', '                        interactive: false\n                        contentWidth: width; contentHeight: bluetoothContent.implicitHeight\n',1)
p.write_text(s)
