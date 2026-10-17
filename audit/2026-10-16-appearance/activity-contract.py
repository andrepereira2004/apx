from pathlib import Path
p=Path('config/environment-shell-v1/quickshell/apx/BarButton.qml');s=p.read_text().replace('    property string iconName: ""','    property string iconName: ""\n    property int iconSize: iconName.startsWith("battery") ? (iconName === "battery-charging" ? 23 : 29) : 17').replace('implicitHeight: 30','implicitHeight: Math.max(30, iconSize + 2)').replace('iconSize: 17','iconSize: button.iconSize');p.write_text(s)
p=Path('src/apx_host_services_v3_contract.py');s=p.read_text().replace('"radio.status",','"radio.status", "radio.airplane",',1)
s=s.replace('    if operation == "appearance.save":','    if operation == "radio.airplane":\n        if set(payload) != {"enabled"} or type(payload["enabled"]) is not bool:\n            raise HostServicesV3ContractError("airplane mode requires a boolean")\n        return dict(payload)\n    if operation == "appearance.save":',1);p.write_text(s)
p=Path('scripts/physical-pilot/apx-host-services-v3.py');s=p.read_text().replace('"radio.status", "snapshot.get"','"radio.status", "radio.airplane", "snapshot.get"',1)
anchor='def _default_route() -> bool:'
s=s.replace(anchor,'''def set_airplane(enabled: bool) -> dict[str, object]:
    before = radio_state()
    if not before["radios_present"]: raise UnsupportedError("Os rádios Wi-Fi e Bluetooth não estão disponíveis")
    changed = []
    try:
        for kind in ("wlan", "bluetooth"):
            result = run((RFKILL, "block" if enabled else "unblock", kind))
            if result.returncode: raise HostServicesV3Error("Não foi possível alterar o modo de avião")
            changed.append(kind)
        state = radio_state()
        if state["wlan_soft_blocked"] != enabled or state["bluetooth_soft_blocked"] != enabled:
            raise HostServicesV3Error("O modo de avião não foi confirmado")
        return state
    except HostServicesV3Error:
        for kind in reversed(changed):
            run((RFKILL, "block" if before[kind + "_soft_blocked"] else "unblock", kind))
        raise


'''+anchor)
s=s.replace('    if operation == "radio.status": return radio_state()','    if operation == "radio.status": return radio_state()\n    if operation == "radio.airplane": return set_airplane(bool(payload["enabled"]))')
s=s.replace('"network.connect", "network.disconnect", "network.forget", "network.scan"}:','"network.connect", "network.disconnect", "network.forget", "network.scan", "radio.airplane"}:')
p.write_text(s)
p=Path('scripts/physical-pilot/apx-host-services-client-v3.py');s=p.read_text().replace('"wifi-status", "radio-status",','"wifi-status", "radio-status", "radio-airplane",').replace('"wifi-status": "network.status", "radio-status": "radio.status",','"wifi-status": "network.status", "radio-status": "radio.status", "radio-airplane": "radio.airplane",')
s=s.replace('    if arguments.operation == "appearance-save":','    if arguments.operation == "radio-airplane":\n        if arguments.target not in {"on", "off"}: parser.error("airplane mode requires on or off")\n        payload = {"enabled": arguments.target == "on"}\n    if arguments.operation == "appearance-save":')
p.write_text(s)
