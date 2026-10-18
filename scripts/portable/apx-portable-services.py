#!/usr/bin/env python3
"""Portable adapters around the current authenticated service contracts."""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load(filename, label):
    spec = importlib.util.spec_from_file_location(label, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[label] = module
    spec.loader.exec_module(module)
    return module


def configure_peer():
    import apx_host_services_peer as peer
    def hub(credentials):
        identity = peer.authorize_active_environment_peer(credentials)
        if (identity.name, identity.role) != ("hub", "hub"):
            raise peer.HostServicesPeerError("only the authoritative active Hub may manage Environments")
    peer.authorize_official_hub_peer = hub
    peer.authorize_shared_service_peer = peer.authorize_active_environment_peer
    return peer


def generic_hardware(base):
    def backlight():
        candidates = [p for p in Path("/sys/class/backlight").iterdir()
                      if (p / "brightness").is_file() and (p / "max_brightness").is_file()]
        if len(candidates) != 1:
            raise RuntimeError("display backlight is absent or ambiguous")
        return candidates[0]
    keyboards = [p for p in Path("/sys/class/leds").glob("*kbd_backlight*") if (p / "brightness").is_file()]
    if len(keyboards) == 1: base.KEYBOARD_BACKLIGHT = keyboards[0]
    def controls():
        value = {}
        try:
            device = backlight()
            maximum = base._read_hardware_integer(device / "max_brightness", 1, 2**31 - 1)
            raw = base._read_hardware_integer(device / "brightness", 0, maximum)
            value.update(display_brightness=round(100 * raw / maximum),
                         display_brightness_raw=raw, display_brightness_max=maximum)
        except (OSError, RuntimeError): pass
        if len(keyboards) == 1:
            maximum = base._read_hardware_integer(keyboards[0] / "max_brightness", 1, 255)
            value.update(keyboard_brightness=base._read_hardware_integer(keyboards[0] / "brightness", 0, maximum),
                         keyboard_brightness_max=maximum)
        return value
    def profile():
        value = {"schema": 1, "platform_profiles": [], "gpu_profiles": [], "reboot_required": False}
        if base.PLATFORM_CHOICES.is_file() and base.PLATFORM_PROFILE.is_file():
            value.update(platform_profiles=base.PLATFORM_CHOICES.read_text().split(),
                         platform_profile=base.PLATFORM_PROFILE.read_text().strip())
        value.update(controls())
        return value
    base.display_backlight = backlight
    base.hardware_control_status = controls
    base.hardware_profile_status = profile
    base.platform_profile_status = profile
    original = base.apply
    def apply(operation, payload, peer, shell_pid):
        if operation.startswith("hardware.gpu."):
            raise RuntimeError("A mudança de modo gráfico não está disponível neste computador.")
        return original(operation, payload, peer, shell_pid)
    base.apply = apply
    base.RUNNER = "/usr/lib/apx/apx-portable-power.py"


def configure_switch(module, peer):
    graphical = load("apx-portable-graphical.py", "apx_portable_graphical")
    def hub_management(credentials, **unused):
        peer.authorize_official_hub_peer(credentials)
        if module.MANAGEMENT_LOCK.exists():
            raise RuntimeError("Já existe uma operação de Environment em curso.")
    module.authorize_hub_management = hub_management
    original = module.apply
    def apply(operation, payload, credentials):
        if operation.startswith("native.") or (operation == "environment.create" and payload.get("system_kind") != "arch"):
            raise RuntimeError("A instalação de Windows não está disponível nesta versão.")
        if operation == "switch.to-workload":
            hub_management(credentials)
            target = graphical.registration(payload["target"])
            graphical.queue_switch(target["name"], target["generation"])
            return {"accepted": True, "direction": "hub-to-workload", "target": target["name"]}
        if operation == "return.to-hub":
            identity = peer.authorize_active_environment_peer(credentials)
            if identity.name == "hub" or identity.role != "graphical-base":
                raise PermissionError("only the active workload may return to Hub")
            hub = graphical.registration("hub")
            graphical.queue_switch("hub", hub["generation"])
            return {"accepted": True, "direction": "workload-to-hub"}
        if operation == "status.get":
            identity = peer.authorize_active_environment_peer(credentials)
            return {"active": identity.name, "handoff_running": graphical.NEXT.exists(),
                    "identity": module.active_identity(credentials)}
        return original(operation, payload, credentials)
    module.apply = apply


def main():
    if len(sys.argv) != 2 or os.geteuid(): raise ValueError("requires Host root and one fixed service name")
    service = sys.argv[1]
    allowed = {"host-services-v1", "host-services-v2", "host-services-v3", "audio-state-v1",
               "environment-switch-v1", "system-power-v1", "environment-hardware-v1", "coordinated-update-v1"}
    if service not in allowed: raise ValueError("unsupported portable service")
    peer = configure_peer()
    module = load("apx-" + service + ".py", "apx_portable_" + service.replace("-", "_"))
    if hasattr(module, "EXPECTED_HOSTNAME"):
        # This adapter is admitted only by the root-owned installation record.
        # Peer authority remains tied to the current private namespace and generation.
        graph = load("apx-portable-graphical.py", "apx_portable_graphical_identity")
        installed = graph.trusted(Path("/var/lib/apx/portable-graphical-install.json"), max_size=262144)
        if installed.get("profile") != "portable-graphical-v1":
            raise ValueError("portable Host installation identity is missing")
        module.EXPECTED_HOSTNAME = Path("/etc/hostname").read_text().strip()
    wifi = [p.name for p in Path("/sys/class/net").iterdir() if (p / "wireless").exists()]
    if hasattr(module, "WIFI_INTERFACE"):
        module.WIFI_INTERFACE = wifi[0] if len(wifi) == 1 else "apx-no-wifi"
    if service == "environment-switch-v1": configure_switch(module, peer)
    if service == "system-power-v1":
        generic_hardware(module)
        from apx_active_shell_peer import quickshell_ancestor
        def shell(pid):
            values = dict(line.split(":", 1) for line in Path(f"/proc/{pid}/status").read_text().splitlines() if ":" in line)
            return quickshell_ancestor(peer.HostServicesPeer(pid, int(values["Uid"].split()[0]), int(values["Gid"].split()[0])))
        module.quickshell_parent = shell
    if service == "environment-hardware-v1": generic_hardware(module.base)
    if service == "coordinated-update-v1":
        original = module.apply
        def environments_only(operation, payload):
            if not operation.startswith("environments."):
                raise RuntimeError("use the Environment-only update workflow; Host updates belong to the Arch console")
            return original(operation, payload)
        module.apply = environments_only
    module.serve()


if __name__ == "__main__":
    main()
