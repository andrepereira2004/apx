#!/usr/bin/env python3
"""Read fixed APX package/config metadata; never launch apps or read user content."""
import configparser
import json
from pathlib import Path

PACKAGES = ('thunar', 'brave-bin', 'thunderbird', 'zapzap', 'flatpak', 'electron',
            'gtk3', 'gtk4', 'qt5-base', 'qt6-base', 'xdg-desktop-portal',
            'xdg-desktop-portal-gtk', 'xdg-desktop-portal-hyprland')
CONFIGS = ('xdg-desktop-portal/portals.conf', 'gtk-3.0/settings.ini',
           'gtk-4.0/settings.ini')


def inventory(base):
    rows = []
    for env in sorted(base.iterdir()):
        if not (env / 'registration.json').is_file():
            continue
        packages = {}
        database = env / 'root/var/lib/pacman/local'
        if database.is_dir():
            for entry in sorted(database.iterdir()):
                desc = entry / 'desc'
                if not desc.is_file():
                    continue
                fields = desc.read_text().splitlines()
                def field(key):
                    marker = '%' + key + '%'
                    return fields[fields.index(marker) + 1] if marker in fields else None
                name = field('NAME')
                if name in PACKAGES or (name and name.startswith('electron')):
                    packages[name] = field('VERSION')
        configs = {}
        for relative in CONFIGS:
            path = env / 'home/apx/.config' / relative
            if path.is_file():
                parser = configparser.ConfigParser(interpolation=None, strict=False)
                parser.read(path)
                configs[relative] = {section: dict(parser[section]) for section in parser.sections()}
        flatpaks = []
        for location in (env / 'root/var/lib/flatpak/app', env / 'home/apx/.local/share/flatpak/app'):
            if location.is_dir():
                flatpaks.extend(p.name for p in location.iterdir() if p.is_dir())
        launcher = env / 'home/apx/.local/bin/apx-desktop-activation-v1'
        text = launcher.read_text() if launcher.is_file() else ''
        rows.append(dict(environment=env.name, packages=packages, configs=configs,
                         flatpak_app_ids=sorted(set(flatpaks)),
                         directory_default_unconditionally_reset='files.set_as_default_for_type' in text and
                         "Gio.AppInfo.get_default_for_type('inode/directory'" not in text,
                         behavioral_validation='not tested'))
    return dict(scope='read-only on-disk metadata; no live behavior or app content', environments=rows)


if __name__ == '__main__':
    print(json.dumps(inventory(Path('/var/lib/apx/environments')), indent=2))
