#!/usr/bin/env python3
"""TEST FIXTURE ONLY: root command channel inside an owner-controlled QEMU guest.

Never installed by APX. No physical disks, shared Host filesystems or public
network listeners are exposed. The VM owner already controls QMP and its disk.
"""
import json
from pathlib import Path
import subprocess
import time

PROTOCOL_VERSION = 2

if __name__ == "__main__":
    port = Path("/dev/virtio-ports/apx.lab")
    if subprocess.run(["systemd-detect-virt", "--vm", "--quiet"]).returncode \
            or not Path("/etc/apx-disposable-full-vm").is_file():
        raise SystemExit("disposable VM fixture only")
    while not port.exists(): time.sleep(.1)
    with port.open("r+b", buffering=0) as stream:
        while True:
            request = {}
            try:
                data = bytearray()
                while not data.endswith(b"\n") and len(data) <= 65536:
                    item = stream.read(1)
                    if not item: time.sleep(.05); continue
                    data += item
                request = json.loads(data)
                args = request["args"]
                if type(args) is not list or not args or any(type(arg) is not str for arg in args):
                    raise ValueError("command must be a string vector")
                result = subprocess.run(args, text=True, capture_output=True, timeout=min(600, int(request.get("timeout", 60))))
                response = {"exit_code": result.returncode, "stdout": result.stdout[-100000:], "stderr": result.stderr[-20000:]}
            except Exception as error:
                response = {"exit_code": -1, "error": str(error)}
            response['request_id'] = request.get('request_id')
            try:
                payload = memoryview((json.dumps(response) + "\n").encode())
                while payload:
                    count = stream.write(payload)
                    if count: payload = payload[count:]
                    else: time.sleep(.01)
            except OSError: time.sleep(.1)
