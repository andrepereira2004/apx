#!/usr/bin/env python3
"""Read-only source coverage and resource audit; never installs or changes APX."""
from __future__ import annotations

import argparse
import ast
from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
GIB = 1024 ** 3
# This is the existing runtime's policy, not a test-only lower threshold.
RESERVE_BYTES = 96 * GIB
TEST_WORKSPACE_BYTES = 32 * GIB
SOURCE_TREES = ("src/", "scripts/", "config/")


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def regular(path: Path) -> bool:
    return path.is_file() and not path.is_symlink()


def literal_assignments(path: Path) -> dict:
    """Read pinned inventories without importing/executing privileged adapters."""
    result = {}
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    try:
                        result[target.id] = ast.literal_eval(node.value)
                    except (ValueError, TypeError):
                        pass
    return result


def runtime_reserve(path: Path) -> int:
    def arithmetic(node):
        if isinstance(node, ast.Constant) and type(node.value) is int and node.value > 0:
            return node.value
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
            return arithmetic(node.left) * arithmetic(node.right)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
            base, exponent = arithmetic(node.left), arithmetic(node.right)
            if base > 1024 or exponent > 4:
                raise ValueError("unsupported reserve expression")
            return base ** exponent
        raise ValueError("unsupported reserve expression")
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and
                x.id == "HOST_STORAGE_RESERVE_BYTES" for x in node.targets):
            return arithmetic(node.value)
    raise ValueError("runtime reserve policy is missing")


def source_index(repo: Path) -> dict:
    names = subprocess.check_output(
        ["git", "-C", str(repo), "ls-files", "-z"], text=True,
    ).split("\0")
    index = defaultdict(list)
    for relative in names:
        if not relative.startswith(SOURCE_TREES):
            continue
        path = repo / relative
        if regular(path):
            index[path.name].append({"source": relative, "sha256": sha256(path)})
    return dict(index)


def compare_file(path: Path, index: dict) -> dict:
    digest = sha256(path)
    candidates = index.get(path.name, [])
    matches = [item["source"] for item in candidates if item["sha256"] == digest]
    return {
        "installed": str(path), "sha256": digest,
        "status": "identical" if matches else "differs" if candidates else "no-source-name-match",
        "matching_sources": matches, "candidates": candidates,
    }


def inventory_library(directory: Path, index: dict) -> list[dict]:
    if not directory.is_dir() or directory.is_symlink():
        return []
    # Deliberately exclude historical backups and all runtime state/credentials.
    return [compare_file(path, index) for path in sorted(directory.iterdir())
            if regular(path) and path.suffix in {".py", ".sh"}]


def seed_coverage(repo: Path, installed: Path, assets: dict) -> list[dict]:
    result = []
    for relative, expected in sorted(assets.items()):
        source = repo / "config/environment-shell-v1" / relative
        target = installed / relative
        source_hash = sha256(source) if regular(source) else None
        installed_hash = sha256(target) if regular(target) else None
        result.append({
            "asset": relative, "runtime_sha256": expected,
            "repository_sha256": source_hash, "installed_seed_sha256": installed_hash,
            "source_is_pinned": source_hash == expected,
            "seed_matches_source": source_hash is not None and installed_hash == source_hash,
        })
    return result


def storage_check(available: int, reserve: int = RESERVE_BYTES,
                  workspace: int = TEST_WORKSPACE_BYTES) -> dict:
    required = reserve + workspace
    return {"available_bytes": available, "protected_reserve_bytes": reserve,
            "planned_test_workspace_bytes": workspace, "required_available_bytes": required,
            "shortfall_bytes": max(0, required - available), "ready": available >= required}


def service_inventory(directory: Path, index: dict) -> list[dict]:
    result = []
    if not directory.is_dir():
        return result
    for path in sorted(directory.glob("apx*.service")):
        if not regular(path):
            continue
        # Record unit hash and executable paths only. Do NOT export unit bodies
        # or Environment/credential arguments; neither is a portable recipe.
        programs = []
        for line in path.read_text().splitlines():
            match = re.match(r"Exec(?:Start|StartPre|StartPost|Stop|StopPost)=\s*[-+!:@]*\s*(/[^\s]+)", line)
            if match:
                program = Path(match.group(1))
                item = {"path": str(program)}
                if regular(program) and program.suffix in {".py", ".sh"}:
                    item.update(compare_file(program, index))
                programs.append(item)
        result.append({"unit": path.name, "sha256": sha256(path), "executables": programs})
    return result


