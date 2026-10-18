#!/usr/bin/env python3
"""Experimental generic seat supervisor for private APX graphical Environments."""
from __future__ import annotations
import argparse
import fcntl
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import shutil
import stat
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from apx_portable_hardware import discover, validate_node

STATE = Path("/var/lib/apx")
RUN = Path("/run/apx")
ACTIVE = RUN / "active-graphical-environment-v1.json"
NEXT = RUN / "portable-next.json"
LEASES = Path("/dev/apx-portable-device-leases")
NAME = re.compile(r"[a-z][a-z0-9-]{0,26}")
SERVICES = ("host-services-v1", "host-services-v2", "host-services-v3", "audio-state-v1",
            "environment-switch-v1", "system-power-v1", "environment-hardware-v1", "coordinated-update-v1")
CLIENTS = ("apx-host-services-client-v1.py", "apx-host-services-client-v2.py", "apx-host-services-client-v3.py",
           "apx-host-services-ui-v3.py", "apx-desktop-menu-v2.py", "apx-audio-state-client-v1.py",
           "apx-environment-switch-client-v1.py", "apx-system-power-client-v1.py", "apx-coordinated-update-client-v1.py")


def run(*args, check=True, timeout=60):
    result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False,
                            env={**os.environ, "LC_ALL": "C"})
    if check and result.returncode:
        raise RuntimeError(f"{args[0]}: {(result.stderr or result.stdout)[-1200:]}")
    return result


def trusted(path: Path, max_size=16384) -> dict:
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid or info.st_gid or info.st_mode & 0o022 \
            or not 0 < info.st_size <= max_size:
        raise ValueError(f"untrusted APX record: {path}")
    value = json.loads(path.read_text())
    if type(value) is not dict:
        raise ValueError("APX record must be an object")
    return value


def atomic(path: Path, value: dict, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
    temp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, "w") as stream:
        json.dump(value, stream, sort_keys=True); stream.write("\n")
        stream.flush(); os.fsync(stream.fileno())
    os.replace(temp, path)


def selected_udev_view(nodes, destination, source=Path('/run/udev'), inputs=Path('/sys/class/input')):
    """Expose public discovery metadata only for the already admitted devices."""
    identifiers = {f"c{item['major']}:{item['minor']}" for item in nodes}
    for item in nodes:
        if item['kind'] != 'input': continue
        parent = (inputs / Path(item['node']).name / 'device').resolve().name
        if re.fullmatch(r'input[0-9]+', parent): identifiers.add('+input:' + parent)
    for directory in (destination, destination / 'data', destination / 'tags'):
        directory.mkdir(mode=0o755, exist_ok=True); directory.chmod(0o755)
    for identifier in sorted(identifiers):
        record = source / 'data' / identifier
        if not record.exists(): continue
        info = record.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid or info.st_gid or info.st_mode & 0o022 or info.st_size > 65536:
            raise ValueError('untrusted device discovery metadata')
        target = destination / 'data' / identifier
        target.write_bytes(record.read_bytes()); target.chmod(0o644)
        for tag in (source / 'tags').iterdir():
            if not re.fullmatch(r'[A-Za-z0-9_-]+', tag.name) or not (tag / identifier).is_file(): continue
            directory = destination / 'tags' / tag.name
            directory.mkdir(mode=0o755, exist_ok=True); directory.chmod(0o755)
            (directory / identifier).touch(mode=0o644)
            (directory / identifier).chmod(0o644)


def registration(name: str) -> dict:
    if not NAME.fullmatch(name):
        raise ValueError("invalid Environment name")
    record = trusted(STATE / "environments" / name / "registration.json")
    if record.get("name") != name or record.get("role") != ("hub" if name == "hub" else "graphical-base") \
            or not re.fullmatch(r"[0-9a-f]{8}-[0-9a-f-]{27}", str(record.get("generation"))) \
            or record.get("state") not in {"running", "stopped"}:
        raise ValueError("graphical registration differs")
    return record


