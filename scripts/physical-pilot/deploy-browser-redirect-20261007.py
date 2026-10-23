#!/usr/bin/env python3
"""Bounded deployment of Environment-local browser handoff on the active pilot."""
from pathlib import Path
import configparser
import datetime
import hashlib
import json
import os
import re
import shutil

REPO = Path(__file__).resolve().parents[2]
SEED = REPO / 'config/environment-shell-v1'
INSTALLED_SEED = Path('/usr/share/apx/config-seeds/environment-shell-v1')
ASSETS = ('local/bin/apx-browser-redirect-v1', 'local/share/applications/apx-browser-redirect.desktop',
          'local/bin/apx-settings', 'mako/config', 'mimeapps.list')
BACKUP = Path('/var/lib/apx/backups') / (datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-browser-redirect-feedback')
RULE = '\n[app-name="APX Browser"]' + (SEED / 'mako/config').read_text().split('[app-name="APX Browser"]', 1)[1]


def install(path, content, uid, gid, mode):
    if path.is_symlink():
        raise RuntimeError('Refusing symlink: ' + str(path))
    destination = BACKUP / str(path).lstrip('/')
    destination.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.copy2(path, destination)
    else:
        destination.with_suffix(destination.suffix + '.absent').touch()
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chown(path.parent, uid, gid)
    temporary = path.with_name(path.name + '.redirect-tmp')
    temporary.write_bytes(content)
    os.chmod(temporary, mode)
    os.chown(temporary, uid, gid)
    os.replace(temporary, path)


BACKUP.mkdir(mode=0o700)
for environment in ('hub', 'faculdade', 'hytale', 'minecraft', 'steam'):
    home = Path('/var/lib/apx/environments') / environment / 'home/apx'
    identity = home.stat()
    uid, gid = identity.st_uid, identity.st_gid
    settings = home / '.local/bin/apx-settings'
    text = settings.read_text()
    old_get = '["/usr/bin/xdg-settings", "get", "default-web-browser"]'
    old_set = '["/usr/bin/xdg-settings", "set",\n                                     "default-web-browser", selected]'
    if old_get not in text or old_set not in text:
        raise RuntimeError('Unrecognized Settings browser code: ' + environment)
    text = text.replace(old_get, '[str(HOME / ".local/bin/apx-browser-redirect-v1"), "get-browser"]').replace(
        old_set, '[str(HOME / ".local/bin/apx-browser-redirect-v1"),\n                                     "set-browser", selected]')
    install(settings, text.encode(), uid, gid, 0o755)
    for asset in ASSETS[:2]:
        install(home / ('.' + asset), (SEED / asset).read_bytes(), uid, gid, 0o755 if '/bin/' in asset else 0o600)
    mime = home / '.config/mimeapps.list'
    parser = configparser.ConfigParser(interpolation=None, strict=False)
    parser.read(mime)
    if not parser.has_section('Default Applications'):
        parser.add_section('Default Applications')
    defaults = parser['Default Applications']
    browser = defaults.get('x-scheme-handler/https', defaults.get('text/html', 'brave-browser.desktop')).split(';')[0]
    if browser == 'apx-browser-redirect.desktop':
        raise RuntimeError('Already installed; refusing to overwrite browser preference')
    install(home / '.config/apx/browser-redirect.json', json.dumps({'desktop': browser}).encode(), uid, gid, 0o600)
    # Preserve all unrelated MIME associations and their textual representation.
    original = mime.read_text() if mime.exists() else '[Default Applications]\n'
    for scheme in ('http', 'https'):
        key = 'x-scheme-handler/' + scheme
        original, count = re.subn('^' + re.escape(key) + '=.*$', key + '=apx-browser-redirect.desktop', original, flags=re.M)
        if not count:
            original = original.replace('[Default Applications]', '[Default Applications]\n' + key + '=apx-browser-redirect.desktop', 1)
    install(mime, original.encode(), uid, gid, 0o600)
    mako = home / '.config/mako/config'
    original = mako.read_text() if mako.exists() else ''
    if '[app-name="APX Browser"]' in original:
        raise RuntimeError('Unexpected existing notification rule')
    install(mako, (original + RULE).encode(), uid, gid, 0o600)

for asset in ASSETS:
    install(INSTALLED_SEED / asset, (SEED / asset).read_bytes(), 0, 0, 0o755 if '/bin/' in asset else 0o600)

for runtime in (REPO / 'scripts/virtual-lab/apx-lab-runtime.py', Path('/usr/lib/apx/apx-lab-runtime.py')):
    text = runtime.read_text()
    for asset in ASSETS:
        digest = hashlib.sha256((SEED / asset).read_bytes()).hexdigest()
        expression = r'("' + re.escape(asset) + r'": ")[a-f0-9]{64}("[,])'
        text, count = re.subn(expression, lambda match: match[1] + digest + match[2], text)
        if not count:
            anchor = 'ENVIRONMENT_SHELL_ASSETS = {'
            if anchor not in text:
                raise RuntimeError('Missing seed registry')
            text = text.replace(anchor, anchor + '\n    "' + asset + '": "' + digest + '",', 1)
    identity = runtime.stat()
    install(runtime, text.encode(), identity.st_uid, identity.st_gid, identity.st_mode & 0o777)
print(BACKUP)
