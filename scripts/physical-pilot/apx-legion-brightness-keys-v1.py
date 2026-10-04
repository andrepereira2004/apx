#!/usr/bin/env python3
"""Bridge the exact Lenovo ITE function row into the running Hub shell."""

from __future__ import annotations

import fcntl
import os
from pathlib import Path
import select
import stat
import struct
import subprocess


ITE_NAME = "ITE Tech. Inc. ITE Device(8910) Keyboard"
# The same internal i8042 device has been observed in both translation modes.
# Normalize the aliases into one role so two AT devices still fail closed.
AT_NAME = "AT Translated Set 2 keyboard"
AT_NAMES = frozenset((AT_NAME, "AT Raw Set 2 keyboard"))
VIDEO_NAME = "Video Bus"
IDEAPAD_NAME = "Ideapad extra buttons"
EV_KEY = 1
KEY_PRINT = 99
KEY_BRIGHTNESSDOWN = 224
KEY_BRIGHTNESSUP = 225
EVENT = struct.Struct("llHHI")
LAPTOP_ACTION = "/home/apx/.local/bin/apx-laptop-action-v1"
LOCK = "/run/apx/session-1000/apx-legion-brightness-keys-v1.lock"


def _ioc_read(kind: int, number: int, size: int) -> int:
    return (2 << 30) | (size << 16) | (kind << 8) | number


def _device_name(descriptor: int) -> str:
    data = bytearray(256)
    fcntl.ioctl(descriptor, _ioc_read(ord("E"), 0x06, len(data)), data, True)
    return bytes(data).split(b"\0", 1)[0].decode("utf-8", "strict")


def open_exact_keyboards() -> dict[int, str]:
    matches: dict[str, list[int]] = {ITE_NAME: [], AT_NAME: [], VIDEO_NAME: [], IDEAPAD_NAME: []}
    for node in sorted(Path("/dev/input").glob("event*")):
        metadata = node.stat(follow_symlinks=False)
        if not stat.S_ISCHR(metadata.st_mode) or os.major(metadata.st_rdev) != 13:
            continue
        descriptor = os.open(node, os.O_RDONLY | os.O_NONBLOCK | os.O_CLOEXEC)
        try:
            name = _device_name(descriptor)
            if name in AT_NAMES:
                name = AT_NAME
            if name in matches:
                matches[name].append(descriptor)
            else:
                os.close(descriptor)
        except Exception:
            os.close(descriptor)
            raise
    if any(len(matches[name]) != 1 for name in (ITE_NAME, AT_NAME)) \
            or any(len(descriptors) > 1 for descriptors in matches.values()):
        for descriptors in matches.values():
            for descriptor in descriptors:
                os.close(descriptor)
        raise RuntimeError("exact Lenovo internal keyboards are absent or ambiguous")
    return {descriptors[0]: name for name, descriptors in matches.items() if descriptors}


def call_shell(method: str) -> None:
    try:
        subprocess.run(
            ("/usr/bin/quickshell", "-c", "apx", "ipc", "call", "host", method),
            check=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=3,
        )
    except (OSError, subprocess.SubprocessError):
        # A transient shell restart must not terminate the keyboard bridge.
        return


def launch_action(action: str) -> None:
    try:
        subprocess.Popen(
            (LAPTOP_ACTION, action),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        call_shell("hotkeyFailed")


def handle_key(name: str, code: int, value: int, scan: int | None = None) -> None:
    if value != 1:
        return
    # Only semantic brightness events, never raw F5/F6. The real Fn events
    # on this boot originate on ACPI Video Bus, not the complete ITE keyboard.
    if name in (ITE_NAME, VIDEO_NAME) and code == KEY_BRIGHTNESSDOWN:
        call_shell("brightnessDown")
    elif name in (ITE_NAME, VIDEO_NAME) and code == KEY_BRIGHTNESSUP:
        call_shell("brightnessUp")
    elif name == AT_NAME and code == KEY_PRINT:
        launch_action("screenshot")
    elif name == IDEAPAD_NAME and code == 364 and scan == 0x101:
        # Three isolated Fn+F9 presses proved KEY_FAVORITES with scan 0x101.
        # The earlier 0x10d/KEY_UNKNOWN assignment was not this physical key.
        launch_action("apps")
    elif name == IDEAPAD_NAME and code == 248:
        call_shell("microphoneMute")
    elif name == IDEAPAD_NAME and code == 247:
        # The kernel already changes the radios. Report its resulting state;
        # toggling them here as well would immediately undo the physical key.
        launch_action("airplane-status")
    elif name == IDEAPAD_NAME and code == 532:
        launch_action("touchpad-off")
    elif name == IDEAPAD_NAME and code == 531:
        launch_action("touchpad-on")


def handle_event(name: str, event_type: int, code: int, value: int,
                 scans: dict[str, int]) -> None:
    if event_type == 0:
        # SYN_REPORT and SYN_DROPPED invalidate frame-local scan information.
        if code in (0, 3):
            scans.pop(name, None)
    elif event_type == 4 and code == 4 and name == IDEAPAD_NAME:
        scans[name] = value
    elif event_type == EV_KEY:
        handle_key(name, code, value, scans.pop(name, None))


def main() -> int:
    lock = os.open(LOCK, os.O_RDWR | os.O_CREAT | os.O_CLOEXEC, 0o600)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(lock)
        return 0
    keyboards = open_exact_keyboards()
    # Observe the exact ITE interface without grabbing it exclusively. The
    # physical follow-up after enabling an exclusive grab reported a non-responsive
    # keyboard and repeated clean compositor exits, so exclusivity remains
    # disabled until the complete key/modifier stream is proved safe.
    poller = select.poll()
    scans: dict[str, int] = {}
    for descriptor in keyboards:
        poller.register(descriptor, select.POLLIN | select.POLLERR | select.POLLHUP)
    while True:
        for descriptor, flags in poller.poll():
            if flags & (select.POLLERR | select.POLLHUP):
                raise RuntimeError("Lenovo ITE brightness keyboard disconnected")
            data = os.read(descriptor, EVENT.size * 32)
            for offset in range(0, len(data) - EVENT.size + 1, EVENT.size):
                _, _, event_type, code, value = EVENT.unpack_from(data, offset)
                name = keyboards[descriptor]
                # ITE is the complete keyboard, not an Fn-only interface. Its
                # raw F1--F12 codes are therefore ordinary application keys.
                # Act only on semantic firmware events that cannot be emitted
                # by a plain F key while fn_lock is off.
                handle_event(name, event_type, code, value, scans)


if __name__ == "__main__":
    raise SystemExit(main())
