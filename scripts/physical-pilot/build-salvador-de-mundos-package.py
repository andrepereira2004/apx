#!/usr/bin/env python3
"""Package the owner's reviewed Linux adaptation for this APX pilot."""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import subprocess
import tempfile

NAME = "salvador-de-mundos-apx"
VERSION = "1.0-1"
SOURCE_SHA256 = "528c7984cb61fdbdc811360ba45599314885b47e93c18bcfd7c3705ff8115dfa"
PROGRAM_DIR = Path("usr/lib/apx/salvador-de-mundos")
DESKTOP = """[Desktop Entry]
Type=Application
Name=DreNinja Salvador de Mundos
Comment=Backups e recuperação de mundos Minecraft Bedrock e Java
Exec=/usr/bin/python3 /usr/lib/apx/salvador-de-mundos/app.py
Icon=salvador-de-mundos
StartupWMClass=salvador-de-mundos
Terminal=false
Categories=Game;Utility;
"""


def patch_app(source: str) -> str:
    changes = (
        ("    raise RuntimeError('Não foi encontrada a pasta de mundos do Bedrock instalado.')",
         "    return users / 'Shared/games/com.mojang/minecraftWorlds'"),
        ("        settings_path.write_text(json.dumps({\n            'worlds_root': str(discover_bedrock()),",
         "        world_root = discover_bedrock()\n"
         "        engine.default_backup_root().mkdir(parents=True, exist_ok=True)\n"
         "        settings_path.write_text(json.dumps({\n"
         "            'worlds_root': str(world_root),\n"
         "            'linux_bedrock_pending': str(world_root) if not world_root.is_dir() else None,"),
        ("    api = original.WorldSafeApi()\n    settings = api._settings()",
         "    api = original.WorldSafeApi()\n    refresh_bedrock(api)\n    settings = api._settings()"),
        ("def file_dialog(action, directory='', save_filename='', **kwargs):",
         """def refresh_bedrock(api):
    settings = api._settings()
    if settings.get('linux_bedrock_pending') != str(api.worlds_root):
        return
    root = discover_bedrock()
    if not root.is_dir():
        return
    settings['worlds_root'] = str(root)
    del settings['linux_bedrock_pending']
    api._save_settings(settings)
    api.worlds_root = root


def file_dialog(action, directory='', save_filename='', **kwargs):"""),
        ("                for world_id, world in api._world_entries():",
         "                refresh_bedrock(api)\n                for world_id, world in api._world_entries():"),
        ("                with LOCK:\n                    value = getattr(api, method)(*args)",
         "                with LOCK:\n                    refresh_bedrock(api)\n"
         "                    value = getattr(api, method)(*args)"),
    )
    for old, new in changes:
        if source.count(old) != 1:
            raise ValueError("the reviewed Linux adapter has changed")
        source = source.replace(old, new, 1)
    compile(source, "app.py", "exec")
    return source


def build(source: Path, output: Path) -> None:
    relatives = {"app.py", "dialog.py", "dist/index.html"}
    relatives.update(path.relative_to(source).as_posix() for path in
                     (source / "dist/assets").iterdir())
    for package in ("backend", "nbtlib", "send2trash"):
        relatives.update(path.relative_to(source).as_posix() for path in
                         (source / package).rglob("*.pyc"))
    payload = {}
    digest = hashlib.sha256()
    for relative in sorted(relatives):
        path = source / relative
        if (not path.resolve().is_relative_to(source) or
                not stat.S_ISREG(path.lstat().st_mode)):
            raise ValueError(f"unexpected application entry: {relative}")
        data = path.read_bytes()
        digest.update(relative.encode() + b"\0" + hashlib.sha256(data).digest())
        payload[relative] = data
    if digest.hexdigest() != SOURCE_SHA256:
        raise ValueError("application files differ from the reviewed Linux adaptation")

    archive = output / f"{NAME}-{VERSION}-x86_64.pkg.tar.zst"
    manifest = output / f"{NAME}-v1.json"
    if archive.exists() or manifest.exists():
        raise FileExistsError("package output already exists")
    with tempfile.TemporaryDirectory(dir=output) as temp:
        stage = Path(temp) / "payload"
        program = stage / PROGRAM_DIR
        for relative, data in payload.items():
            path = program / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            if relative == "app.py":
                data = patch_app(data.decode()).encode()
            path.write_bytes(data)
        icon = stage / "usr/share/icons/hicolor/256x256/apps/salvador-de-mundos.png"
        icon.parent.mkdir(parents=True)
        icon.write_bytes(payload["dist/assets/dreninja-logo-Ct-Q74Dz.png"])
        desktop = stage / "usr/share/applications/salvador-de-mundos.desktop"
        desktop.parent.mkdir(parents=True)
        desktop.write_text(DESKTOP)
        size = sum(path.stat().st_size for path in stage.rglob("*") if path.is_file())
        (stage / ".PKGINFO").write_text(
            f"pkgname = {NAME}\npkgver = {VERSION}\n"
            "pkgdesc = DreNinja Salvador de Mundos (adaptacao local APX)\n"
            f"size = {size}\narch = x86_64\n"
            "depend = python>=3.14\ndepend = python<3.15\n"
            "depend = brave-bin\ndepend = gtk3\ndepend = python-gobject\ndepend = libnotify\ndepend = python-numpy\n"
        )
        for path in stage.rglob("*"):
            path.chmod(0o755 if path.is_dir() else 0o644)
        candidate = Path(temp) / archive.name
        subprocess.run(["bsdtar", "--zstd", "--uid", "0", "--gid", "0",
                        "-cf", str(candidate), "-C", str(stage), ".PKGINFO", "usr"],
                       check=True)
        record = {
            "schema": 1,
            "package": NAME,
            "filename": archive.name,
            "sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
            "source_sha256": SOURCE_SHA256,
        }
        candidate.rename(archive)
        manifest.write_text(json.dumps(record, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    build(args.source.resolve(strict=True), args.output.resolve(strict=True))
