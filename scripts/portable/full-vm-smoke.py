#!/usr/bin/env python3
"""Disposable VM fixture exercising the real portable graphical installation."""
import argparse
import json
from pathlib import Path
import secrets
import os
import signal
import subprocess
import time

RESULT = Path("/root/full-vm-result.json")


def call(*args, check=True, **kwargs):
    result = subprocess.run(args, text=True, capture_output=True, check=False, **kwargs)
    if check and result.returncode:
        raise RuntimeError(f"{args[0]}: {(result.stderr or result.stdout)[-2500:]}")
    return result


def inside(machine, *args, user="apx", check=True):
    return call("systemd-run", "-M", machine, "--quiet", "--wait", "--pipe", "--collect",
                "--expand-environment=no",
                "--property=User=" + user, *args, check=check)


def hub(*args):
    return inside("apx-hub", "/usr/bin/apx", *args).stdout


def active(name, timeout=150):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            value = json.loads(Path("/run/apx/active-graphical-environment-v1.json").read_text())
            if value["name"] == name:
                return value
        except (FileNotFoundError, KeyError, json.JSONDecodeError): pass
        time.sleep(.25)
    raise RuntimeError("graphical readiness missing for " + name)


def main(mode):
    if call("systemd-detect-virt", "--vm", "--quiet", check=False).returncode \
            or not Path("/etc/apx-disposable-full-vm").is_file():
        raise RuntimeError("disposable VM fixture only")
    events = []
    def event(name):
        events.append(name)
        RESULT.write_text(json.dumps({"state": "running", "checks": events}, indent=2) + "\n")
        print("APX_FULL_VM_CHECK " + name, flush=True)
    if mode == "install":
        call("/usr/lib/systemd/systemd-networkd-wait-online", "--any", "--ipv4", "--timeout=60")
        # New synthetic identity exists only in the disposable guest. Never
        # copy the physical pilot's password, tokens or biometric enrollment.
        password = secrets.token_urlsafe(24)
        with Path("/root/full-install.log").open("w") as log:
            result = subprocess.run(["bash", "/root/apx/scripts/portable/install-apx-full.sh", "--apply", "--password-stdin"],
                                    input=password + "\n", text=True, stdout=log, stderr=subprocess.STDOUT)
        password = None
        if result.returncode:
            raise RuntimeError("full installer failed; inspect /root/full-install.log")
        event("fresh-generic-graphical-install")
        call("systemctl", "start", "apx-portable-graphical.service")
    state = active("hub")
    event("current-quickshell-and-hyprland-ready")
    identity = inside("apx-hub", "/run/apx/environment-switch-client-v1.py", "identity").stdout
    if json.loads(identity).get("name") != "hub": raise RuntimeError("authenticated Hub identity differs")
    event("authenticated-hub-service-identity")
    root = Path("/var/lib/apx")
    # The source seed is compared byte for byte, not just parsed by QML.
    import importlib.util, hashlib
    spec = importlib.util.spec_from_file_location("full_installer", "/root/apx/scripts/portable/install_apx_full.py")
    installer = importlib.util.module_from_spec(spec); spec.loader.exec_module(installer)
    for relative, expected in installer.manifests()["ENVIRONMENT_SHELL_ASSETS"].items():
        path = Path("/usr/share/apx/config-seeds/environment-shell-v1") / relative
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError("installed shell source differs: " + relative)
    event("all-current-shell-source-digests-match")
    plan = json.loads(hub("environment", "create-plan", "vmwork", "--role", "graphical-base"))
    hub("environment", "create", "--plan", plan["digest"], "--approve", "CREATE vmwork AS graphical-base")
    event("hub-creates-independent-intermediate-workload")
    # Switch through the real authenticated socket. The client may be stopped
    # after the accepted request when its old Hub session is retired.
    inside("apx-hub", "/run/apx/environment-switch-client-v1.py", "open", "--target", "vmwork", check=False)
    work = active("vmwork")
    machine = "apx-g" + work["generation"].split("-")[0][:7]
    event("graphical-workload-switch")
    if inside(machine, "/usr/bin/test", "-S", "/run/apx/executor.sock", check=False).returncode == 0:
        raise RuntimeError("workload received the management socket")
    rejected = inside(machine, "/run/apx/environment-switch-client-v1.py", "create", "--target", "forbidden", check=False)
    if rejected.returncode == 0 or (root / "environments/forbidden").exists():
        raise RuntimeError("workload management was not rejected")
    if "only the authoritative active Hub" not in rejected.stderr:
        raise RuntimeError("workload request did not reach the Hub authorization refusal: " + rejected.stderr[-500:])
    direct = inside(machine, "/usr/bin/apx", "environment", "create-plan", "forbidden", "--role", "minimal", check=False)
    if direct.returncode == 0:
        raise RuntimeError("workload CLI unexpectedly reached management")
    event("workload-management-is-refused")
    inside(machine, "/usr/bin/touch", "/home/apx/private-vm-test.txt")
    if (root / "environments/hub/home/apx/private-vm-test.txt").exists() or Path("/home/apx/private-vm-test.txt").exists():
        raise RuntimeError("workload private file leaked")
    inside(machine, "/usr/lib/systemd/systemd-networkd-wait-online", "--interface=host0", "--ipv4", "--timeout=60", user="root")
    inside(machine, "/usr/bin/pacman", "-Syu", "--needed", "--noconfirm", "ed", user="root")
    inside(machine, "/usr/bin/pacman", "-Q", "ed")
    if call("pacman", "-Q", "ed", check=False).returncode == 0 \
            or call("pacman", "--root", str(root / "environments/hub/root"), "-Q", "ed", check=False).returncode == 0:
        raise RuntimeError("workload package appeared in Host or Hub")
    event("real-package-and-file-isolation")
    inside(machine, "/run/apx/environment-switch-client-v1.py", "return", check=False)
    active("hub")
    event("authenticated-return-to-hub")
    inside("apx-hub", "/run/apx/environment-switch-client-v1.py", "open", "--target", "vmwork", check=False)
    crashed = active("vmwork")
    os.kill(crashed["pid"], signal.SIGKILL)
    active("hub")
    event("workload-compositor-failure-recovers-to-hub")
    hub("environment", "snapshot", "vmwork")
    event("stopped-graphical-workload-snapshot")
    # Archive/restore the smaller normal headless role to bound test storage.
    plan = json.loads(hub("environment", "create-plan", "vmarchive", "--role", "minimal"))
    hub("environment", "create", "--plan", plan["digest"], "--approve", "CREATE vmarchive AS minimal")
    hub("environment", "start", "vmarchive")
    inside("apx-vmarchive", "/usr/bin/touch", "/home/apx/restored-marker")
    hub("environment", "stop", "vmarchive")
    archive = hub("environment", "archive", "vmarchive").strip().splitlines()[-1]
    hub("environment", "restore", "--archive", archive, "--name", "vmrestored", "--approve", "RESTORE " + archive + " AS vmrestored")
    if not (root / "environments/vmrestored/home/apx/restored-marker").is_file():
        raise RuntimeError("restored private home marker missing")
    event("normal-environment-archive-and-restore")
    for name in ("vmwork", "vmarchive", "vmrestored"):
        plan = json.loads(hub("environment", "destroy-plan", name))
        hub("environment", "destroy", "--plan", plan["digest"], "--approve", "DESTROY " + name)
    event("test-workloads-and-their-copies-destroyed")
    preview = inside("apx-hub", "/usr/bin/python", "-c",
                     "import runpy,json; m=runpy.run_path('/run/apx/coordinated-update-client-v1.py');"
                     "print(json.dumps(m['exchange']('environments.preview',{})))")
    if json.loads(preview.stdout).get("classification") != "ready-for-approval":
        raise RuntimeError("portable Environment update preview is not ready")
    event("authenticated-environment-update-preview")
    refused = call("bash", "/root/apx/scripts/portable/install-apx-full.sh", "--apply", "--password-stdin", input="", check=False)
    if refused.returncode != 2: raise RuntimeError("existing installation was not refused")
    event("existing-installation-overwrite-refused")
    inside("apx-hub", "/usr/bin/python", "-c",
           "import os,subprocess;from pathlib import Path;"
           "p=Path('/run/apx/session-1000');d=[s.name for s in p.glob('wayland-*') if s.is_socket()];"
           "assert len(d)==1;os.environ.update(XDG_RUNTIME_DIR=str(p),WAYLAND_DISPLAY=d[0]);"
           "subprocess.run(['/usr/bin/quickshell','--path','/home/apx/.config/quickshell/apx/shell.qml',"
           "'ipc','call','host','toggleControls'],check=True)")
    event("control-centre-opened-through-real-quickshell-ipc")
    RESULT.write_text(json.dumps({"state": "passed", "checks": events, "active": active("hub")}, indent=2) + "\n")
    print("APX_FULL_VM_PASS", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("mode", choices=("install", "check"))
    args = parser.parse_args()
    try:
        main(args.mode)
    except Exception as error:
        try: record = json.loads(RESULT.read_text())
        except (OSError, ValueError): record = {"checks": []}
        record.update(state="failed", error=str(error))
        RESULT.write_text(json.dumps(record, indent=2) + "\n")
        print("APX_FULL_VM_FAIL " + str(error), flush=True)
        raise
