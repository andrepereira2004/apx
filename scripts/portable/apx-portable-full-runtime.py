#!/usr/bin/env python3
"""Current lifecycle with a fresh, generic graphical seed and optional artifacts."""
import importlib.util
import json
import os
from pathlib import Path
import sys

directory = Path(__file__).resolve().parent
sys.path.insert(0, str(directory))
spec = importlib.util.spec_from_file_location("apx_full_runtime_core", directory / "apx-lab-runtime-core.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
runtime.ROLES = {"hub", "development", "minimal", "graphical-base"}
runtime.RELEASE_IDS["hub"] = "portable-hub-graphical-v1"
original_create = runtime.create


def configure_features(root, plan):
    from apx_environment_features import validate_selection, packages_for
    preset, modules = validate_selection(plan["desktop_preset"], plan["desktop_modules"])
    folder = root / "etc/apx"
    folder.mkdir(parents=True, exist_ok=True)
    runtime.atomic_json(folder / "environment-features.json",
                        {"schema": 1, "preset": preset, "modules": list(modules)}, 0o644)
    source = runtime.read_trusted_shadow(runtime.ENVIRONMENTS / "hub/root")
    password = next((line.split(":")[1] for line in source.splitlines() if line.startswith("apx:")), None)
    if not password or password.startswith(("!", "*")):
        raise runtime.Refusal("enroll the new installation's APX identity before creating workloads")
    lines = runtime.read_trusted_shadow(root).splitlines()
    found = False
    for index, line in enumerate(lines):
        if line.startswith("apx:"):
            fields = line.split(":"); fields[1] = password
            lines[index] = ":".join(fields); found = True
    if not found: raise runtime.Refusal("release APX account is missing")
    runtime.write_trusted_shadow(root, "\n".join(lines) + "\n")
    packages = tuple(sorted(set(packages_for(modules)) | ({"thunar"} if "files" in modules else set())))
    if packages:
        runtime.run(["pacman", "--root", str(root), "--dbpath", str(root / "var/lib/pacman"),
                     "--config", str(root / "etc/pacman.conf"), "--cachedir", "/var/cache/pacman/pkg",
                     "--disable-sandbox", "-Syu", "--needed", "--noconfirm", *packages])
    # Proprietary applications, biometric identity and pilot GPU artifacts are
    # deliberately not cloned from the live machine. The open-source graphics
    # stack belongs to the fresh release; NVIDIA is admitted during installation.
    runtime.atomic_json(folder / "portable-application-policy.json", {
        "schema": 1, "profile": "fresh-apx-without-personal-applications",
        "third_party_artifacts_copied": False, "biometric_identity_copied": False,
    }, 0o644)


def create(plan_identity, approval):
    plan = runtime.load_plan(plan_identity, "create")
    # A Hub has the same independent shell seed as other graphical roots.
    # Keep all writes within the existing create journal before publication by
    # completing its home immediately afterwards while the Hub remains stopped.
    original_create(plan_identity, approval)
    if plan["role"] == "hub":
        home = runtime.ENVIRONMENTS / "hub/home/apx"
        runtime.copy_environment_shell_seed(runtime.ENVIRONMENT_SHELL_SEED, home)


runtime.configure_environment_features = configure_features
runtime.create = create
if __name__ == "__main__":
    try:
        raise SystemExit(runtime.main())
    except (runtime.Refusal, runtime.subprocess.CalledProcessError) as error:
        print(f"APX refused: {error}", file=sys.stderr)
        raise SystemExit(2)
else:
    globals().update({key: value for key, value in vars(runtime).items() if not key.startswith("__")})
