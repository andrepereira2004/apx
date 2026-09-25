#!/usr/bin/env python3
"""Produce a non-executable native Windows migration review artifact."""
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from apx_native_instances_v3 import plan_second_windows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--legacy", type=Path, required=True)
    parser.add_argument("--disk-serial", required=True)
    parser.add_argument("--new-name", required=True)
    parser.add_argument("--new-generation", required=True)
    parser.add_argument("--ntfs-min-bytes", type=int, required=True)
    parser.add_argument("--apx-used-bytes", type=int, required=True)
    parser.add_argument("--luks-header-bytes", type=int, required=True)
    parser.add_argument("--existing-gib", type=int, default=120)
    parser.add_argument("--new-gib", type=int, default=80)
    args = parser.parse_args()
    table = json.loads(args.inventory.read_text())["partitiontable"]
    legacy = json.loads(args.legacy.read_text())
    if legacy["disk_serial"] != args.disk_serial:
        raise ValueError("observed disk serial differs from registry")
    plan = plan_second_windows(table, legacy, new_name=args.new_name,
                              new_generation=args.new_generation,
                              ntfs_min_bytes=args.ntfs_min_bytes,
                              apx_used_bytes=args.apx_used_bytes,
                              luks_header_bytes=args.luks_header_bytes,
                              existing_gib=args.existing_gib, new_gib=args.new_gib)
    print(json.dumps(plan, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
