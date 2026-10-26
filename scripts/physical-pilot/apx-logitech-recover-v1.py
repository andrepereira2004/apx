#!/usr/bin/python3
"""Recover a missing G305 once per outage, without resetting healthy input."""
import fcntl
import json
import time
from pathlib import Path

USB = Path('/sys/bus/usb/devices')
INPUT = Path('/sys/class/input')
DRIVER = Path('/sys/bus/usb/drivers/usb')
STATE = Path('/run/apx-logitech-recover-v1')


def read(path):
    try:
        return path.read_text().strip().lower()
    except OSError:
        return ''


def receivers():
    return [p for p in USB.iterdir()
            if read(p / 'idVendor') == '046d'
            and read(p / 'idProduct') == 'c53f']


def mouse_present(receiver):
    parent = receiver.resolve()
    for event in INPUT.glob('event*'):
        device = (event / 'device').resolve()
        if (device.is_relative_to(parent)
                and read(device / 'id/vendor') == '046d'
                and read(device / 'id/product') == '4074'):
            return True
    return False


def wait_for_mouse(receiver):
    for _ in range(10):
        if mouse_present(receiver):
            return True
        time.sleep(0.5)
    return mouse_present(receiver)


def recover(receiver):
    # Use the receiver's identity in this boot, so reconnecting permits a retry.
    stamp = STATE / receiver.name
    identity = str(receiver.stat().st_ino)
    if mouse_present(receiver):
        stamp.unlink(missing_ok=True)
        return
    if read(stamp) == identity:
        return
    if wait_for_mouse(receiver):
        stamp.unlink(missing_ok=True)
        return
    stamp.write_text(identity)
    print(f'{receiver.name}: G305 absent; reconnecting its USB receiver.', flush=True)
    (DRIVER / 'unbind').write_text(receiver.name)
    try:
        time.sleep(0.2)
    finally:
        (DRIVER / 'bind').write_text(receiver.name)
    if wait_for_mouse(receiver):
        stamp.unlink(missing_ok=True)
        print(f'{receiver.name}: Logitech G305 recovered.', flush=True)
    else:
        print(f'{receiver.name}: G305 still absent; no repeated reset until '
              'mouse returns or receiver is reconnected.', flush=True)


def record_health(devices):
    # Log only changes; no input events or typed content are read.
    status = {"receivers": [{"port": device.name,
                              "mouse_present": mouse_present(device),
                              "power_control": read(device / 'power/control'),
                              "runtime_status": read(device / 'power/runtime_status')}
                             for device in sorted(devices)]}
    path = STATE / 'health.json'
    try:
        if json.loads(path.read_text()) == status:
            return
    except (OSError, ValueError):
        pass
    temporary = STATE / '.health.tmp'
    temporary.write_text(json.dumps(status, sort_keys=True) + '\n')
    temporary.replace(path)
    print(json.dumps(dict(event='logitech-health', **status), sort_keys=True), flush=True)


def main():
    STATE.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (STATE / 'lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        devices = receivers()
        for receiver in devices:
            try:
                recover(receiver)
            except FileNotFoundError:
                # Unplugging during a scan is not a service failure.
                continue
            except OSError as error:
                print(f'{receiver.name}: recovery failed: {error}', flush=True)
                raise
        record_health(receivers())


if __name__ == '__main__':
    main()
