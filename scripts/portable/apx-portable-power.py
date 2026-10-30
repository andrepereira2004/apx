#!/usr/bin/env python3
"""Complete a server-confirmed power action after stopping the portable session."""
import argparse
import fcntl
import os
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--action", required=True, choices=("reboot", "poweroff", "suspend"))
if __name__ == "__main__":
    args = parser.parse_args()
    if os.geteuid(): raise SystemExit("Host root required")
    reservation = Path("/run/apx/system-power-v1.reserved")
    if reservation.is_symlink() or not reservation.is_file() or reservation.stat().st_uid:
        raise SystemExit("confirmed power reservation is missing")
    with Path("/run/apx/machine-transition-v1.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.action != "suspend":
            subprocess.run(["systemctl", "stop", "apx-portable-graphical.service"], check=True)
        subprocess.run(["systemctl", args.action], check=True)
        reservation.unlink(missing_ok=True)