def audit(repo: Path = REPO, host: Path = Path("/")) -> dict:
    index = source_index(repo)
    runtime = literal_assignments(repo / "scripts/virtual-lab/apx-lab-runtime.py")
    reserve = runtime_reserve(repo / "scripts/virtual-lab/apx-lab-runtime.py")
    # Validate established policy without importing or executing the runtime.
    if reserve != RESERVE_BYTES:
        raise ValueError("runtime reserve policy changed; review the audit before use")
    pool = host / "var/lib/apx"
    storage = storage_check(shutil.disk_usage(pool if pool.exists() else host).free, reserve)
    library = inventory_library(host / "usr/lib/apx", index)
    canonical = inventory_library(host / "var/lib/apx/official-hub-v1", index)
    seeds = seed_coverage(repo, host / "usr/share/apx/config-seeds/environment-shell-v1",
                          runtime["ENVIRONMENT_SHELL_ASSETS"])
    active_path = host / "run/apx/active-graphical-environment-v1.json"
    active = None
    if regular(active_path) and active_path.stat().st_size <= 4096:
        record = json.loads(active_path.read_text())
        active = {key: record.get(key) for key in ("name", "role", "generation", "unit")}
    vm_core_verified = False
    evidence = repo / "audit/2026-10-18-portable-rebuild/vm"
    try:
        result = json.loads((evidence / "pc-result.json").read_text())
        source_manifest = json.loads((evidence / "source-manifest.json").read_text())
        vm_core_verified = result.get("state") == "passed" and len(result.get("checks", [])) >= 15 \
            and bool(source_manifest) and all(
                regular(repo / relative) and sha256(repo / relative) == expected
                for relative, expected in source_manifest.items())
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    blockers = []
    if not storage["ready"] and not vm_core_verified:
        blockers.append({"code": "test-storage", "detail":
                         "Teste creation/VM rehearsal must preserve the 96 GiB Host reserve and allow 32 GiB working space."})
    if not vm_core_verified and not regular(pool / "environments/teste/root/usr/bin/qemu-system-x86_64"):
        blockers.append({"code": "teste-qemu-not-provisioned", "detail":
                         "QEMU must be installed inside the newly created Teste Environment, not on the Host."})
    candidate = all(regular(repo / "scripts/portable" / name) for name in
                    ("install_apx_full.py", "apx-portable-graphical.py", "apx-portable-services.py"))
    blockers.extend([
        {"code": "graphical-port-not-accepted" if candidate else "graphical-port-not-implemented", "detail":
         "A local experimental graphical candidate exists; full portable parity is not established." if candidate else
         "The public installer covers the headless base only."},
        {"code": "physical-and-full-parity-unverified" if vm_core_verified else "full-vm-rehearsal-pending", "detail":
         "Automated VM core checks passed; human login, full update execution, personalization interaction and real hardware remain unverified." if vm_core_verified else
         "A clean Arch VM must pass graphical Hub boot, current QuickShell, authenticated lifecycle, isolation, recovery and a second boot."},
    ])
    return {
        "schema": 1, "profile": "apx-full-rebuild-readiness-v1",
        "source_commit": subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip(),
        "scope": "read-only source comparison; no credentials, personal data, installed root images or service bodies exported",
        "full_rebuild_verified": False, "automated_vm_core_verified": vm_core_verified,
        "active_environment": active, "test_storage": storage,
        "requested_test": {"name": "teste", "display_name": "Teste", "role": "graphical-base",
                           "desktop_preset": "intermediate", "vm": "fresh Arch Linux x86_64"},
        "library_summary": dict(Counter(item["status"] for item in library)),
        "library": library, "canonical_graphical_engine": canonical,
        "shell_seed_summary": {"assets": len(seeds),
                               "repository_pins_match": all(x["source_is_pinned"] for x in seeds),
                               "installed_seed_matches": all(x["seed_matches_source"] for x in seeds)},
        "shell_seed": seeds,
        "host_services": service_inventory(host / "etc/systemd/system", index),
        "blockers": blockers,
        "interpretation": [
            "Different hashes are review candidates, not proof that the installed version should replace repository code.",
            "Name matching cannot establish complete transitive dependency coverage.",
            "Pinned/source-identical files do not prove a working or hardware-independent installation.",
            "This is not an installer or backup and does not claim Teste or its VM exist.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new JSON report; existing files are never overwritten")
    args = parser.parse_args()
    report = audit()
    payload = json.dumps(report, indent=2) + "\n"
    if args.output:
        # Avoid overwrites and inherited public modes even under permissive umask.
        descriptor = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, "w") as stream:
            stream.write(payload)
        print(f"Report: {args.output}")
        print(json.dumps({"library": report["library_summary"], "shell_seed": report["shell_seed_summary"],
                          "test_storage": report["test_storage"], "blockers": report["blockers"]}, indent=2))
    else:
        print(payload, end="")
    return 2 if report["blockers"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"APX rebuild audit failed: {error}", file=sys.stderr)
        raise SystemExit(3)