def queue_switch(target: str, generation: str):
    record = registration(target)
    if record["generation"] != generation or record["state"] != "stopped":
        raise ValueError("switch target changed or is not stopped")
    fd = os.open(NEXT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump({"target": target, "generation": generation}, stream)


def translated_user(machine: str) -> int:
    leader = run("machinectl", "show", machine, "--property=Leader", "--value").stdout.strip()
    if not leader.isdecimal():
        raise ValueError("container leader is missing")
    lines = Path(f"/proc/{leader}/uid_map").read_text().splitlines()
    fields = lines[0].split() if len(lines) == 1 else []
    if len(fields) != 3 or fields[0] != "0" or fields[2] != "65536" or int(fields[1]) < 65536:
        raise ValueError("unexpected private user namespace")
    return int(fields[1]) + 1000


def wait_translated_user(machine: str, unit: str, timeout: float = 120) -> int:
    # nspawn registers only AFTER translating a fresh private root's ownership.
    # An intermediate desktop can contain enough files to exceed ten seconds.
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            return translated_user(machine)
        except (RuntimeError, ValueError, OSError):
            if run('systemctl', 'is-active', '--quiet', unit, check=False).returncode:
                raise RuntimeError('graphical container ended before registration')
            time.sleep(.2)
    raise RuntimeError('graphical container registration timed out')


def find_process(unit: str, comm: str) -> int | None:
    prefix = f"/system.slice/{unit}"
    found = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdecimal(): continue
        try:
            group = (proc / "cgroup").read_text().strip().split(":", 2)[-1]
            if (group == prefix or group.startswith(prefix + "/")) and (proc / "comm").read_text().strip() == comm:
                found.append(int(proc.name))
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
    return found[0] if len(found) == 1 else None


def inside(machine: str, *command, check=True):
    return run("systemd-run", "-M", machine, "--quiet", "--wait", "--pipe", "--collect",
               "--expand-environment=no", *command,
               check=check)


def hyprctl(machine: str, *args):
    directory = inside(machine, "/usr/bin/bash", "-c",
                       "for p in /run/apx/session-1000/hypr/*/.socket.sock; do test -S \"$p\" && basename \"${p%/.socket.sock}\"; done")
    signature = directory.stdout.strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,200}", signature):
        raise ValueError("compositor IPC is not ready")
    return inside(machine, "/usr/bin/setpriv", "--reuid=1000", "--regid=1000", "--clear-groups",
                  "/usr/bin/env", "XDG_RUNTIME_DIR=/run/apx/session-1000",
                  f"HYPRLAND_INSTANCE_SIGNATURE={signature}", "/usr/bin/hyprctl", *args)


