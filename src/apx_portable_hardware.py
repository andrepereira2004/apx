"""Discover a bounded graphical seat without model, serial or fixed PCI IDs.

Discovery does not grant access or change a device. The Host session supervisor
must validate nodes again before creating its own generation-bound proxies.
"""
from __future__ import annotations
from pathlib import Path
import os
import re
import stat
import subprocess

PATTERNS = {
    "drm": (r"/dev/dri/(?:card[0-9]+|renderD[0-9]+)", {226}),
    "input": (r"/dev/input/event[0-9]+", {13}),
    "audio": (r"/dev/snd/(?:controlC[0-9]+|pcmC[0-9]+D[0-9]+[pc]|timer|seq)", {116}),
    "video": (r"/dev/video[0-9]+", {81}),
    "tty": (r"/dev/tty2", {4}),
    "nvidia": (r"/dev/nvidia(?:[0-9]+|ctl|-modeset|-uvm(?:-tools)?)", None),
}


def validate_node(name: str, kind: str) -> dict:
    pattern, majors = PATTERNS[kind]
    path = Path(name)
    info = path.lstat()
    if not re.fullmatch(pattern, name) or not stat.S_ISCHR(info.st_mode) \
            or (majors is not None and os.major(info.st_rdev) not in majors):
        raise ValueError(f"unsupported {kind} node: {name}")
    return {"node": name, "kind": kind, "major": os.major(info.st_rdev), "minor": os.minor(info.st_rdev)}


def properties(node: Path) -> dict[str, str]:
    result = subprocess.run(["udevadm", "info", "--query=property", f"--name={node}"],
                            capture_output=True, text=True, timeout=5, check=False)
    if result.returncode:
        return {}
    return dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)


def select_display(cards: list[dict]) -> dict:
    """Prefer an active display, then firmware's primary GPU; reject ambiguity."""
    if not cards:
        raise ValueError("no DRM display/render pair; install a supported graphics driver")
    connected = [card for card in cards if card["connected"]]
    candidates = connected or cards
    primary = [card for card in candidates if card.get("boot_vga")]
    if len(primary) == 1:
        return primary[0]
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError("multiple display GPUs are eligible; an explicit seat selection is required")


def discover_graphics(sys_drm: Path = Path("/sys/class/drm")) -> dict:
    cards = []
    for card in sorted(sys_drm.glob("card*")):
        if not re.fullmatch(r"card[0-9]+", card.name):
            continue
        device = (card / "device").resolve(strict=True)
        renders = [p for p in sys_drm.glob("renderD*")
                   if (p / "device").resolve() == device]
        if len(renders) != 1:
            continue
        connected = []
        for connector in sys_drm.glob(card.name + "-*"):
            status = connector / "status"
            if status.is_file() and status.read_text().strip() == "connected":
                connected.append(connector.name[len(card.name) + 1:])
        boot = device / "boot_vga"
        driver = (device / "driver").resolve().name if (device / "driver").exists() else "unknown"
        cards.append({"card": "/dev/dri/" + card.name, "render": "/dev/dri/" + renders[0].name,
                      "connected": connected, "boot_vga": boot.exists() and boot.read_text().strip() == "1",
                      "driver": driver, "device_path": str(device)})
    return select_display(cards)


def admitted_input(props: dict, node: str) -> bool:
    return bool(re.fullmatch(r"/dev/input/event[0-9]+", node) and props.get("DEVNAME") == node
                and props.get("ID_INPUT") == "1" and props.get("ID_SEAT", "seat0") == "seat0"
                and any(props.get(key) == "1" for key in
                        ("ID_INPUT_KEYBOARD", "ID_INPUT_MOUSE", "ID_INPUT_TOUCHPAD", "ID_INPUT_TOUCHSCREEN")))


def discover() -> dict:
    graphics = discover_graphics()
    nodes = [validate_node(graphics["card"], "drm"), validate_node(graphics["render"], "drm")]
    inputs = []
    for node in sorted(Path("/dev/input").glob("event*")):
        if admitted_input(properties(node), str(node)):
            nodes.append(validate_node(str(node), "input")); inputs.append(str(node))
    if not inputs:
        raise ValueError("no input devices admitted on seat0")
    audio = []
    for node in sorted(Path("/dev/snd").glob("*")):
        if re.fullmatch(PATTERNS["audio"][0], str(node)):
            nodes.append(validate_node(str(node), "audio")); audio.append(str(node))
    if graphics["driver"] == "nvidia":
        # Only already-published character nodes. No modprobe, firmware write,
        # GPU mode switch or VFIO passthrough is part of generic seat discovery.
        for node in sorted(Path("/dev").glob("nvidia*")):
            if re.fullmatch(PATTERNS["nvidia"][0], str(node)):
                nodes.append(validate_node(str(node), "nvidia"))
    nodes.append(validate_node("/dev/tty2", "tty"))
    if len(nodes) > 128 or len({item["node"] for item in nodes}) != len(nodes):
        raise ValueError("graphical device set is oversized or ambiguous")
    wireless = sorted(p.name for p in Path("/sys/class/net").iterdir() if (p / "wireless").exists())
    return {"schema": 1, "seat": "seat0", "graphics": graphics, "inputs": inputs,
            "audio": audio, "wifi_interface": wireless[0] if len(wireless) == 1 else None,
            "nodes": nodes}
