#!/usr/bin/env python3
"""Lease physical external HID nodes and relay udev into one graphical session.

No key or pointer events are read. Only device metadata crosses namespaces.
The parent launcher owns this process; losing its pinned container ends work.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
import os
from pathlib import Path
import re
import socket
import stat
import struct
import subprocess
import time

ENGINE = Path('/var/lib/apx/official-hub-v1/apx-official-hub-graphical-v1.py')
SEND = '''import socket,sys
s=socket.socket(socket.AF_NETLINK,socket.SOCK_RAW,15)
s.bind((0,0))
s.sendto(sys.stdin.buffer.read(65536),(0,2))
'''


def run(args, **kwargs):
    return subprocess.run(args, check=True, capture_output=True, timeout=5, **kwargs)


def policies(unit):
    lines = run(['systemctl', 'show', unit, '-p', 'DeviceAllow', '--value'], text=True).stdout.splitlines()
    result = []
    for line in lines:
        parts = line.split()
        if len(parts) != 2 or parts[1] not in {'r', 'rw', 'rwm'}:
            raise RuntimeError('unexpected device policy')
        result.append(tuple(parts))
    return result


def removal_packet(packet):
    offset = struct.unpack_from('=I', packet, 16)[0]
    properties = packet[offset:].replace(b'ACTION=add\0', b'ACTION=remove\0', 1)
    header = bytearray(packet[:offset])
    struct.pack_into('=I', header, 20, len(properties))
    return bytes(header) + properties


class Bridge:
    def __init__(self, leader, outer, seatd):
        self.leader, self.outer, self.seatd = leader, outer, seatd
        self.proc = Path('/proc') / str(leader)
        self.start = (self.proc / 'stat').read_text().rsplit(')', 1)[1].split()[19]
        self.user_map = (self.proc / 'uid_map').read_text()
        start, base, length = map(int, self.user_map.split())
        if start != 0 or base < 65536 or length != 65536:
            raise RuntimeError('not an APX private user namespace')
        self.owner = base + 1000
        self.check()
        spec = importlib.util.spec_from_file_location('input_engine', ENGINE)
        self.engine = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.engine)
        internal = {node for label, node in self.engine.resolve_input_devices().items()
                    if not label.startswith("external_")}
        self.base_policies = {
            unit: [(node, access) for node, access in policies(unit)
                   if not node.startswith('/dev/input/') or node in internal]
            for unit in (outer, seatd)
        }
        self.external = {}
        self.managed = set()
        self.receiver = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, 15)
        self.receiver.bind((0, 2))
        self.receiver.settimeout(1)
        self.snapshot = None
        self.display_snapshot = None
        self.display_compositor = None
        self.packets = {}
        # A private, non-listening socket enables libudev subscriptions. It
        # exposes no Host udev control channel; this bridge supplies the events.
        control = self.proc / 'root/run/udev/control'
        self.control = None
        if not control.exists():
            self.control = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
            self.control.bind(str(control))
            os.chmod(control, 0)
        (self.proc / 'root/run/apx/input-bridge-v1.ready').write_text('ready\n')

    def check(self):
        if (self.proc / 'stat').read_text().rsplit(')', 1)[1].split()[19] != self.start \
                or (self.proc / 'uid_map').read_text() != self.user_map \
                or '/system.slice/' + self.outer not in (self.proc / 'cgroup').read_text():
            raise RuntimeError('graphical session identity changed')

    def inventory(self):
        result = {}
        for node in Path('/dev/input').glob('event*'):
            try:
                info = node.stat()
                if not stat.S_ISCHR(info.st_mode) or os.major(info.st_rdev) != 13:
                    continue
                props = run(['udevadm', 'info', '--query=property', '--name=' + str(node)], text=True).stdout
                values = dict(line.split('=', 1) for line in props.splitlines() if '=' in line)
                if self.engine.admitted_external_input(values, str(node)):
                    result[str(node)] = (info.st_rdev, info.st_ino)
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        return result

    def update_policies(self, devices):
        self.check()
        for unit, baseline in self.base_policies.items():
            preserved = [(node, access) for node, access in baseline if node not in self.managed]
            args = ['systemctl', 'set-property', '--runtime', unit, 'DeviceAllow=']
            args += ['DeviceAllow=' + node + ' ' + access for node, access in preserved]
            args += ['DeviceAllow=' + node + ' rw' for node in sorted(devices)]
            run(args)

    def notify(self, node, subsystem="input", action="add"):
        # Obtain libudev's real header/hashes from the Host. A metadata-only add
        # announcement does not disconnect, grab, or synthesize keyboard input.
        run(['udevadm', 'trigger', '--action=' + action, '/sys/class/' + subsystem + '/' + Path(node).name])
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            try:
                packet = self.receiver.recv(65536)
            except socket.timeout:
                continue
            if not packet.startswith(b'libudev\0') or ('DEVNAME=' + node + '\0').encode() not in packet \
                    or ('ACTION=' + action + '\0').encode() not in packet:
                continue
            self.check()
            if subsystem == "drm" and b'HOTPLUG=1\0' not in packet:
                packet += b'HOTPLUG=1\0'
                packet = bytearray(packet)
                struct.pack_into('=I', packet, 20, len(packet) - struct.unpack_from('=I', packet, 16)[0])
                packet = bytes(packet)
            self.relay(packet)
            self.packets[node] = packet
            return
        raise RuntimeError('no udev announcement for ' + node)

    def relay(self, packet):
        self.check()
        run(['nsenter', '--target', str(self.leader), '--user', '--net', '--pid', '--mount', '--',
             '/usr/bin/python3', '-c', SEND], input=packet, cwd='/')

    def forward_display_events(self, cards):
        # DRM status may remain cached until the compositor probes connectors.
        # Forward the real udev hotplug instead of waiting for that cache to
        # change first. Drain input metadata too; evdev data is never read.
        for _ in range(128):
            try:
                packet = self.receiver.recv(65536, socket.MSG_DONTWAIT)
            except (BlockingIOError, socket.timeout):
                return
            if len(packet) < 40 or not packet.startswith(b"libudev\0"):
                continue
            offset, length = struct.unpack_from("=II", packet, 16)
            if offset < 40 or offset + length != len(packet):
                continue
            props = dict(item.split(b"=", 1) for item in packet[offset:].split(b"\0") if b"=" in item)
            if props.get(b"SUBSYSTEM") != b"drm" or props.get(b"ACTION") != b"change" \
                    or props.get(b"HOTPLUG") != b"1":
                continue
            node = props.get(b"DEVNAME", b"").decode("utf-8", "replace")
            if node not in cards:
                continue
            self.relay(packet)
            print(json.dumps({"event": "display-hotplug-forwarded", "node": node}), flush=True)

    def refresh(self):
        self.check()
        cards = [node for node, _ in self.base_policies[self.seatd]
                 if re.fullmatch(r'/dev/dri/card[0-9]+', node)]
        self.forward_display_events(cards)
        # The initial reconciliation runs before Hyprland subscribes to udev.
        # Replay it once its IPC socket exists, and again after a restart.
        sockets = list((self.proc / 'root/run/apx/session-1000/hypr').glob('*/.socket.sock'))
        compositor = sockets[0].parent.name if len(sockets) == 1 and sockets[0].is_socket() else None
        display_snapshot = tuple(sorted((str(p), p.read_text().strip()) for card in cards
                                 for p in Path('/sys/class/drm').glob(Path(card).name + '-*/status')))
        # Reconcile already-connected outputs on bridge startup too: a hotplug
        # may have happened before this process subscribed.
        if display_snapshot != self.display_snapshot or (compositor and compositor != self.display_compositor):
            for card in cards:
                self.notify(card, "drm", "change")
                print(json.dumps({"event": "display-rescan", "node": card}), flush=True)
        self.display_snapshot = display_snapshot
        self.display_compositor = compositor
        snapshot = tuple(sorted((str(p), p.stat().st_ino) for p in Path('/dev/input').glob('event*')))
        if snapshot == self.snapshot:
            return
        devices = self.inventory()
        self.managed.update(devices)
        self.update_policies(devices)
        for node, identity in devices.items():
            if self.external.get(node) == identity:
                continue
            target = self.proc / ('root' + node)
            if not target.exists():
                os.mknod(target, stat.S_IFCHR | 0o660, identity[0])
                os.chown(target, self.owner, self.owner)
                os.chmod(target, 0o660)
            info = target.stat()
            if not stat.S_ISCHR(info.st_mode) or info.st_rdev != identity[0]:
                raise RuntimeError('unexpected container input node')
            self.notify(node)
            print(json.dumps({'event': 'external-input-admitted', 'node': node}), flush=True)
        # Unplug closes evdev FDs in libinput. Revoke access before removing
        # non-mounted nodes; the container owns the lifetime of startup binds.
        for node in self.external.keys() - devices.keys():
            packet = self.packets.pop(node, None)
            if packet:
                self.relay(removal_packet(packet))
            target = self.proc / ('root' + node)
            try:
                target.unlink()
            except OSError:
                pass
        self.external, self.snapshot = devices, snapshot


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--leader', type=int, required=True)
    parser.add_argument('--outer-unit', required=True)
    parser.add_argument('--seatd-unit', choices=['apx-official-hub-seatd.service', 'apx-graphical-seatd.service'], required=True)
    args = parser.parse_args()
    if os.geteuid() != 0 or args.leader <= 1 \
            or re.fullmatch(r'apx-(?:official-hub-graphical|graphical-[a-z0-9-]+)-[a-f0-9]{8}\.service', args.outer_unit) is None:
        raise RuntimeError('invalid graphical bridge identity')
    bridge = Bridge(args.leader, args.outer_unit, args.seatd_unit)
    while True:
        bridge.check()
        try:
            bridge.refresh()
        except (OSError, subprocess.SubprocessError, RuntimeError) as error:
            bridge.check()
            print('external input retry: ' + str(error), flush=True)
        time.sleep(0.75)


if __name__ == '__main__':
    main()
