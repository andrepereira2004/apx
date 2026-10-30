#!/usr/bin/env python3
"""Install reversible UI CSS into one explicitly selected Thunderbird profile.

No account settings or mail files are read or copied. Existing CSS remains intact.
Close Thunderbird before applying; restart after rollback as well.
"""
from pathlib import Path
import argparse
import datetime
import json
import os
import shutil

REPO = Path(__file__).resolve().parents[2]
BEGIN = '/* APX Graphite begin */'
END = '/* APX Graphite end */'
PREF = 'user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profile', type=Path)
    parser.add_argument('--rollback', type=Path)
    args = parser.parse_args()
    profile = args.profile.resolve(strict=True)
    assert profile.is_dir()
    if args.rollback:
        manifest = json.loads((args.rollback / 'inventory.json').read_text())
        assert manifest['profile'] == str(profile)
        for item in manifest['files']:
            dest = profile / item['relative']
            if item['existed']:
                shutil.copyfile(args.rollback / item['relative'], dest)
                os.chmod(dest, item['mode'])
                os.chown(dest, item['uid'], item['gid'])
            else:
                dest.unlink(missing_ok=True)
        print('Restored appearance files; restart Thunderbird.')
        return
    chrome = profile / 'chrome'
    assert not chrome.is_symlink()
    paths = [profile / 'user.js', chrome / 'userChrome.css', chrome / 'apx-graphite.css',
             chrome / 'userContent.css', chrome / 'apx-compose-content.css']
    for path in paths:
        assert not path.is_symlink(), path
    old_prefs = paths[0].read_text() if paths[0].exists() else ''
    old_css = paths[1].read_text() if paths[1].exists() else ''
    source = (REPO / 'config/thunderbird-graphite-v1/graphite.css').read_text()
    old_content = paths[3].read_text() if paths[3].exists() else ''
    compose_source = (REPO / 'config/thunderbird-graphite-v1/compose-content.css').read_text()
    # @import must precede other style rules; keep all previous user CSS below it.
    css_block = BEGIN + '\n@import url("apx-graphite.css");\n' + END + '\n'
    pref_block = BEGIN + '\n' + PREF + '\n' + END + '\n'

    def strip_block(text):
        if BEGIN not in text:
            return text
        assert text.count(BEGIN) == 1 and text.count(END) == 1
        start = text.index(BEGIN)
        end = text.index(END, start) + len(END)
        if text[end:end + 1] == '\n':
            end += 1
        return text[:start] + text[end:]

    prefs = strip_block(old_prefs)
    planned = [prefs + ('' if not prefs or prefs.endswith('\n') else '\n') + pref_block,
               css_block + strip_block(old_css), source,
               BEGIN + '\n@import url("apx-compose-content.css");\n' + END + '\n'
               + strip_block(old_content), compose_source]
    changed = [(p, data) for p, data in zip(paths, planned)
               if not p.exists() or p.read_text() != data]
    if not changed:
        print('Appearance already matches; no changes.')
        return
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    backup = profile / ('apx-appearance-backup-' + stamp)
    backup.mkdir(mode=0o700)
    owner = profile.stat()
    os.chown(backup, owner.st_uid, owner.st_gid)
    inventory = []
    for path, data in changed:
        relative = str(path.relative_to(profile))
        existed = path.exists()
        info = path.stat() if existed else owner
        if existed:
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, saved)
        inventory.append(dict(relative=relative, existed=existed,
                              mode=info.st_mode & 0o777, uid=info.st_uid, gid=info.st_gid))
    (backup / 'inventory.json').write_text(json.dumps(dict(profile=str(profile), files=inventory), indent=2) + '\n')
    chrome.mkdir(exist_ok=True)
    os.chown(chrome, owner.st_uid, owner.st_gid)
    for path, data in changed:
        temp = path.with_name(path.name + '.apx-tmp')
        assert not temp.exists() and not temp.is_symlink()
        temp.write_text(data)
        info = path.stat() if path.exists() else owner
        os.chmod(temp, info.st_mode & 0o777 if path.exists() else 0o600)
        os.chown(temp, info.st_uid, info.st_gid)
        os.replace(temp, path)
    print(backup)


if __name__ == '__main__':
    main()