class Session:
    def __init__(self, name):
        self.record = registration(name)
        self.name = name
        short = self.record["generation"].split("-")[0]
        self.machine = "apx-hub" if name == "hub" else "apx-g" + short[:7]
        self.unit = f"apx-portable-{name}-{short}.service"
        self.seat_unit = "apx-portable-seatd.service"
        self.environment = STATE / "environments" / name
        self.proxies = []
        self.hardware = None

    def active(self):
        return run("systemctl", "is-active", "--quiet", self.unit, check=False).returncode == 0

    def start(self, authenticated=False):
        self.hardware = discover()
        for service in SERVICES:
            endpoint = RUN / (service + ".sock")
            for _ in range(300):
                if endpoint.is_socket(): break
                time.sleep(.05)
            else: raise RuntimeError(f"portable service did not become ready: {service}")
        if LEASES.exists():
            raise ValueError("stale graphical leases require Host-console recovery")
        LEASES.mkdir(mode=0o700)
        for index, item in enumerate(self.hardware["nodes"]):
            current = validate_node(item["node"], item["kind"])
            if current != item:
                raise ValueError("device identity changed after discovery")
            proxy = LEASES / f"device-{index}"
            os.mknod(proxy, stat.S_IFCHR | 0o600, os.makedev(item["major"], item["minor"]))
            self.proxies.append((proxy, item))
        atomic(LEASES / "state.json", {"name": self.name, "generation": self.record["generation"],
                                      "nodes": self.hardware["nodes"]})
        selected_udev_view(self.hardware['nodes'], LEASES / 'udev')
        seat_nodes = [item for item in self.hardware["nodes"] if item["kind"] in {"input", "tty"}
                      or item["node"] == self.hardware["graphics"]["card"]]
        run("systemd-run", "--quiet", "--collect", "--unit=" + self.seat_unit,
            "--property=KillMode=mixed", "--property=TimeoutStopSec=5s", "--property=DevicePolicy=closed",
            *("--property=DeviceAllow=" + item["node"] + " rw" for item in seat_nodes),
            "--setenv=SEATD_VTBOUND=0", "/usr/bin/seatd", "-u", "root", "-l", "error")
        for _ in range(100):
            if Path("/run/seatd.sock").is_socket(): break
            time.sleep(.05)
        else: raise RuntimeError("seatd did not start")
        command = ["systemd-run", "--quiet", "--collect", "--unit=" + self.unit,
                   "--property=Delegate=yes", "--property=KillMode=mixed", "--property=TimeoutStopSec=10s",
                   "--property=MemoryMax=8G", "--property=TasksMax=4096", "--property=DevicePolicy=closed"]
        command += ["--property=DeviceAllow=" + item["node"] + " rw" for _, item in self.proxies]
        command += ["systemd-nspawn", "--quiet", "--keep-unit", "--boot", "--settings=no",
                    "--register=yes", "--machine=" + self.machine, "--directory=" + str(self.environment / "root"),
                    "--private-users=pick", "--private-users-ownership=chown", "--private-network", "--network-veth",
                    "--link-journal=no", "--console=pipe", "--bind=" + str(self.environment / "home") + ":/home:idmap",
                    "--bind=/run/seatd.sock:/run/seatd.sock",
                    "--bind-ro=" + str(LEASES / 'udev') + ":/run/udev"]
        command += [f"--bind={proxy}:{item['node']}" for proxy, item in self.proxies]
        bound_services = [service for service in SERVICES if service !=
                          ("environment-hardware-v1" if self.name == "hub" else "system-power-v1")]
        if self.name != "hub": bound_services.remove("coordinated-update-v1")
        for service in bound_services:
            endpoint = RUN / (service + ".sock")
            if not endpoint.is_socket(): raise RuntimeError(f"missing portable service {service}")
            command.append(f"--bind={endpoint}:{endpoint}")
        for filename in CLIENTS:
            target = filename.removeprefix("apx-")
            command.append(f"--bind-ro=/usr/lib/apx/{filename}:/run/apx/{target}")
        if self.name == "hub":
            command.append("--bind-ro=/run/apx/executor.sock:/run/apx/executor.sock")
            run("/usr/lib/apx/apx-environment-network-v1.py", "apply", "--environment", "hub")
        proof = RUN / "authenticated-handoff-v1"
        if authenticated:
            fd = os.open(proof, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o444)
            os.fchmod(fd, 0o444)
            os.write(fd, b"apx-authenticated-handoff-v1\n"); os.close(fd)
            command.append(f"--bind-ro={proof}:{proof}")
        try:
            run(*command)
            uid = wait_translated_user(self.machine, self.unit)
        finally:
            if authenticated: proof.unlink(missing_ok=True)
        for _ in range(200):
            if inside(self.machine, "/usr/bin/true", check=False).returncode == 0: break
            time.sleep(.05)
        inside(self.machine, "/usr/bin/udevadm", "settle", "--timeout=20")
        inside(self.machine, "/usr/bin/chmod", "0755", "/run/apx")
        for proxy, item in self.proxies:
            os.chown(proxy, uid, uid); os.chmod(proxy, 0o660)
        for endpoint in [Path("/run/seatd.sock")] + [RUN / (s + ".sock") for s in SERVICES]:
            os.chown(endpoint, uid, uid); os.chmod(endpoint, 0o660)
        inside(self.machine, "/usr/bin/install", "-d", "-m", "0700", "-o", "1000", "-g", "1000", "/run/apx/session-1000")
        run("systemd-run", "-M", self.machine, "--quiet", "--unit=apx-portable-desktop",
            "--property=User=apx", "--property=Group=apx", "--property=KillMode=mixed",
            "--setenv=AQ_DRM_DEVICES=" + self.hardware["graphics"]["card"],
            "/usr/bin/dbus-run-session", "--", "/usr/lib/apx/apx-portable-session.sh")
        run("chvt", "2", check=False)
        deadline = time.monotonic() + 300
        while time.monotonic() < deadline:
            if not self.active(): raise RuntimeError("graphical container ended before readiness")
            pid = find_process(self.unit, "Hyprland")
            shell = find_process(self.unit, "quickshell")
            if pid and shell:
                try:
                    monitors = json.loads(hyprctl(self.machine, "-j", "monitors").stdout)
                    if any(not m.get("disabled", False) for m in monitors):
                        self.record["state"] = "running"
                        atomic(self.environment / "registration.json", self.record)
                        atomic(ACTIVE, {"schema": 1, "profile": "apx-active-graphical-environment-v1",
                                       "name": self.name, "role": self.record["role"],
                                       "generation": self.record["generation"], "unit": self.unit, "pid": pid})
                        print(f"APX_PORTABLE_GRAPHICAL_READY {self.name}", flush=True)
                        self.compositor_pid = pid
                        return
                except (RuntimeError, ValueError): pass
            time.sleep(.2)
        raise RuntimeError("login/compositor/QuickShell readiness timed out")

    def close(self):
        ACTIVE.unlink(missing_ok=True)
        run("systemctl", "stop", self.unit, check=False)
        run("systemctl", "stop", self.seat_unit, check=False)
        for endpoint in [RUN / (s + ".sock") for s in SERVICES]:
            if endpoint.is_socket(): os.chown(endpoint, 0, 0); os.chmod(endpoint, 0o600)
        Path("/run/seatd.sock").unlink(missing_ok=True)
        for proxy, _ in self.proxies: proxy.unlink(missing_ok=True)
        if LEASES.exists():
            if (LEASES / 'udev').exists(): shutil.rmtree(LEASES / 'udev')
            (LEASES / "state.json").unlink(missing_ok=True); LEASES.rmdir()
        self.record["state"] = "stopped"
        atomic(self.environment / "registration.json", self.record)
        if self.name == "hub":
            run("/usr/lib/apx/apx-environment-network-v1.py", "remove", "--environment", "hub", check=False)
        run("chvt", "1", check=False)


def main():
    if os.geteuid(): raise ValueError("graphical supervisor requires Host root")
    RUN.mkdir(mode=0o755, exist_ok=True)
    lock = (RUN / "portable-graphical.lock").open("a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    def interrupted(*_): raise KeyboardInterrupt
    signal.signal(signal.SIGTERM, interrupted)
    target, authenticated = "hub", False
    fixture = RUN / "portable-vm-authenticated-fixture"
    if fixture.exists():
        if run("systemd-detect-virt", "--vm", check=False).returncode or fixture.is_symlink() \
                or fixture.stat().st_uid or fixture.read_bytes() != b"disposable-vm-test\n":
            raise ValueError("invalid disposable VM authentication fixture")
        authenticated = True
    while True:
        session = Session(target)
        try:
            session.start(authenticated)
            while session.active() and find_process(session.unit, "Hyprland") == session.compositor_pid:
                if NEXT.exists(): break
                time.sleep(.2)
        finally:
            session.close()
        if NEXT.exists():
            request = trusted(NEXT); NEXT.unlink()
            target = request["target"]
            if registration(target)["generation"] != request["generation"]:
                raise ValueError("queued generation changed")
            authenticated = True
        elif target != "hub":
            target, authenticated = "hub", True
        else:
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
